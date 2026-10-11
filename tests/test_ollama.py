"""Tests for the offline LLM backend (Ollama), against a stand-in local server."""
import json
import os
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from src.agents import optimizer_llm
from src.agents.optimizer_llm import (
    GeminiOptimizer,
    OllamaOptimizer,
    create_llm_optimizer,
    ollama_host,
    ollama_running,
)
from src.agents.orchestrator import Orchestrator
from src.tac.program import TACProgram

ROOT = os.path.join(os.path.dirname(__file__), "..")
GOOD_REPLY = "<reasoning>fold 3 + 5</reasoning>\n<tac>\nt0 = 8\nprint t0\n</tac>"


def chat(text, done_reason="stop", delay=0.0):
    """One scripted /api/chat reply: (status, JSON body, seconds to wait first)."""
    return 200, {"message": {"role": "assistant", "content": text}, "done": True,
                 "done_reason": done_reason}, delay


class _QuietServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):    # a client that gave up is not worth a traceback
        pass


class _FakeOllama:
    """Answers /api/tags, /api/version and /api/chat like an Ollama server would."""

    def __init__(self, models, replies):
        self.models = list(models)
        self.replies = list(replies)
        self.requests = []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _send(self, status, payload):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path == "/api/tags":
                    self._send(200, {"models": [{"name": name} for name in fake.models]})
                else:
                    self._send(200, {"version": "0.0.0"})

            def do_POST(self):
                fake.requests.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
                status, payload, delay = fake.replies.pop(0)
                time.sleep(delay)
                self._send(status, payload)

        self.server = _QuietServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, args=(0.02,), daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def ollama():
    started = []

    def start(replies=(), models=("qwen2.5-coder:7b",)):
        started.append(_FakeOllama(models, replies))
        return started[-1]

    yield start
    for server in started:
        server.close()


