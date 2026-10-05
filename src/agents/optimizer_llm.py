"""LLM-based optimizer agents (Anthropic Claude or Google Gemini).

The LLM is only a *proposer*: everything it returns goes through exactly the
same Verifier and CostEvaluator gates as rule-based proposals, so a wrong LLM
answer can never be accepted.

Providers:
  * ``anthropic`` -- Claude via the ``anthropic`` SDK. Credentials:
    ``ANTHROPIC_API_KEY`` or an ``ant auth login`` profile.
  * ``gemini``    -- Gemini via the ``google-genai`` SDK. Credentials:
    ``GEMINI_API_KEY`` (or ``GOOGLE_API_KEY``), free from aistudio.google.com.

If credentials are missing, or the API fails with a non-retryable error, the
optimizer marks itself unavailable and the orchestrator carries on with
rule-based optimization only.
"""
from __future__ import annotations

import re
import time

from ..tac.program import TACParseError, TACProgram

DEFAULT_PROVIDER = "anthropic"
DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "gemini": "gemini-3.1-flash-lite",
}
DEFAULT_MODEL = DEFAULT_MODELS[DEFAULT_PROVIDER]

PROMPT_TEMPLATE = """You are a compiler optimization expert. Given this Three-Address Code (TAC), propose exactly ONE semantics-preserving optimization.

Original TAC:
{tac_string}

Rules:
1. The optimized code MUST produce identical output for ALL possible inputs.
2. Apply exactly one optimization: constant folding, dead code elimination, common subexpression elimination, algebraic simplification, strength reduction, or copy propagation.
3. Return ONLY the modified TAC inside <tac> tags, nothing else outside the tags.
4. Explain your optimization in one line inside <reasoning> tags.

TAC syntax (one instruction per line, keep exactly this syntax):
  x = y            x = a op b   (op: + - * / % << == != < > <= >= && ||)
  x = -a           x = !a       L0:      goto L0
  if a goto L0     ifFalse a goto L0     print a
Variables that are read before being written are program inputs. Integer
division truncates toward zero; dividing by zero is a runtime error.

Format:
<reasoning>your explanation</reasoning>
<tac>
modified TAC here
</tac>"""

_REASONING_RE = re.compile(r"<reasoning>(.*?)</reasoning>", re.DOTALL | re.IGNORECASE)
_TAC_RE = re.compile(r"<tac>(.*?)</tac>", re.DOTALL | re.IGNORECASE)
_LINE_NO_RE = re.compile(r"^\s*\d+\s*[|:.)]\s+")


def parse_llm_tac(text: str) -> TACProgram | None:
    """Robustly turn the body of a <tac> block into a TACProgram (None on failure)."""
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("```"):
            continue
        line = _LINE_NO_RE.sub("", line)   # strip "3 | " / "3: " listing prefixes
        lines.append(line)
    if not lines:
        return None
    try:
        return TACProgram.from_string("\n".join(lines))
    except TACParseError:
        return None


class _LLMUnavailable(Exception):
    """Raised by a provider when it should be switched off for the rest of the run."""


class _LLMSkip(Exception):
    """Raised by a provider when this one proposal failed but later ones may work."""


class BaseLLMOptimizer:
    provider = "base"

    def __init__(self, model: str):
        self._model = model
        self.available = True
        self.unavailable_reason = ""

    def _disable(self, reason: str) -> None:
        self.available = False
        self.unavailable_reason = reason

    def _build_prompt(self, program: TACProgram) -> str:
        return PROMPT_TEMPLATE.format(tac_string=program.to_string())

    def _complete(self, prompt: str) -> str:
        """Return the model's text reply. Raise _LLMSkip or _LLMUnavailable on failure."""
        raise NotImplementedError

    def propose(self, program: TACProgram) -> tuple[TACProgram | None, str]:
        """Returns (proposed_program, reasoning). Returns (None, error_msg) on failure."""
        if not self.available:
            return None, f"LLM unavailable: {self.unavailable_reason}"
        try:
            text = self._complete(self._build_prompt(program))
        except _LLMUnavailable as exc:
            self._disable(str(exc))
            return None, f"LLM unavailable: {self.unavailable_reason}"
        except _LLMSkip as exc:
            return None, str(exc)
        return self._parse_text(text, program)

    @staticmethod
    def _parse_text(text: str, original: TACProgram) -> tuple[TACProgram | None, str]:
        reasoning_match = _REASONING_RE.search(text)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "(no reasoning given)"
        tac_match = _TAC_RE.search(text)
        if not tac_match:
            return None, f"no <tac> block in LLM response; reasoning: {reasoning}"
        candidate = parse_llm_tac(tac_match.group(1))
        if candidate is None:
            return None, f"could not parse LLM TAC; reasoning: {reasoning}"
        if candidate == original:
            return None, f"LLM returned unchanged TAC; reasoning: {reasoning}"
        return candidate, reasoning


