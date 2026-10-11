"""Regression tests for problems found by stress-testing the project."""
from src.agents.code_analyzer import CodeAnalyzer, OpportunityType
from src.agents.cost_evaluator import CostEvaluator
from src.agents.optimizer_llm import DEFAULT_PROVIDER
from src.agents.optimizer_rule import RuleBasedOptimizer
from src.agents.orchestrator import Orchestrator
from src.agents.verifier import Verifier
from src.frontend import compile_source
from src.tac.interpreter import TACInterpreter
from src.tac.program import TACProgram
from src.visualization.report import aggregate_metrics, format_metrics_table, result_to_record


def P(text):
    return TACProgram.from_string(text)


# ------------------------------------------------- programs that run too long
def test_program_too_long_to_verify_stops_at_once():
    # ~3 million steps: far beyond the verifier's limit. The loop used to try (and fail)
    # every single opportunity; now it stops after the first.
    prog = compile_source("int s = 0; for (int i = 0; i < 1000000; i = i + 1) { s = s + (2 + 3); } print(s);")
    result = Orchestrator(max_iterations=200).optimize(prog)
    assert "does not finish" in result.stopped_reason
    assert result.optimized_tac == prog and result.accepted_count == 0
    assert result.iterations == 1                      # not 200
    assert result.invalid_count == 0 and result.proposals == []   # unverifiable is not "invalid"
    assert result.output_match                         # nothing changed, so nothing can be wrong


def test_infinite_loop_program_is_not_reported_as_a_false_positive():
    prog = P("x = 1\nL0:\nt0 = x + 0\ngoto L0\nprint t0")
    result = Orchestrator().optimize(prog)
    assert result.stopped_reason and result.output_match and result.optimized_tac == prog


def test_verifier_marks_inconclusive_results():
    loop = P("L0:\ngoto L0")
    result = Verifier(max_steps=200).verify(loop, loop.copy())
    assert not result.passed and result.details.get("inconclusive") is True
    wrong = Verifier().verify(P("print 1"), P("print 2"))
    assert not wrong.passed and not wrong.details.get("inconclusive")


def test_unchanged_program_passes_final_check_without_running():
    prog = P("print x")
    result = Orchestrator().optimize(prog)
    assert result.output_match and "no changes" in result.final_check_reason


# ------------------------------------------------- CSE on non-arithmetic ops
def test_cse_of_shift_is_accepted():
    # Replacing a duplicate shift by a copy alone raises the weighted cost, so it used to be
    # rejected on every retry. Forwarding the copy in the same step makes it a real gain.
    prog = P("t1 = n << 2\na = t1 + 10\nt5 = n << 2\nb = t5 + 10\nt9 = a + b\nprint t9")
    result = Orchestrator(max_iterations=100).optimize(prog)
    assert "CSE" in result.optimization_types_applied
    assert result.rejected_count == 0 and result.output_match
    assert result.optimized_tac.to_string().count("<<") == 1


def test_cse_of_comparison_is_accepted():
    prog = P("t1 = a < b\nt2 = a < b\nifFalse t1 goto L0\nprint 1\nL0:\nifFalse t2 goto L1\nprint 2\nL1:")
    result = Orchestrator().optimize(prog)
    assert result.optimization_types_applied == ["CSE"]
    assert result.optimized_tac.to_string().count("a < b") == 1
    for a, b in ((1, 2), (2, 1), (3, 3)):
        run = lambda p: TACInterpreter().execute(p, {"a": a, "b": b})   # noqa: E731
        assert run(prog) == run(result.optimized_tac)


def test_cse_forwarding_is_a_cost_improvement_and_arithmetic_cse_is_unchanged():
    ev, opt = CostEvaluator(), RuleBasedOptimizer()
    shift = P("t1 = n << 2\nt5 = n << 2\nt9 = t1 + t5\nprint t9")
    opp = [o for o in CodeAnalyzer().analyze(shift) if o.type == OpportunityType.CSE][0]
    assert opp.details["forward"] is True
    new = opt.propose(shift, opp)
    assert new.to_string() == "t1 = n << 2\nt9 = t1 + t1\nprint t9"
    assert ev.is_improvement(ev.evaluate(shift), ev.evaluate(new))
    arith = P("t0 = a + b\nt1 = a + b\nt2 = t0 * t1\nprint t2")
    opp = [o for o in CodeAnalyzer().analyze(arith) if o.type == OpportunityType.CSE][0]
    assert opp.details["forward"] is False
    assert opt.propose(arith, opp).to_string() == "t0 = a + b\nt1 = t0\nt2 = t0 * t1\nprint t2"


