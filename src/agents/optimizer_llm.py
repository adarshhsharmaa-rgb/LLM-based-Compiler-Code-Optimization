"""LLM-based optimizer agents (Google Gemini, Groq, or a local Ollama model).

The LLM is only a *proposer*: everything it returns goes through exactly the
same Verifier and CostEvaluator gates as rule-based proposals, so a wrong LLM
answer can never be accepted.

Providers:
  * ``gemini``    -- Gemini via the ``google-genai`` SDK. Credentials:
    ``GEMINI_API_KEY`` (or ``GOOGLE_API_KEY``), free from aistudio.google.com.
  * ``groq``      -- an open model hosted by Groq, via its OpenAI-compatible
    HTTP API. Credentials: ``GROQ_API_KEY``, free from console.groq.com.
  * ``ollama``    -- a model running on this machine, served by Ollama
    (ollama.com). No key and no internet, so this is the offline backend.
    Server address: ``OLLAMA_HOST`` (default 127.0.0.1:11434).
  * ``auto``      -- accepted by ``create_llm_optimizer`` only: the first cloud
    provider that is configured (Gemini, then Groq) when online, otherwise Ollama.

If credentials are missing, the local server is not running, or the API fails
with a non-retryable error, the optimizer marks itself unavailable and the
orchestrator carries on with rule-based optimization only.
"""
from __future__ import annotations

import json
import os
import re
import socket
import time
import urllib.error
import urllib.request

from ..tac.program import TACParseError, TACProgram

DEFAULT_PROVIDER = "gemini"
DEFAULT_MODELS = {
    "gemini": "gemini-3.1-flash-lite",
    "groq": "openai/gpt-oss-120b",
    "ollama": "qwen2.5-coder:7b",
}
DEFAULT_MODEL = DEFAULT_MODELS[DEFAULT_PROVIDER]
CLOUD_HOSTS = {"gemini": "generativelanguage.googleapis.com", "groq": "api.groq.com"}
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
OLLAMA_DEFAULT_HOST = "http://127.0.0.1:11434"

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
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)   # local reasoning models
_GPU_CRASH_RE = re.compile(r"llama-server process has terminated|llama runner process has terminated|CUDA",
                           re.IGNORECASE)


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
    selected_because = ""      # set by create_llm_optimizer: why this backend was picked
    _min_interval = 0.0        # seconds to leave between API calls (cloud rate limits)
    _last_call = 0.0

    def __init__(self, model: str):
        self._model = model
        self.available = True
        self.unavailable_reason = ""

    def _throttle(self) -> None:
        wait = self._min_interval - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    @property
    def model(self) -> str:
        return self._model

    @property
    def label(self) -> str:
        """Short name for logs, e.g. ``ollama qwen2.5-coder:7b``."""
        return f"{self.provider} {self._model}"

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


