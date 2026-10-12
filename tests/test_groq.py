"""Tests for the Groq LLM backend, against a stand-in OpenAI-compatible server."""
import json
import os
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from src.agents import optimizer_llm
from src.agents.optimizer_llm import (
    GroqOptimizer,
    OllamaOptimizer,
    create_llm_optimizer,
    load_key_files,
)
from src.agents.orchestrator import Orchestrator
from src.tac.program import TACProgram

GOOD_REPLY = "<reasoning>fold 3 + 5</reasoning>\n<tac>\nt0 = 8\nprint t0\n</tac>"
PER_MINUTE = "Rate limit reached for model `openai/gpt-oss-120b` on tokens per minute (TPM): Limit 8000"
PER_DAY = "Rate limit reached for model `openai/gpt-oss-120b` on tokens per day (TPD): Limit 200000"


def ok(text, finish_reason="stop"):
    return 200, {"choices": [{"message": {"role": "assistant", "content": text},
                              "finish_reason": finish_reason}]}, {}


def err(status, message, code="", retry_after=None):
    headers = {} if retry_after is None else {"retry-after": str(retry_after)}
    return status, {"error": {"message": message, "type": "invalid_request_error", "code": code}}, headers


class _FakeGroq:
    """Answers POST /chat/completions with scripted replies and records what it was sent."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.bodies = []
        self.headers = []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                fake.bodies.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
                fake.headers.append(dict(self.headers))
                status, payload, extra = fake.replies.pop(0)
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                for name, value in extra.items():
                    self.send_header(name, value)
                self.end_headers()
                self.wfile.write(body)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/openai/v1"
        threading.Thread(target=self.server.serve_forever, args=(0.02,), daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def groq(monkeypatch):
    """groq(replies, **options) -> (optimizer, server), with a key set and no waiting."""
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key")
    monkeypatch.delenv("GROQ_REASONING_EFFORT", raising=False)
    monkeypatch.delenv("GROQ_FALLBACK_MODELS", raising=False)
    started = []

    def start(replies=(), **options):
        server = _FakeGroq(replies)
        started.append(server)
        options.setdefault("fallback_models", ())        # no fallback unless a test asks for one
        return GroqOptimizer(base_url=server.url, min_interval=0, retry_wait=0, **options), server

    yield start
    for server in started:
        server.close()


def P(text):
    return TACProgram.from_string(text)


PROG = "t0 = 3 + 5\nprint t0"


# ------------------------------------------------------------------ proposals
def test_groq_proposal_is_parsed(groq):
    opt, server = groq([ok(GOOD_REPLY)])
    assert opt.available and opt.label == "groq openai/gpt-oss-120b"
    cand, reason = opt.propose(P(PROG))
    assert cand.to_string() == "t0 = 8\nprint t0" and reason == "fold 3 + 5"
    body = server.bodies[0]
    assert body["model"] == "openai/gpt-oss-120b" and "t0 = 3 + 5" in body["messages"][0]["content"]
    assert opt.api_calls == 1


def test_groq_request_carries_the_key_and_its_own_user_agent(groq):
    opt, server = groq([ok(GOOD_REPLY)])
    opt.propose(P(PROG))
    headers = {k.lower(): v for k, v in server.headers[0].items()}
    assert headers["authorization"] == "Bearer gsk_test_key"
    # Groq answers the standard library's default "Python-urllib" agent with a bare 403.
    assert "urllib" not in headers["user-agent"].lower()


def test_groq_reasoning_options_depend_on_the_model(groq, monkeypatch):
    opt, server = groq([ok(GOOD_REPLY)])
    opt.propose(P(PROG))
    assert server.bodies[0]["reasoning_effort"] == "low" and server.bodies[0]["include_reasoning"] is False
    qwen, server = groq([ok(GOOD_REPLY)], model="qwen/qwen3.8-27b")
    qwen.propose(P(PROG))
    assert server.bodies[0]["reasoning_format"] == "hidden" and "include_reasoning" not in server.bodies[0]
    plain, server = groq([ok(GOOD_REPLY)], model="some/other-model")
    plain.propose(P(PROG))
    assert "reasoning_effort" not in server.bodies[0]
    monkeypatch.setenv("GROQ_REASONING_EFFORT", "medium")
    medium, server = groq([ok(GOOD_REPLY)])
    medium.propose(P(PROG))
    assert server.bodies[0]["reasoning_effort"] == "medium"


def test_groq_model_that_rejects_reasoning_options_is_retried_without_them(groq):
    opt, server = groq([err(400, "`reasoning_effort` is not supported with this model"),
                        ok(GOOD_REPLY), ok(GOOD_REPLY)])
    assert opt.propose(P(PROG))[0].to_string() == "t0 = 8\nprint t0"
    assert "reasoning_effort" in server.bodies[0] and "reasoning_effort" not in server.bodies[1]
    opt.propose(P(PROG))
    assert "reasoning_effort" not in server.bodies[2]              # remembered for later calls


def test_groq_think_block_is_ignored(groq):
    opt, _ = groq([ok("<think>maybe <tac>print 1</tac></think>" + GOOD_REPLY)])
    assert opt.propose(P(PROG))[0].to_string() == "t0 = 8\nprint t0"


# ------------------------------------------------------------------ availability
def test_groq_without_a_key_is_unavailable(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    opt = GroqOptimizer()
    assert not opt.available and "GROQ_API_KEY" in opt.unavailable_reason
    assert opt.propose(P("print 1"))[0] is None


def test_groq_rejected_key_switches_off(groq):
    opt, _ = groq([err(401, "Invalid API Key", "invalid_api_key")])
    cand, reason = opt.propose(P(PROG))
    assert cand is None and not opt.available and "API key (401)" in reason


def test_groq_unknown_model_switches_off(groq):
    opt, _ = groq([err(404, "The model `nope` does not exist", "model_not_found")], model="nope")
    cand, reason = opt.propose(P(PROG))
    assert cand is None and not opt.available and "not available" in reason


def test_groq_decommissioned_model_switches_off(groq):
    opt, _ = groq([err(400, "The model has been decommissioned", "model_decommissioned")])
    assert opt.propose(P(PROG))[0] is None and not opt.available


# ------------------------------------------------------------------ rate limits and errors
def test_groq_per_minute_limit_is_waited_out_and_retried(groq):
    opt, server = groq([err(429, PER_MINUTE, "rate_limit_exceeded", retry_after=0), ok(GOOD_REPLY)])
    assert opt.propose(P(PROG))[0].to_string() == "t0 = 8\nprint t0"
    assert len(server.bodies) == 2 and opt.available


def test_groq_persistent_per_minute_limit_skips_one_proposal(groq):
    opt, server = groq([err(429, PER_MINUTE, retry_after=0)] * 3)      # first try + 2 retries
    cand, reason = opt.propose(P(PROG))
    assert cand is None and opt.available and "still rate-limited" in reason
    assert len(server.bodies) == 3


def test_groq_daily_quota_switches_off_at_once(groq):
    opt, server = groq([err(429, PER_DAY, "rate_limit_exceeded", retry_after=5)])
    cand, reason = opt.propose(P(PROG))
    assert cand is None and not opt.available and "daily quota" in reason
    assert len(server.bodies) == 1


def test_groq_daily_quota_moves_on_to_the_next_model(groq):
    # Each model has its own daily quota, so a spent one is replaced, not the end of the run.
    opt, server = groq([err(429, PER_DAY, retry_after=5), ok(GOOD_REPLY), ok(GOOD_REPLY)],
                       fallback_models=("openai/gpt-oss-20b", "qwen/qwen3.8-27b"))
    assert opt.propose(P(PROG))[0].to_string() == "t0 = 8\nprint t0"      # same proposal, next model
    assert opt.available and opt.model == "openai/gpt-oss-20b" and opt.label == "groq openai/gpt-oss-20b"
    assert opt.model_switches == [("openai/gpt-oss-120b", "openai/gpt-oss-20b", 1)]
    assert [b["model"] for b in server.bodies] == ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
    opt.propose(P(PROG))
    assert server.bodies[2]["model"] == "openai/gpt-oss-20b"               # and it stays there


def test_groq_switches_off_when_every_model_is_spent(groq):
    opt, server = groq([err(429, PER_DAY, retry_after=5)] * 2, fallback_models=("openai/gpt-oss-20b",))
    cand, reason = opt.propose(P(PROG))
    assert cand is None and not opt.available and "daily quota" in reason
    assert len(server.bodies) == 2 and len(opt.model_switches) == 1


def test_groq_unavailable_model_moves_on_to_the_next_one(groq):
    opt, _ = groq([err(404, "The model `nope` does not exist", "model_not_found"), ok(GOOD_REPLY)],
                  model="nope", fallback_models=("openai/gpt-oss-20b",))
    assert opt.propose(P(PROG))[0] is not None and opt.model == "openai/gpt-oss-20b"


def test_groq_fallback_models_default_and_environment(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key")
    monkeypatch.delenv("GROQ_FALLBACK_MODELS", raising=False)
    assert GroqOptimizer()._fallback_models == ["openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
    assert GroqOptimizer(model="openai/gpt-oss-20b")._fallback_models == ["qwen/qwen3.8-27b"]
    monkeypatch.setenv("GROQ_FALLBACK_MODELS", "a/one, b/two")
    assert GroqOptimizer()._fallback_models == ["a/one", "b/two"]
    monkeypatch.setenv("GROQ_FALLBACK_MODELS", "")
    assert GroqOptimizer()._fallback_models == []


def test_groq_long_retry_after_counts_as_the_daily_quota(groq):
    opt, _ = groq([err(429, "Rate limit reached", retry_after=3600)])
    assert opt.propose(P(PROG))[0] is None and not opt.available


def test_groq_server_errors_are_retried_then_skipped(groq):
    opt, server = groq([err(503, "Service Unavailable")] * 4)          # first try + 3 retries
    cand, reason = opt.propose(P(PROG))
    assert cand is None and opt.available and "503" in reason
    assert len(server.bodies) == 4
    recovering, _ = groq([err(502, "Bad Gateway"), ok(GOOD_REPLY)])
    assert recovering.propose(P(PROG))[0].to_string() == "t0 = 8\nprint t0"


def test_groq_other_errors_skip_with_the_message(groq):
    opt, _ = groq([err(413, "Request too large for model")])
    cand, reason = opt.propose(P(PROG))
    assert cand is None and opt.available and "413" in reason and "too large" in reason


def test_groq_truncated_or_empty_reply_is_skipped(groq):
    opt, _ = groq([ok("<reasoning>fold</reasoning><tac>t0 = 8", "length"), ok("")])
    assert "truncated" in opt.propose(P(PROG))[1]
    assert "no text" in opt.propose(P(PROG))[1] and opt.available


def test_groq_network_failure_skips_without_switching_off(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        closed = f"http://127.0.0.1:{sock.getsockname()[1]}/openai/v1"
    opt = GroqOptimizer(base_url=closed, min_interval=0, retry_wait=0)
    cand, reason = opt.propose(P(PROG))
    assert cand is None and opt.available and "request failed" in reason


# ------------------------------------------------------------------ choosing the backend
def test_auto_provider_uses_groq_when_gemini_has_no_key(monkeypatch):
    monkeypatch.setattr(optimizer_llm, "is_online", lambda: True)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key")
    opt = create_llm_optimizer("auto")
    assert isinstance(opt, GroqOptimizer) and opt.available
    assert opt.selected_because == "online, gemini not available"


def test_auto_provider_falls_back_to_ollama_when_no_cloud_key_is_set(monkeypatch):
    monkeypatch.setattr(optimizer_llm, "is_online", lambda: True)
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        monkeypatch.setenv("OLLAMA_HOST", f"127.0.0.1:{sock.getsockname()[1]}")
    opt = create_llm_optimizer("auto")
    assert isinstance(opt, OllamaOptimizer) and opt.selected_because == "gemini and groq not available"


def test_named_groq_provider_and_model(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key")
    opt = create_llm_optimizer("groq", "openai/gpt-oss-20b")
    assert isinstance(opt, GroqOptimizer) and opt.model == "openai/gpt-oss-20b" and opt.selected_because == ""


def test_key_files_fill_in_unset_variables_only(tmp_path, monkeypatch):
    (tmp_path / ".groq_key").write_text("gsk_from_file\n", encoding="utf-8")
    (tmp_path / ".gemini_key").write_text("gemini_from_file\n", encoding="utf-8")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "already-set")
    load_key_files(str(tmp_path))
    assert os.environ["GROQ_API_KEY"] == "gsk_from_file"
    assert "GEMINI_API_KEY" not in os.environ                  # the Gemini SDK already has a key
    monkeypatch.setenv("GROQ_API_KEY", "from-environment")
    load_key_files(str(tmp_path))
    assert os.environ["GROQ_API_KEY"] == "from-environment"    # a set variable is never overwritten
    load_key_files(str(tmp_path / "missing"))                   # no files: nothing happens


# ------------------------------------------------------------------ in the agent loop
def test_orchestrator_with_groq_accepts_right_and_rejects_wrong_proposals(groq):
    opt, _ = groq([ok("<reasoning>x is probably 1</reasoning><tac>print 2</tac>"),
                   ok("<reasoning>multiply by 2 is a shift</reasoning><tac>t0 = x << 1\nprint t0</tac>"),
                   ok("<reasoning>nothing left</reasoning><tac>t0 = x << 1\nprint t0</tac>")])
    orch = Orchestrator()
    orch.llm_optimizer = opt
    result = orch.optimize(P("t0 = x * 2\nprint t0"))
    assert result.optimized_tac.to_string() == "t0 = x << 1\nprint t0" and result.output_match
    assert (result.llm_provider, result.llm_model) == ("groq", "openai/gpt-oss-120b")
    assert result.llm_proposals == 2 and result.llm_valid == 1 and result.invalid_count == 1
    assert "[ROUTE]   LLM optimizer (groq openai/gpt-oss-120b)" in result.log.format_log()