# ------------------------------------------------- iteration cap reporting
def test_iteration_cap_is_only_reported_when_work_remains():
    src = "int a = 1 + 2; int b = a + 3; print(b);"
    full = Orchestrator(max_iterations=200).optimize(compile_source(src))
    steps_needed = full.accepted_count + full.rejected_count
    assert not full.hit_iteration_cap
    # exactly enough iterations to finish: converged, so not "stopped by the cap"
    exact = Orchestrator(max_iterations=steps_needed).optimize(compile_source(src))
    assert exact.optimized_tac == full.optimized_tac and not exact.hit_iteration_cap
    # one too few: genuinely cut short
    short = Orchestrator(max_iterations=steps_needed - 1).optimize(compile_source(src))
    assert short.hit_iteration_cap and short.output_match


# ------------------------------------------------- LLM bookkeeping
class _ScriptedLLM:
    available = True
    unavailable_reason = ""

    def __init__(self, replies):
        self.replies = list(replies)

    def propose(self, program):
        if not self.replies:
            return None, "nothing more"
        text, reason = self.replies.pop(0)
        return (TACProgram.from_string(text) if text else None), reason


def test_llm_calls_are_counted_including_unusable_replies():
    prog = P("t0 = x * 2\nprint t0")
    orch = Orchestrator(max_llm_calls=5)
    # call 1 (after the rule is rejected): unreadable; call 2 (rules exhausted): accepted,
    # so the loop continues; call 3: a wrong program, which ends the run.
    orch.llm_optimizer = _ScriptedLLM([(None, "garbled"), ("t0 = x << 1\nprint t0", "shift"), ("print 2", "wrong")])
    result = orch.optimize(prog)
    assert result.llm_calls == 3
    assert result.llm_proposals == 2 and result.llm_valid == 1
    assert [p["outcome"] for p in result.proposals if p["source"] == "llm"] == ["accepted", "invalid"]
    assert result.optimized_tac.to_string() == "t0 = x << 1\nprint t0"
    assert result.output_match


def test_metrics_report_suggestions_by_source():
    prog = P("t0 = x * 2\nprint t0")
    orch = Orchestrator(max_llm_calls=5)
    orch.llm_optimizer = _ScriptedLLM([("print 2", "wrong"), ("t0 = x << 1\nprint t0", "shift")])
    record = result_to_record(orch.optimize(prog, "mixed_001.src"), "mixed")
    metrics = aggregate_metrics([record])
    src = metrics["by_source"]
    assert src["Rule-based"] == {"suggested": 1, "verified": 1, "accepted": 0, "rejected": 1, "invalid": 0}
    assert src["LLM"] == {"suggested": 2, "verified": 1, "accepted": 1, "rejected": 0, "invalid": 1}
    assert src["Total"]["suggested"] == 3 == metrics["total_proposals"]
    table = format_metrics_table(metrics)
    assert "Suggestions by source" in table and "Rule-based" in table


def test_gemini_is_the_default_llm_provider():
    assert DEFAULT_PROVIDER == "gemini"


# ------------------------------------------------- strength reduction of huge powers of two
def test_strength_reduction_never_proposes_an_invalid_shift():
    # x * 2^65 used to become x << 65, which the interpreter rejects (shifts stop at 64),
    # so every such proposal failed verification.
    for k, expected in ((64, "t0 = x << 64"), (65, None), (70, None)):
        prog = P(f"t0 = x * {2 ** k}\nprint t0")
        opps = [o for o in CodeAnalyzer().analyze(prog) if o.type == OpportunityType.STRENGTH_REDUCTION]
        assert [o.details["after"] for o in opps] == ([expected] if expected else [])
        result = Orchestrator().optimize(prog)
        assert result.invalid_count == 0 and result.output_match


# ------------------------------------------------- metrics when the LLM made no proposals
def test_metrics_table_when_the_llm_was_enabled_but_never_proposed():
    record = result_to_record(Orchestrator().optimize(P("t0 = 3 + 5\nprint t0"), "arithmetic_001.src"),
                              "arithmetic")
    table = format_metrics_table(aggregate_metrics([record], llm_used=True))
    assert "n/a (no LLM proposals)" in table and "n/a %" not in table
    assert "n/a (LLM not used)" in format_metrics_table(aggregate_metrics([record], llm_used=False))
