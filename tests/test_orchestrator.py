import json
from types import SimpleNamespace

from src.agents.orchestrator import Orchestrator
from src.frontend import compile_source
from src.tac.interpreter import TACInterpreter
from src.tac.program import TACProgram


def run(prog, inputs=None):
    return TACInterpreter().execute(prog, inputs)


def test_end_to_end_mixed_program():
    src = "int a = 3 + 4; int b = a + 0; int c = b * 1; int dead = 99; int d = a + 0; print(c + d);"
    prog = compile_source(src)
    result = Orchestrator().optimize(prog, "mixed_demo.src")
    assert result.output_match
    assert result.optimized_tac.to_string() == "print 14"
    assert result.final_cost.weighted_total < result.original_cost.weighted_total
    assert result.cost_reduction_pct > 30
    applied = set(result.optimization_types_applied)
    assert {"CONSTANT_FOLD", "COPY_PROPAGATION", "DEAD_CODE"} <= applied
    assert result.invalid_count == 0
    assert result.accepted_count == len(result.optimization_types_applied)


def test_original_program_is_not_mutated():
    prog = compile_source("int a = 2 * 3; print(a);")
    snapshot = prog.to_string()
    result = Orchestrator().optimize(prog)
    assert prog.to_string() == snapshot
    assert result.original_tac is prog


def test_loop_program_optimized_and_correct():
    src = "int sum = 0; int i = 0; while (i < 10) { int t = 2 + 3; sum = sum + t; i = i + 1; } print(sum);"
    prog = compile_source(src)
    result = Orchestrator().optimize(prog)
    assert run(result.optimized_tac) == run(prog) == [50]
    assert "sum = sum + 5" in result.optimized_tac.to_string()
    assert result.output_match


def test_program_with_inputs_and_branches():
    src = "int y = 0; if (in_x > 5) { y = in_x * 1; } else { y = in_x + 0; } print(y * 4);"
    prog = compile_source(src)
    result = Orchestrator().optimize(prog)
    for x in (-3, 5, 6, 40):
        assert run(result.optimized_tac, {"in_x": x}) == run(prog, {"in_x": x})
    assert result.output_match
    assert "STRENGTH_REDUCTION" in result.optimization_types_applied


def test_no_opportunities_returns_original():
    prog = TACProgram.from_string("print x")
    result = Orchestrator().optimize(prog)
    assert result.optimized_tac == prog
    assert result.iterations == 1 and result.accepted_count == 0
    assert result.cost_reduction_pct == 0.0 and result.output_match


def test_all_proposals_rejected_returns_original():
    # x * 2 -> x + x is cost-neutral, so the only proposal is rejected
    prog = TACProgram.from_string("t0 = x * 2\nprint t0")
    result = Orchestrator().optimize(prog)
    assert result.optimized_tac == prog
    assert result.rejected_count == 1 and result.accepted_count == 0
    assert result.log.entries[-1].description == "No more opportunities found."


def test_dead_code_only_program():
    prog = TACProgram.from_string("a = 1\nb = 2\nc = 3\nprint 0")
    result = Orchestrator().optimize(prog)
    assert result.optimized_tac.to_string() == "print 0"
    assert result.optimization_types_applied == ["DEAD_CODE"] * 3


def test_max_iterations_cap():
    prog = compile_source("int a = 1 + 2; int b = a + 3; int c = b + 4; print(c);")
    result = Orchestrator(max_iterations=3).optimize(prog)
    assert result.iterations == 3 and result.hit_iteration_cap
    assert result.output_match


def test_cost_history_is_monotone_non_increasing():
    prog = compile_source("int a = 4 * 5; int b = a * 1; int c = b + 0; int z = 9; print(c * 8);")
    result = Orchestrator().optimize(prog)
    hist = result.cost_history
    assert hist[0] == result.original_cost.weighted_total
    assert hist[-1] == result.final_cost.weighted_total
    assert all(b <= a for a, b in zip(hist, hist[1:]))


