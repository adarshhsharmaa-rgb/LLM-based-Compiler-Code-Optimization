"""Tests for the Review 3 additions: execution time in the cost model and SMT verification."""
import pytest

from src.agents.cost_evaluator import LATENCY, CostEvaluator, profile_inputs
from src.agents.orchestrator import Orchestrator
from src.agents.smt_verifier import is_loop_free, smt_equivalent, z3_available
from src.agents.verifier import Verifier
from src.frontend.c_frontend import compile_c
from src.tac.interpreter import TACInterpreter
from src.tac.program import TACProgram

needs_z3 = pytest.mark.skipif(not z3_available(), reason="the z3-solver package is not installed")


def tac(text):
    return TACProgram.from_string(text)


def c_program(body, strict=False):
    source = "#include <stdio.h>\nint main() {\n" + body + "\nreturn 0;\n}\n"
    return compile_c(source, strict=strict)[0]


# ---------------------------------------------------------------- execution time
def test_the_interpreter_counts_executed_instructions():
    program = tac("i = 0\nL0:\nt0 = i < 3\nifFalse t0 goto L1\ni = i + 1\ngoto L0\nL1:\nprint i")
    counts = [0] * len(program)
    assert TACInterpreter().execute(program, counts=counts) == [3]
    assert counts == [1, 4, 4, 4, 3, 3, 1, 1]


def test_execution_time_of_straight_line_code_is_the_sum_of_latencies():
    program = tac("x = 6\ny = x * 7\nz = y / 2\nprint z")
    expected = LATENCY["copy"] + LATENCY["multiply"] + LATENCY["divide"] + LATENCY["print"]
    assert CostEvaluator().evaluate(program).exec_time == expected


def test_work_inside_a_loop_counts_once_per_iteration():
    looped = tac("i = 0\ns = 0\nL0:\nt0 = i < 10\nifFalse t0 goto L1\nt1 = 3 * 4\ns = s + t1\ni = i + 1\ngoto L0\nL1:\nprint s")
    hoisted = tac("i = 0\ns = 0\nt1 = 3 * 4\nL0:\nt0 = i < 10\nifFalse t0 goto L1\ns = s + t1\ni = i + 1\ngoto L0\nL1:\nprint s")
    evaluator = CostEvaluator()
    a, b = evaluator.evaluate(looped), evaluator.evaluate(hoisted)
    assert a.weighted_total == b.weighted_total              # the static cost cannot tell them apart
    assert a.exec_time - b.exec_time == 9 * LATENCY["multiply"]
    assert not CostEvaluator("static").is_improvement(a, b)
    assert CostEvaluator("time").is_improvement(a, b)


def test_the_time_model_prefers_a_shift_to_a_multiplication():
    multiply, shift = tac("x = in_a * 8\nprint x"), tac("x = in_a << 3\nprint x")
    evaluator = CostEvaluator("time")
    assert evaluator.is_improvement(evaluator.evaluate(multiply), evaluator.evaluate(shift))
    assert not evaluator.is_improvement(evaluator.evaluate(shift), evaluator.evaluate(multiply))


def test_with_equal_time_the_time_model_falls_back_to_static_cost():
    evaluator = CostEvaluator("time")
    a, b = evaluator.evaluate(tac("L0:\nx = 1\nprint x")), evaluator.evaluate(tac("x = 1\nprint x"))
    assert a.exec_time == b.exec_time and evaluator.is_improvement(a, b)


def test_profile_inputs_do_not_depend_on_the_other_variables():
    both, one = profile_inputs(["in_a", "in_b"]), profile_inputs(["in_b"])
    assert [s["in_b"] for s in both] == [s["in_b"] for s in one]
    assert len(both) == 25 and profile_inputs([]) == [{}]


def test_a_run_that_traps_is_timed_up_to_the_trap():
    program = tac("x = 5\ny = x / in_d\nprint y")
    assert CostEvaluator().evaluate(program).exec_time > 0     # in_d = 0 is one of the profile inputs


def test_unknown_cost_model_is_refused():
    with pytest.raises(ValueError):
        CostEvaluator("fastest")


def test_orchestrator_reports_time_saved_and_accepts_strength_reduction_under_the_time_model():
    program = c_program('int n; scanf("%d", &n); int s = 0; for (int i = 0; i < 20; i++) { s = s + n * 2; } printf("%d", s);')
    static = Orchestrator(max_iterations=200).optimize(program, "p")
    timed = Orchestrator(max_iterations=200, cost_model="time").optimize(program, "p")
    assert static.cost_model == "static" and timed.cost_model == "time"
    assert static.time_reduction_pct > 0 and static.output_match and timed.output_match
    assert "STRENGTH_REDUCTION" not in static.optimization_types_applied
    assert "STRENGTH_REDUCTION" in timed.optimization_types_applied
    assert timed.final_cost.exec_time < static.final_cost.exec_time


# ---------------------------------------------------------------- SMT verification
def test_loop_detection():
    assert is_loop_free(tac("ifFalse in_a goto L0\nprint 1\nL0:\nprint 2"))
    assert not is_loop_free(tac("L0:\nprint 1\nif in_a goto L0"))


def test_without_loops_only():
    result = smt_equivalent(tac("L0:\nif in_a goto L0\nprint 1"), tac("print 1"))
    assert result.status == "unsupported"