# ====================================================================== #
class GroqOptimizer(BaseLLMOptimizer):
    """An open model hosted by Groq (free tier; key from console.groq.com).

    Uses Groq's OpenAI-compatible chat API with the standard library only, so
    there is no SDK to install. Credentials: ``GROQ_API_KEY``.

    Free-tier limits are per model: about 30 requests and 8,000 tokens a
    minute, 1,000 requests and 200,000 tokens a day when this was written
    (October 2026; the Limits page of the Groq console has the exact numbers).
    Calls are spaced ``min_interval`` seconds apart to stay under the
    per-minute token limit. A per-minute 429 is waited out for as long as Groq
    says and retried twice; a per-day 429 means the quota is spent and the
    optimizer switches off. 5xx errors are retried three times; if they
    persist only that proposal is skipped.

    The default models reason before answering, and those hidden tokens count
    against the daily quota, so reasoning effort is kept low
    (``GROQ_REASONING_EFFORT`` changes it: low, medium or high).
    """

    provider = "groq"
    MAX_RATE_LIMIT_RETRIES = 2
    MAX_OVERLOAD_RETRIES = 3
    MAX_RETRY_AFTER = 90.0     # a longer wait than this is the daily quota, not the per-minute one
    # Groq's front door rejects the standard library's default User-Agent with a bare 403.
    USER_AGENT = "tac-optimization-agent/1.0"

    def __init__(self, model: str = DEFAULT_MODELS["groq"], min_interval: float = 5.0,
                 retry_wait: float = 20.0, base_url: str = GROQ_BASE_URL, timeout: float = 90.0,
                 max_tokens: int = 4000):
        super().__init__(model)
        self._min_interval = min_interval
        self._retry_wait = retry_wait
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._timeout = timeout
        self._max_tokens = max_tokens
        self._effort = os.environ.get("GROQ_REASONING_EFFORT", "low")
        self._send_reasoning_options = True
        self.api_calls = 0
        self._key = os.environ.get("GROQ_API_KEY", "").strip()
        if not self._key:
            self._disable("no Groq API key - set GROQ_API_KEY or put the key in a .groq_key file")

    def _reasoning_options(self) -> dict:
        if not self._send_reasoning_options:
            return {}
        if "gpt-oss" in self._model:
            return {"reasoning_effort": self._effort, "include_reasoning": False}
        if "qwen" in self._model:
            return {"reasoning_effort": self._effort, "reasoning_format": "hidden"}
        return {}

    def _post(self, prompt: str) -> dict:
        body = {"model": self._model, "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2, "max_completion_tokens": self._max_tokens, **self._reasoning_options()}
        request = urllib.request.Request(
            self._url, data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self._key}",
                     "User-Agent": self.USER_AGENT})
        with urllib.request.urlopen(request, timeout=self._timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    @staticmethod
    def _error(exc: urllib.error.HTTPError) -> tuple[str, str]:
        """(message, code) from an error reply; both '' if the body is not Groq's JSON."""
        try:
            error = json.loads(exc.read().decode("utf-8")).get("error") or {}
            return str(error.get("message", ""))[:200], str(error.get("code", ""))
        except (OSError, ValueError, AttributeError):
            return "", ""

    def _retry_after(self, exc: urllib.error.HTTPError, attempt: int) -> float:
        try:
            return float(exc.headers.get("retry-after"))
        except (TypeError, ValueError):
            return self._retry_wait * attempt

    def _complete(self, prompt: str) -> str:
        rate_limited = overloaded = 0
        while True:
            self._throttle()
            self.api_calls += 1
            try:
                reply = self._post(prompt)
                break
            except urllib.error.HTTPError as exc:
                message, code = self._error(exc)
                if exc.code == 429:
                    rate_limited += 1
                    wait = self._retry_after(exc, rate_limited)
                    if "per day" in message or wait > self.MAX_RETRY_AFTER:
                        raise _LLMUnavailable(f"Groq daily quota used up (429): {message}") from exc
                    if rate_limited <= self.MAX_RATE_LIMIT_RETRIES:
                        time.sleep(wait)
                        continue
                    raise _LLMSkip("Groq still rate-limited (429) after "
                                   f"{self.MAX_RATE_LIMIT_RETRIES} retries") from exc
                if exc.code >= 500 or exc.code == 498:
                    overloaded += 1
                    if overloaded <= self.MAX_OVERLOAD_RETRIES:
                        time.sleep(self._retry_wait / 3 * 2 ** (overloaded - 1))
                        continue
                    raise _LLMSkip(f"Groq API error {exc.code} (still failing after "
                                   f"{self.MAX_OVERLOAD_RETRIES} retries)") from exc
                if exc.code in (401, 403):
                    raise _LLMUnavailable(f"Groq rejected the API key ({exc.code})") from exc
                if exc.code == 404 or code in ("model_not_found", "model_decommissioned"):
                    raise _LLMUnavailable(f"Groq model {self._model!r} is not available: {message}") from exc
                if exc.code == 400 and "reasoning" in message and self._send_reasoning_options:
                    self._send_reasoning_options = False    # this model takes no reasoning options
                    continue
                raise _LLMSkip(f"Groq API error {exc.code}: {message}") from exc
            except (OSError, ValueError) as exc:  # network failures, timeouts, unreadable replies
                raise _LLMSkip(f"Groq request failed: {type(exc).__name__}") from exc
        choice = (reply.get("choices") or [{}])[0]
        if choice.get("finish_reason") == "length":
            raise _LLMSkip("Groq reply was truncated (max_completion_tokens)")
        text = _THINK_RE.sub("", (choice.get("message") or {}).get("content") or "")
        if not text.strip():
            raise _LLMSkip("Groq returned no text")
        return text


# ====================================================================== #
def ollama_host(host: str | None = None) -> str:
    """Base URL of the Ollama server: the argument, else ``$OLLAMA_HOST``, else the local default."""
    host = (host or os.environ.get("OLLAMA_HOST") or OLLAMA_DEFAULT_HOST).strip().rstrip("/")
    if "://" not in host:
        host = "http://" + host + ("" if ":" in host else ":11434")
    # OLLAMA_HOST is often the server's bind address; 0.0.0.0 is not one a client can connect to.
    return host.replace("//0.0.0.0", "//127.0.0.1")


def _open_local(url: str, data: bytes | None, timeout: float):
    """Open a URL on the Ollama server, never through a system HTTP proxy."""
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    return urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=timeout)