# ====================================================================== #
class LLMOptimizer(BaseLLMOptimizer):
    """Claude via the Anthropic API."""

    provider = "anthropic"

    def __init__(self, model: str = DEFAULT_MODELS["anthropic"], max_tokens: int = 2000):
        super().__init__(model)
        self._max_tokens = max_tokens
        try:
            import anthropic
            self._anthropic = anthropic
            self._client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var / ant profile
        except Exception as exc:  # pragma: no cover - depends on local environment
            self._client = None
            self._disable(f"could not create Anthropic client: {exc}")

    def _complete(self, prompt: str) -> str:
        anthropic = self._anthropic
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
        except (anthropic.AuthenticationError, anthropic.PermissionDeniedError) as exc:
            raise _LLMUnavailable(f"authentication failed ({exc.status_code})") from exc
        except anthropic.NotFoundError as exc:
            raise _LLMUnavailable(f"model {self._model!r} not found") from exc
        except anthropic.RateLimitError as exc:
            raise _LLMSkip("LLM rate-limited (429); skipping this proposal") from exc
        except anthropic.APIStatusError as exc:
            raise _LLMSkip(f"LLM API error {exc.status_code}") from exc
        except anthropic.APIConnectionError as exc:
            raise _LLMSkip("LLM connection error") from exc
        except Exception as exc:  # missing credentials surface as a non-API error
            raise _LLMUnavailable(f"{type(exc).__name__}: {exc}") from exc
        if response.stop_reason == "refusal":
            raise _LLMSkip("LLM declined the request")
        if response.stop_reason == "max_tokens":
            raise _LLMSkip("LLM response was truncated (max_tokens)")
        return "".join(block.text for block in response.content if block.type == "text")


# ====================================================================== #
class GeminiOptimizer(BaseLLMOptimizer):
    """Gemini via the Google Gen AI SDK (works with a free AI Studio key).

    The free tier allows only a few requests per minute, so calls are spaced
    ``min_interval`` seconds apart. Rate-limit errors (429) are retried twice
    with growing pauses; if they persist the quota is used up and the
    optimizer switches off. "High demand" errors (500/503) are retried three
    times; if they persist only that proposal is skipped.
    """

    provider = "gemini"
    MAX_RATE_LIMIT_RETRIES = 2
    MAX_OVERLOAD_RETRIES = 3

    def __init__(self, model: str = DEFAULT_MODELS["gemini"], min_interval: float = 6.5,
                 retry_wait: float = 30.0):
        super().__init__(model)
        self._min_interval = min_interval
        self._retry_wait = retry_wait
        self._last_call = 0.0
        self.api_calls = 0
        self._config = None
        try:
            from google import genai
            from google.genai import errors, types
            self._errors = errors
            # Plain text generation: turn off automatic function calling (also silences its log line).
            self._config = types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
            self._client = genai.Client()  # uses GEMINI_API_KEY / GOOGLE_API_KEY env var
        except ImportError:
            self._client = None
            self._disable("google-genai is not installed (pip install google-genai)")
        except Exception as exc:
            self._client = None
            self._disable(f"could not create Gemini client - set GEMINI_API_KEY ({exc})")

    def _throttle(self) -> None:
        wait = self._min_interval - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def _complete(self, prompt: str) -> str:
        errors = self._errors
        rate_limited = overloaded = 0
        while True:
            self._throttle()
            self.api_calls += 1
            try:
                response = self._client.models.generate_content(
                    model=self._model, contents=prompt, config=self._config)
                break
            except errors.APIError as exc:
                message = str(exc.message or "")
                if exc.code == 429:
                    rate_limited += 1
                    if rate_limited <= self.MAX_RATE_LIMIT_RETRIES:
                        time.sleep(self._retry_wait * rate_limited)
                        continue
                    raise _LLMUnavailable(f"Gemini quota exhausted (429): {message[:200]}") from exc
                if exc.code in (500, 503):
                    overloaded += 1
                    if overloaded <= self.MAX_OVERLOAD_RETRIES:
                        time.sleep(self._retry_wait / 3 * 2 ** (overloaded - 1))
                        continue
                    raise _LLMSkip(f"Gemini API error {exc.code} (still overloaded after "
                                   f"{self.MAX_OVERLOAD_RETRIES} retries)") from exc
                if exc.code in (400, 401, 403) and "API key" in message:
                    raise _LLMUnavailable(f"Gemini rejected the API key ({exc.code})") from exc
                if exc.code == 404:
                    raise _LLMUnavailable(f"Gemini model {self._model!r} not found: {message[:150]}") from exc
                if exc.code in (401, 403):
                    raise _LLMUnavailable(f"Gemini permission denied ({exc.code})") from exc
                raise _LLMSkip(f"Gemini API error {exc.code}") from exc
            except Exception as exc:  # network failures etc.
                raise _LLMSkip(f"Gemini request failed: {type(exc).__name__}") from exc
        text = response.text
        if not text:
            reason = ""
            if response.candidates:
                reason = str(response.candidates[0].finish_reason)
            raise _LLMSkip(f"Gemini returned no text ({reason or 'blocked or empty'})")
        return text


PROVIDERS = {"anthropic": LLMOptimizer, "gemini": GeminiOptimizer}


def create_llm_optimizer(provider: str = DEFAULT_PROVIDER, model: str | None = None) -> BaseLLMOptimizer:
    if provider not in PROVIDERS:
        raise ValueError(f"unknown LLM provider {provider!r}; choose from {sorted(PROVIDERS)}")
    return PROVIDERS[provider](model=model or DEFAULT_MODELS[provider])