@pytest.fixture
def no_server():
    """Address of a local port with nothing listening on it."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"http://127.0.0.1:{port}"


def P(text):
    return TACProgram.from_string(text)


# ------------------------------------------------------------------ proposals
def test_ollama_proposal_is_parsed(ollama):
    server = ollama([chat(GOOD_REPLY)])
    opt = OllamaOptimizer(host=server.url)
    assert opt.available and opt.label == "ollama qwen2.5-coder:7b"
    cand, reason = opt.propose(P("t0 = 3 + 5\nprint t0"))
    assert cand.to_string() == "t0 = 8\nprint t0" and reason == "fold 3 + 5"
    request = server.requests[0]
    assert request["model"] == "qwen2.5-coder:7b" and request["stream"] is False
    assert "t0 = 3 + 5" in request["messages"][0]["content"]
    assert opt.api_calls == 1


def test_ollama_reasoning_model_think_block_is_ignored(ollama):
    reply = "<think>maybe <tac>print 1</tac> ... no</think>\n" + GOOD_REPLY
    opt = OllamaOptimizer(host=ollama([chat(reply)]).url)
    cand, reason = opt.propose(P("t0 = 3 + 5\nprint t0"))
    assert cand.to_string() == "t0 = 8\nprint t0" and reason == "fold 3 + 5"


def test_ollama_unchanged_or_garbled_reply_is_no_proposal(ollama):
    server = ollama([chat("<reasoning>none</reasoning><tac>t0 = 3 + 5\nprint t0</tac>"), chat("I cannot help")])
    opt = OllamaOptimizer(host=server.url)
    prog = P("t0 = 3 + 5\nprint t0")
    assert opt.propose(prog)[0] is None
    cand, reason = opt.propose(prog)
    assert cand is None and "no <tac> block" in reason and opt.available


# ------------------------------------------------------------------ availability and models
def test_ollama_without_a_server_is_unavailable(no_server):
    opt = OllamaOptimizer(host=no_server)
    assert not opt.available and "ollama serve" in opt.unavailable_reason
    cand, reason = opt.propose(P("print 1"))
    assert cand is None and "LLM unavailable" in reason
    assert not ollama_running(no_server)


def test_ollama_running_detects_the_server(ollama):
    assert ollama_running(ollama().url)


def test_ollama_with_no_model_says_how_to_get_one(ollama):
    opt = OllamaOptimizer(host=ollama(models=()).url)
    assert not opt.available and "ollama pull qwen2.5-coder:7b" in opt.unavailable_reason


def test_ollama_uses_a_pulled_model_when_the_default_is_missing(ollama):
    server = ollama(models=("nomic-embed-text:latest", "llama3.2:latest", "deepseek-coder:6.7b"))
    opt = OllamaOptimizer(host=server.url)
    assert opt.available and opt.model == "deepseek-coder:6.7b"      # a code model is preferred
    only_embed = OllamaOptimizer(host=ollama(models=("nomic-embed-text:latest",)).url)
    assert not only_embed.available


def test_ollama_explicit_model_must_be_pulled(ollama, monkeypatch):
    server = ollama(models=("llama3.2:latest",))
    missing = OllamaOptimizer(model="phi4", host=server.url)
    assert not missing.available and "ollama pull phi4" in missing.unavailable_reason
    assert OllamaOptimizer(model="llama3.2", host=server.url).available       # ":latest" is implied
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:latest")
    assert OllamaOptimizer(host=server.url).model == "llama3.2:latest"


def test_ollama_host_normalisation(monkeypatch):
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    assert ollama_host() == "http://127.0.0.1:11434"
    assert ollama_host("localhost") == "http://localhost:11434"
    assert ollama_host("0.0.0.0:11434") == "http://127.0.0.1:11434"
    assert ollama_host("http://box:1234/") == "http://box:1234"
    monkeypatch.setenv("OLLAMA_HOST", "192.168.1.5:8000")
    assert ollama_host() == "http://192.168.1.5:8000"


# ------------------------------------------------------------------ failures during a run
def test_ollama_model_missing_at_call_time_switches_off(ollama):
    server = ollama([(404, {"error": "model 'qwen2.5-coder:7b' not found"}, 0)])
    opt = OllamaOptimizer(host=server.url)
    cand, reason = opt.propose(P("t0 = 3 + 5\nprint t0"))
    assert cand is None and not opt.available and "ollama pull" in reason


def test_ollama_server_error_skips_one_proposal(ollama):
    server = ollama([(500, {"error": "model requires more system memory"}, 0), chat(GOOD_REPLY)])
    opt = OllamaOptimizer(host=server.url)
    prog = P("t0 = 3 + 5\nprint t0")
    cand, reason = opt.propose(prog)
    assert cand is None and opt.available and "more system memory" in reason
    assert opt.propose(prog)[0].to_string() == "t0 = 8\nprint t0"


def test_ollama_truncated_reply_is_skipped(ollama):
    opt = OllamaOptimizer(host=ollama([chat("<reasoning>fold</reasoning><tac>t0 = 8", "length")]).url)
    cand, reason = opt.propose(P("t0 = 3 + 5\nprint t0"))
    assert cand is None and "truncated" in reason and opt.available


def test_ollama_slow_reply_times_out_without_switching_off(ollama):
    opt = OllamaOptimizer(host=ollama([chat(GOOD_REPLY, delay=1.5)]).url, timeout=0.3)
    cand, reason = opt.propose(P("t0 = 3 + 5\nprint t0"))
    assert cand is None and "no reply within" in reason and opt.available


def test_ollama_server_going_away_switches_off(ollama):
    server = ollama()
    opt = OllamaOptimizer(host=server.url)
    server.close()
    cand, reason = opt.propose(P("t0 = 3 + 5\nprint t0"))
    assert cand is None and not opt.available and "lost the Ollama server" in reason


# ------------------------------------------------------------------ choosing the backend
def test_offline_mode_selects_ollama(ollama, monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", ollama().url)
    monkeypatch.setattr(optimizer_llm, "is_online", lambda: pytest.fail("offline mode must not probe the network"))
    opt = create_llm_optimizer("gemini", offline=True)
    assert isinstance(opt, OllamaOptimizer) and opt.available and opt.selected_because == "offline mode"


def test_auto_provider_uses_ollama_without_internet(ollama, monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", ollama().url)
    monkeypatch.setattr(optimizer_llm, "is_online", lambda: False)
    opt = create_llm_optimizer("auto")
    assert isinstance(opt, OllamaOptimizer) and opt.selected_because == "no internet connection"


def test_auto_provider_uses_ollama_when_the_cloud_llm_is_not_configured(ollama, monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", ollama().url)
    monkeypatch.setattr(optimizer_llm, "is_online", lambda: True)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    opt = create_llm_optimizer("auto")
    assert isinstance(opt, OllamaOptimizer) and opt.available
    assert opt.selected_because.startswith("gemini is unavailable")


def test_auto_provider_prefers_the_cloud_llm_when_online(monkeypatch):
    monkeypatch.setattr(optimizer_llm, "is_online", lambda: True)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    opt = create_llm_optimizer("auto")
    assert isinstance(opt, GeminiOptimizer) and opt.selected_because == "online"


def test_named_provider_is_used_as_is_and_unknown_ones_are_rejected(ollama, monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", ollama(models=("llama3.2:latest",)).url)
    opt = create_llm_optimizer("ollama", "llama3.2")
    assert isinstance(opt, OllamaOptimizer) and opt.model == "llama3.2" and opt.selected_because == ""
    with pytest.raises(ValueError, match="unknown LLM provider"):
        create_llm_optimizer("copilot")


# ------------------------------------------------------------------ end to end
def test_offline_orchestrator_accepts_a_correct_local_proposal(ollama, monkeypatch):
    server = ollama([chat("<reasoning>multiply by 2 is a shift</reasoning><tac>t0 = x << 1\nprint t0</tac>"),
                     chat("<reasoning>nothing left</reasoning><tac>t0 = x << 1\nprint t0</tac>")])
    monkeypatch.setenv("OLLAMA_HOST", server.url)
    result = Orchestrator(optimizer_mode="hybrid", offline=True).optimize(P("t0 = x * 2\nprint t0"))
    assert result.optimized_tac.to_string() == "t0 = x << 1\nprint t0" and result.output_match
    assert (result.llm_provider, result.llm_model) == ("ollama", "qwen2.5-coder:7b")
    assert result.llm_calls == 2 and result.llm_proposals == 1 and result.llm_valid == 1
    assert "[ROUTE]   LLM optimizer (ollama qwen2.5-coder:7b): the rule-based proposal was turned down" \
        in result.log.format_log()


def test_offline_orchestrator_rejects_a_wrong_local_proposal(ollama, monkeypatch):
    server = ollama([chat("<reasoning>x is probably 1</reasoning><tac>print 2</tac>")] * 2)
    monkeypatch.setenv("OLLAMA_HOST", server.url)
    prog = P("t0 = x * 2\nprint t0")
    result = Orchestrator(optimizer_mode="llm", offline=True, max_llm_calls=2).optimize(prog)
    assert result.optimized_tac == prog and result.output_match       # never accepted
    assert result.llm_proposals == 2 and result.llm_valid == 0 and result.invalid_count == 2


def test_cli_offline_without_ollama_still_optimizes_with_the_rules(no_server, tmp_path):
    env = {**os.environ, "OLLAMA_HOST": no_server}
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "main.py"), "--offline", "--output-dir", str(tmp_path),
         "--run-file", os.path.join(ROOT, "dataset", "programs", "arithmetic", "arithmetic_001.src")],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT, env=env, timeout=120)
    assert proc.returncode == 0, proc.stdout[-800:] + proc.stderr[-400:]
    assert "Optimizer routing: hybrid" in proc.stdout and "offline mode" in proc.stdout
    assert "LLM optimizer unavailable (no Ollama server" in proc.stdout
    assert "Output match:  PASS" in proc.stdout and "[ACCEPT]" in proc.stdout