def ollama_running(host: str | None = None, timeout: float = 1.0) -> bool:
    """Quick check that an Ollama server answers (used before offering offline mode)."""
    try:
        with _open_local(ollama_host(host) + "/api/version", None, timeout):
            return True
    except (OSError, ValueError):
        return False


class _OllamaError(Exception):
    """An HTTP error reply from the Ollama server."""

    def __init__(self, status: int, message: str):
        super().__init__(f"{status}: {message}")
        self.status = status
        self.message = message


class OllamaOptimizer(BaseLLMOptimizer):
    """A model served on this machine by Ollama -- the offline backend.

    Needs no API key, no internet and no extra Python package: it talks to the
    Ollama server's HTTP API with the standard library. Set up once with
    ``ollama pull qwen2.5-coder:7b``. Any chat model works: pass ``--llm-model``
    or set ``OLLAMA_MODEL``. If the default model is not pulled but another one
    is, that one is used.

    A reply can take a while on a laptop, so the read timeout is generous
    (``OLLAMA_TIMEOUT`` seconds, default 300) and a timed-out call only skips
    that proposal. If the server cannot be reached, the optimizer switches off.

    If Ollama's GPU runner crashes while loading the model (an NVIDIA driver too
    old for its CUDA build does this), the call is repeated on the CPU and the
    rest of the run stays there. ``OLLAMA_NUM_GPU=0`` forces the CPU from the start.
    """

    provider = "ollama"

    def __init__(self, model: str | None = None, host: str | None = None, timeout: float | None = None,
                 connect_timeout: float = 3.0, max_tokens: int = 2000):
        requested = model or os.environ.get("OLLAMA_MODEL")
        super().__init__(requested or DEFAULT_MODELS["ollama"])
        self._host = ollama_host(host)
        self._timeout = timeout if timeout is not None else float(os.environ.get("OLLAMA_TIMEOUT", 300))
        self._max_tokens = max_tokens
        self.api_calls = 0
        num_gpu = os.environ.get("OLLAMA_NUM_GPU", "")
        self._num_gpu = int(num_gpu) if num_gpu.lstrip("-").isdigit() else None   # None: Ollama decides
        self.cpu_fallback = False     # True once a GPU crash made this run switch to the CPU
        try:
            pulled = self.pulled_models(connect_timeout)
        except (OSError, ValueError):
            self._disable(f"no Ollama server at {self._host} - install it from ollama.com, "
                          "then run 'ollama serve'")
            return
        self._select_model(pulled, explicit=bool(requested))

    def _request(self, path: str, body: dict | None, timeout: float) -> dict:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        with _open_local(self._host + path, data, timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def pulled_models(self, timeout: float = 3.0) -> list[str]:
        """Names of the models on the server. Raises OSError if it cannot be reached."""
        return [m.get("name", "") for m in self._request("/api/tags", None, timeout).get("models") or []]

    def _select_model(self, pulled: list[str], explicit: bool) -> None:
        wanted = self._model
        if wanted in pulled or f"{wanted}:latest" in pulled:
            return
        usable = [name for name in pulled if "embed" not in name]   # embedding models cannot chat
        if not usable:
            self._disable(f"Ollama has no model yet - run 'ollama pull {wanted}'")
        elif explicit:
            self._disable(f"Ollama model {wanted!r} is not pulled - run 'ollama pull {wanted}' "
                          f"(pulled: {', '.join(usable[:5])})")
        else:
            # The default is not pulled: use what is there, preferring a code model.
            self._model = next((name for name in usable if "code" in name), usable[0])

    def _chat(self, prompt: str) -> dict:
        options = {"temperature": 0.2, "num_predict": self._max_tokens, "num_ctx": 4096}
        if self._num_gpu is not None:
            options["num_gpu"] = self._num_gpu       # layers on the GPU; 0 means CPU only
        body = {"model": self._model, "stream": False, "options": options,
                "messages": [{"role": "user", "content": prompt}]}
        try:
            return self._request("/api/chat", body, self._timeout)
        except urllib.error.HTTPError as exc:
            raise _OllamaError(exc.code, self._error_text(exc)) from exc

    def _complete(self, prompt: str) -> str:
        self.api_calls += 1
        try:
            try:
                reply = self._chat(prompt)
            except _OllamaError as exc:
                if exc.status != 500 or self._num_gpu == 0 or not _GPU_CRASH_RE.search(exc.message):
                    raise
                # The GPU runner died (typically an NVIDIA driver too old for Ollama's CUDA
                # build). The model still runs on the CPU, only slower, so carry on there.
                self._num_gpu = 0
                self.cpu_fallback = True
                reply = self._chat(prompt)
        except _OllamaError as exc:
            if exc.status == 404:
                raise _LLMUnavailable(f"Ollama model {self._model!r} is not pulled - "
                                      f"run 'ollama pull {self._model}'") from exc
            raise _LLMSkip(f"Ollama error {exc.status}: {exc.message}") from exc
        except OSError as exc:
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, TimeoutError):
                raise _LLMSkip(f"Ollama gave no reply within {self._timeout:.0f}s") from exc
            raise _LLMUnavailable(f"lost the Ollama server at {self._host} ({reason})") from exc
        except ValueError as exc:
            raise _LLMSkip("Ollama sent an unreadable reply") from exc
        if reply.get("done_reason") == "length":
            raise _LLMSkip("Ollama reply was truncated (num_predict)")
        text = _THINK_RE.sub("", (reply.get("message") or {}).get("content") or "")
        if not text.strip():
            raise _LLMSkip("Ollama returned no text")
        return text

    @staticmethod
    def _error_text(exc: urllib.error.HTTPError) -> str:
        try:
            return str(json.loads(exc.read().decode("utf-8")).get("error", ""))[:150]
        except (OSError, ValueError, AttributeError):
            return ""