def test_decision_log_format_and_json(tmp_path):
    prog = compile_source("int a = 3 + 5; print(a);")
    result = Orchestrator().optimize(prog, "arithmetic_001.src")
    text = result.format_report()
    assert text.startswith("=== Program: arithmetic_001.src ===")
    for marker in ("--- Iteration 1 ---", "[ANALYZE]", "[PROPOSE]", "[VERIFY]", "[COST]", "[ACCEPT]",
                   "=== RESULT ===", "Output match:  PASS", "=== Original TAC ===", "=== Optimized TAC ==="):
        assert marker in text
    path = tmp_path / "log.json"
    result.log.save(str(path))
    data = json.loads(path.read_text(encoding="utf-8"))
    phases = {e["phase"] for e in data["entries"]}
    assert {"analyze", "propose", "verify", "evaluate", "accept"} <= phases


def test_whole_generated_categories_never_produce_false_positives():
    import random
    import importlib.util
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "dataset", "generator.py")
    spec = importlib.util.spec_from_file_location("gen", path)
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    random.seed(7)
    orch = Orchestrator()
    for category in gen.CATEGORY_COUNTS:
        for i in range(4):
            prog = compile_source(gen.generate_program(category, i))
            result = orch.optimize(prog)
            assert result.output_match, (category, i)


# ------------------------------------------------------------------ LLM path
class _FakeLLM:
    """Stands in for LLMOptimizer: returns a fixed sequence of proposals."""

    def __init__(self, proposals):
        self.proposals = list(proposals)
        self.available = True
        self.calls = 0

    def propose(self, program):
        self.calls += 1
        if not self.proposals:
            return None, "nothing more"
        text, reason = self.proposals.pop(0)
        return TACProgram.from_string(text), reason


def test_llm_wrong_proposal_is_rejected_and_counted():
    prog = TACProgram.from_string("t0 = x * 2\nprint t0")
    orch = Orchestrator()
    orch.llm_optimizer = _FakeLLM([("print 2", "bogus: assume x == 1")])
    result = orch.optimize(prog)
    assert result.optimized_tac == prog               # bad proposal never accepted
    assert result.llm_proposals == 1 and result.llm_valid == 0
    assert result.invalid_count == 1 and result.output_match


def test_llm_valid_proposal_is_accepted():
    prog = TACProgram.from_string("t0 = x * 2\nt1 = t0 + 0\nprint t1")
    orch = Orchestrator()
    # rule-based handles everything except the cost-neutral x*2; LLM proposes x << 1
    orch.llm_optimizer = _FakeLLM([("t0 = x << 1\nprint t0", "strength reduction via shift")])
    result = orch.optimize(prog)
    assert result.output_match
    assert result.llm_proposals == 1 and result.llm_valid == 1
    assert "LLM" in result.optimization_types_applied
    assert result.optimized_tac.to_string() == "t0 = x << 1\nprint t0"


def test_unavailable_llm_is_skipped():
    orch = Orchestrator()
    orch.llm_optimizer = SimpleNamespace(available=False)
    result = orch.optimize(TACProgram.from_string("t0 = 1 + 1\nprint t0"))
    assert result.output_match and result.llm_proposals == 0


def test_llm_not_consulted_for_provably_minimal_program():
    orch = Orchestrator()
    fake = _FakeLLM([("print 9", "should never be asked")])
    orch.llm_optimizer = fake
    result = orch.optimize(compile_source("int a = 2 + 3; print(a * 2);"))
    assert result.optimized_tac.to_string() == "print 10"
    assert fake.calls == 0 and result.llm_proposals == 0
    assert "LLM not consulted" in result.log.format_log()


def test_is_provably_minimal():
    assert Orchestrator.is_provably_minimal(TACProgram.from_string("print 1\nprint -4"))
    assert not Orchestrator.is_provably_minimal(TACProgram.from_string("print x"))
    assert not Orchestrator.is_provably_minimal(TACProgram.from_string("x = 1\nprint 1"))
