"""Tests for the terminal front end (demo.py)."""
import builtins
import glob
import os
import subprocess
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

import demo  # noqa: E402
from src.agents.orchestrator import Orchestrator  # noqa: E402
from src.tac.program import TACProgram  # noqa: E402


def run_demo(*args, stdin=None):
    return subprocess.run([sys.executable, os.path.join(ROOT, "demo.py"), *args, "--fast", "--no-color"],
                          capture_output=True, text=True, encoding="utf-8", input=stdin, cwd=ROOT, timeout=120)


@pytest.mark.parametrize("path", sorted(glob.glob(os.path.join(ROOT, "demo_programs", "*.c"))))
def test_every_sample_runs_through_all_six_stages(path):
    proc = run_demo(path, "--inputs", "n=5,marks=35")
    assert proc.returncode == 0, proc.stdout[-800:] + proc.stderr[-400:]
    for n in range(1, 7):
        assert f"STAGE {n}" in proc.stdout
    assert "Suggestions made by the agent" in proc.stdout
    assert "identical output" in proc.stdout and "PASS" in proc.stdout


def test_summary_reports_rule_llm_and_total_rows():
    out = run_demo(os.path.join(ROOT, "demo_programs", "1_constants.c")).stdout
    rows = {line.split()[0]: line.split() for line in out.splitlines()
            if line.strip().startswith(("Rule-based", "Total"))}
    rule, total = rows["Rule-based"], rows["Total"]
    assert rule[1:] == total[1:]                      # no LLM in this run: totals equal the rules
    suggested, verified, accepted, no_gain, invalid = map(int, total[1:])
    assert suggested == verified + invalid and verified == accepted + no_gain
    assert accepted > 0
    assert "LLM: not used" in out


def test_unsupported_c_shows_a_clear_error_and_exit_code():
    proc = run_demo(stdin='#include <stdio.h>\nint main() {\n  int a[3];\n  return 0;\n}\n')
    assert proc.returncode == 1
    assert "C error at line 3: arrays are not supported" in proc.stdout
    assert "STAGE 2" not in proc.stdout


def test_program_that_runs_too_long_stops_with_a_message():
    src = ('#include <stdio.h>\nint main() {\n  int t = 0;\n'
           '  for (int i = 0; i < 1000000; i++) { t += 2 + 3; }\n  printf("%d", t);\n  return 0;\n}\n')
    proc = run_demo(stdin=src)
    assert proc.returncode == 1
    assert "does not finish within 100,000 steps" in proc.stdout
    assert "STAGE 4" not in proc.stdout


def test_missing_file_is_reported():
    proc = run_demo("no_such_file.c")
    assert proc.returncode == 1 and "Cannot read" in proc.stdout


def test_count_outcomes():
    proposals = [{"outcome": "accepted"}, {"outcome": "accepted"}, {"outcome": "rejected"}, {"outcome": "invalid"}]
    assert demo.count_outcomes(proposals) == {"suggested": 4, "verified": 3, "accepted": 2,
                                              "no_gain": 1, "invalid": 1}
    assert demo.count_outcomes([])["suggested"] == 0


def test_summary_with_llm_counts(capsys):
    class ScriptedLLM:
        available, unavailable_reason = True, ""

        def __init__(self):
            self.replies = [(None, "garbled"), ("t0 = x << 1\nprint t0", "use a shift"), ("print 2", "wrong")]

        def propose(self, program):
            text, reason = self.replies.pop(0)
            return (TACProgram.from_string(text) if text else None), reason

    orch = Orchestrator(max_llm_calls=5)
    orch.llm_optimizer = ScriptedLLM()
    result = orch.optimize(TACProgram.from_string("t0 = x * 2\nprint t0"))
    demo.Style.enabled = False
    demo.suggestion_summary(result, llm_enabled=True, llm_note="", hidden=0)
    out = capsys.readouterr().out
    rows = {line.split("  ")[1].strip(): line.split() for line in out.splitlines()
            if line.strip().startswith(("Rule-based", "LLM", "Total"))}
    assert rows["Rule-based"][-5:] == ["1", "1", "0", "1", "0"]
    assert rows["LLM"][-5:] == ["2", "1", "1", "0", "1"]     # a scripted LLM has no provider name
    assert rows["Total"][-5:] == ["3", "2", "1", "1", "1"]
    assert "LLM requests sent: 3  (2 usable suggestions, 1 unusable reply)" in out