PROVIDERS = {"gemini": GeminiOptimizer, "groq": GroqOptimizer, "ollama": OllamaOptimizer}


AUTO_CLOUD_ORDER = ("gemini", "groq")     # tried in this order by provider="auto"
KEY_FILES = {"GEMINI_API_KEY": ".gemini_key", "GROQ_API_KEY": ".groq_key"}


def load_key_files(root: str) -> None:
    """Load API keys from the git-ignored key files in ``root`` for variables that are not set."""
    for env_var, filename in KEY_FILES.items():
        path = os.path.join(root, filename)
        if os.environ.get(env_var) or not os.path.exists(path):
            continue
        if env_var == "GEMINI_API_KEY" and os.environ.get("GOOGLE_API_KEY"):
            continue      # the Gemini SDK already has a key
        with open(path, encoding="utf-8") as fh:
            key = fh.read().strip()
        if key:
            os.environ[env_var] = key


def is_online(timeout: float = 2.0) -> bool:
    """True if the default cloud provider's API host accepts a connection."""
    try:
        with socket.create_connection((CLOUD_HOSTS[DEFAULT_PROVIDER], 443), timeout=timeout):
            return True
    except OSError:
        return False


def create_llm_optimizer(provider: str = DEFAULT_PROVIDER, model: str | None = None,
                         offline: bool = False) -> BaseLLMOptimizer:
    """Build the LLM backend.

    ``offline=True`` always gives the local Ollama model. ``provider="auto"``
    gives the first cloud provider that is configured (Gemini, then Groq) when
    the internet is up, and falls back to Ollama otherwise.
    """
    kwargs = {"model": model} if model else {}
    why = ""
    if offline:
        provider, why = "ollama", "offline mode"
    elif provider == "auto":
        if is_online():
            passed_over = []
            for name in AUTO_CLOUD_ORDER:
                cloud = PROVIDERS[name](**kwargs)
                if cloud.available:
                    cloud.selected_because = "online" + (
                        f", {' and '.join(passed_over)} not available" if passed_over else "")
                    return cloud
                passed_over.append(name)
            why = f"{' and '.join(passed_over)} not available"
        else:
            why = "no internet connection"
        provider = "ollama"
    if provider not in PROVIDERS:
        raise ValueError(f"unknown LLM provider {provider!r}; choose from {sorted(PROVIDERS)}")
    optimizer = PROVIDERS[provider](**kwargs)
    optimizer.selected_because = why
    return optimizer