@needs_z3
def test_equivalent_branching_programs_are_proved():
    a = c_program('int x; scanf("%d", &x); if (x > 5) { printf("%d", x * 2); } else { printf("%d", x + x); }')
    b = tac("t0 = in_x + in_x\nprint t0")
    result = smt_equivalent(a, b)
    assert result.status == "proved" and result.paths == 3


@needs_z3
def test_an_off_by_one_condition_is_refuted_with_the_input_that_shows_it():
    a = tac("t0 = in_x > 1000000\nifFalse t0 goto L0\nprint 1\nL0:\nprint 2")
    b = tac("t0 = in_x >= 1000000\nifFalse t0 goto L0\nprint 1\nL0:\nprint 2")
    result = smt_equivalent(a, b)
    assert result.status == "refuted" and result.counterexample == {"in_x": 1000000}


@needs_z3
def test_division_follows_c_and_a_removed_trap_is_noticed():
    assert smt_equivalent(tac("t0 = 0 - 7\nt1 = t0 / 2\nt2 = t0 % 2\nprint t1\nprint t2"),
                          tac("print -3\nprint -1")).status == "proved"
    with_trap = tac("t0 = 5 / in_d\nprint 1")
    assert smt_equivalent(with_trap, tac("print 1")).counterexample == {"in_d": 0}
    assert smt_equivalent(with_trap, tac("t0 = 7 % in_d\nprint 1")).status == "proved"


@needs_z3
def test_print_order_and_count_matter():
    assert smt_equivalent(tac("print in_a\nprint in_b"), tac("print in_b\nprint in_a")).status == "refuted"
    assert smt_equivalent(tac("print in_a"), tac("print in_a\nprint in_a")).status == "refuted"


@needs_z3
def test_the_verifier_catches_with_smt_what_its_tests_miss():
    """The two programs differ on exactly one input, which is not near any literal in them."""
    a = tac("t0 = in_x * 3\nt1 = t0 == 999999\nifFalse t1 goto L0\nprint 1\ngoto L1\nL0:\nprint 0\nL1:")
    b = tac("print 0")
    verifier = Verifier()
    assert verifier.verify(a, b).passed                          # testing alone is fooled
    proved = verifier.verify(a, b, prove=True)
    assert not proved.passed and proved.method == "smt" and proved.details["inputs"] == {"in_x": 333333}
    assert "original printed [1]" in proved.reason


@needs_z3
def test_the_final_check_proves_a_branching_program():
    program = c_program('int a, b; scanf("%d%d", &a, &b); int unused = a * 3; '
                        'if (a > b) { puts("FIRST"); return 0; } printf("%d", b - a + 0);', strict=True)
    result = Orchestrator(max_iterations=200).optimize(program, "p")
    assert result.output_match and result.proved and result.final_check_method == "smt"
    assert "proved for all inputs" in result.format_report()


def test_a_loop_program_is_tested_not_proved():
    program = c_program('int n; scanf("%d", &n); int s = 0; for (int i = 0; i < 5; i++) s += n; printf("%d", s);')
    result = Orchestrator(max_iterations=200).optimize(program, "p")
    assert result.output_match and not result.proved and result.final_check_method == "differential"


def test_a_failed_final_check_keeps_the_original_program(monkeypatch):
    program = c_program('int a; scanf("%d", &a); int t = a * 1; if (a > 3) printf("%d", t + 0); else printf("%d", 0);')
    orchestrator = Orchestrator(max_iterations=200)
    monkeypatch.setattr(orchestrator, "_final_output_check", lambda original, optimized: (False, "made to fail", "smt"))
    result = orchestrator.optimize(program, "p")
    assert result.reverted and result.output_match and result.optimized_tac == program
    assert result.cost_reduction_pct == 0 and result.accepted_count > 0


# ---------------------------------------------------------------- wide-range inputs
DIGIT_LOOP = ('long long p, d, ans; scanf("%lld%lld", &p, &d); ans = p; '
              'for (long long x = 10; x <= p; x *= 10) {{ long long a = p / x, b = p % x; '
              'if (b < {limit}) a--; if (p - d <= a * x + x - 1) ans = a * x + x - 1; }} printf("%lld", ans);')


def test_a_change_that_is_only_right_for_small_inputs_is_rejected():
    """Found by re-checking a Groq run: 'x - 1' was replaced by 9, which holds only while x is 10.

    The loop runs a second time only for p >= 100, beyond what the other input sets reach."""
    original = c_program(DIGIT_LOOP.format(limit="x - 1"), strict=True)
    wrong = c_program(DIGIT_LOOP.format(limit="9"), strict=True)
    verifier = Verifier()
    result = verifier.verify(original, wrong)
    assert not result.passed and "output mismatch" in result.reason
    assert max(abs(v) for v in result.details["inputs"].values()) >= 100
    assert verifier.verify(original, original.copy()).details["differential"]["wide_inputs"] > 0


def test_wide_inputs_never_make_a_long_running_pair_inconclusive():
    program = c_program('int n; scanf("%d", &n); int s = 0; for (int i = 0; i < n; i++) s += i; printf("%d", s);')
    verifier = Verifier()
    assert len(verifier.wide_sets(["in_n"])) == 60 and verifier.wide_sets([]) == []
    result = verifier.verify(program, program.copy())       # n up to a billion: far too long to run
    assert result.passed and result.details["differential"]["wide_inputs"] < 60