def test_menu_selects_a_sample_by_number(monkeypatch):
    answers = iter(["99", "1"])                       # an invalid choice is asked again
    monkeypatch.setattr(builtins, "input", lambda *_: next(answers))
    source, name = demo.choose_program()
    assert name == "1_constants.c" and "int main" in source


def test_menu_quit(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "q")
    assert demo.choose_program() is None


def test_menu_picks_a_real_program(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "r")
    source, name = demo.choose_program()
    assert demo.is_real_program(name) and "main" in source
    assert not demo.is_real_program("3_loop.c")


def _options(**changes):
    values = {"llm_provider": "auto", "offline": False, "cost_model": "static", "strict": False,
              "max_iterations": 200, "llm_model": None}
    values.update(changes)
    return demo.argparse.Namespace(**values)


def test_setup_menu_chooses_the_proposer_and_the_cost_model(monkeypatch):
    monkeypatch.setattr(demo, "llm_choices", lambda: [("Groq", "groq", True, ""), ("Gemini", "gemini", False, ""),
                                                      ("Ollama", "ollama", True, "")])
    answers = iter(["4", "t"])                          # rules + Ollama, time cost model
    monkeypatch.setattr(builtins, "input", lambda *_: next(answers))
    chosen, mode, side_by_side = demo.choose_setup(_options())
    assert (chosen.llm_provider, chosen.offline, chosen.cost_model) == ("ollama", True, "time")
    assert mode == "hybrid" and not side_by_side

    answers = iter(["", ""])                            # Enter twice: rules only, static cost
    chosen, mode, side_by_side = demo.choose_setup(_options())
    assert (chosen.llm_provider, chosen.cost_model, mode, side_by_side) == ("auto", "static", "rule", False)

    answers = iter(["5", ""])                           # the last entry compares every proposer
    assert demo.choose_setup(_options())[2] is True


def test_compare_lists_every_proposer(monkeypatch, capsys):
    monkeypatch.setattr(demo, "llm_choices", lambda: [("Groq", "groq", False, "no key")])
    demo.Style.enabled = False
    with open(os.path.join(ROOT, "demo_programs", "3_loop.c"), encoding="utf-8") as fh:
        status = demo.compare(fh.read(), "3_loop.c", _options())
    out = capsys.readouterr().out
    assert status == 0
    rules = next(line for line in out.splitlines() if line.strip().startswith("Rules only"))
    assert "%" in rules and "tested" in rules
    assert "not ready" in next(line for line in out.splitlines() if line.strip().startswith("Rules + Groq"))


def test_time_cost_model_accepts_the_strength_reduction():
    sample = os.path.join(ROOT, "demo_programs", "7_time_cost_model.c")

    def accepted(*extra):
        out = run_demo(sample, "--inputs", "n=5", *extra).stdout
        row = next(line for line in out.splitlines() if line.strip().startswith("Strength reduction"))
        return int(row.split()[-3])                     # ... Suggested Correct Accepted No-gain Wrong

    assert accepted() == 0 and accepted("--cost-model", "time") >= 1


def test_a_real_program_runs_in_strict_mode():
    path = demo.real_files()[0]
    proc = run_demo(path)
    assert proc.returncode == 0, proc.stdout[-600:]
    assert "strict C mode" in proc.stdout and "SUMMARY" in proc.stdout


def test_wrong_suggestions_are_listed_apart(capsys):
    class WrongLLM:
        available, unavailable_reason = True, ""

        def propose(self, program):
            return TACProgram.from_string("print 2"), "wrong"

    orch = Orchestrator(max_llm_calls=1)
    orch.llm_optimizer = WrongLLM()
    result = orch.optimize(TACProgram.from_string("t0 = x * 2\nprint t0"))
    demo.Style.enabled = False
    demo.suggestion_summary(result, llm_enabled=True, llm_note="", hidden=0)
    out = capsys.readouterr().out
    assert "Wrong suggestions, blocked by the verifier: 1" in out
