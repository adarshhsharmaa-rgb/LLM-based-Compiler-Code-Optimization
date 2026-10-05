"""The verifier is the zero-false-positive guarantee: these tests inject wrong
optimizations and require that every one of them is caught."""
import pytest

from src.agents.verifier import Verifier, symbolic_trace
from src.frontend import compile_source
from src.tac.program import TACProgram


def P(text):
    return TACProgram.from_string(text)


@pytest.fixture
def verifier():
    return Verifier()


# ------------------------------------------------------------ equivalent pairs
@pytest.mark.parametrize("orig,cand", [
    ("t0 = 3 + 5\nprint t0", "t0 = 8\nprint t0"),
    ("t0 = 3 + 5\nprint t0", "print 8"),
    ("t0 = x + 0\nprint t0", "print x"),
    ("t0 = x * 2\nprint t0", "t0 = x + x\nprint t0"),
    ("t0 = x * 8\nprint t0", "t0 = x << 3\nprint t0"),
    ("t0 = a + b\nt1 = b + a\nt2 = t0 * t1\nprint t2", "t0 = a + b\nt2 = t0 * t0\nprint t2"),
    ("y = 20\nx = 10\nprint x", "print 10"),
    ("t0 = x - x\nprint t0", "print 0"),
    ("t0 = a * b\nt1 = t0 + a\nprint t1", "t1 = a * b + a\nprint t1".replace("a * b + a", "a * b")
     .replace("t1 = a * b", "t0 = a * b\nt1 = t0 + a")),
])
def test_equivalent_straight_line_programs_pass(verifier, orig, cand):
    result = verifier.verify(P(orig), P(cand))
    assert result.passed, result.reason
    assert result.method == "both"


def test_equivalent_loop_programs_pass(verifier):
    orig = compile_source("int s = 0; int i = 0; while (i < 10) { int t = 2 + 3; s = s + t; i = i + 1; } print(s);")
    cand = P("s = 0\ni = 0\nL0:\nt3 = i < 10\nifFalse t3 goto L1\ns = s + 5\ni = i + 1\ngoto L0\nL1:\nprint s")
    result = verifier.verify(orig, cand)
    assert result.passed, result.reason
    assert result.method == "differential" and "skipped" in result.reason


def test_equivalent_branch_program_with_inputs(verifier):
    orig = compile_source("int y = 0; if (x > 5) { y = x * 1; } else { y = x + 0; } print(y);")
    cand = compile_source("print(x);")
    assert verifier.verify(orig, cand).passed


# ---------------------------------------------------- injected wrong changes
@pytest.mark.parametrize("orig,cand", [
    ("t0 = 3 + 5\nprint t0", "t0 = 9\nprint t0"),                    # wrong fold
    ("t0 = x * 1\nprint t0", "t0 = 1\nprint t0"),                    # wrong identity
    ("t0 = x - 0\nprint t0", "t0 = 0 - x\nprint t0"),                 # operand swap on non-commutative op
    ("t0 = a - b\nt1 = b - a\nt2 = t0 * t1\nprint t2",
     "t0 = a - b\nt2 = t0 * t0\nprint t2"),                           # CSE across non-commutative op
    ("x = 1\nprint x\nx = 2\nprint x", "x = 2\nprint x\nprint x"),     # removed a live store
    ("t0 = x * 3\nprint t0", "t0 = x + x\nprint t0"),                 # wrong strength reduction
    ("t0 = x / 2\nprint t0", "t0 = x << 1\nprint t0"),                # shift is not division
    ("print a\nprint b", "print b\nprint a"),                         # reordered output
    ("print 1", ""),                                                   # dropped output
])
def test_wrong_straight_line_changes_fail(verifier, orig, cand):
    result = verifier.verify(P(orig), P(cand))
    assert not result.passed


def test_differential_reports_failing_inputs(verifier):
    result = verifier.verify(P("t0 = x * 1\nprint t0"), P("t0 = 1\nprint t0"))
    assert result.method == "differential"
    assert "inputs" in result.details and "mismatch" in result.reason


def test_wrong_loop_change_fails(verifier):
    orig = P("s = 0\ni = 0\nL0:\nt0 = i < 10\nifFalse t0 goto L1\ns = s + 5\ni = i + 1\ngoto L0\nL1:\nprint s")
    off_by_one = P("s = 0\ni = 0\nL0:\nt0 = i <= 10\nifFalse t0 goto L1\ns = s + 5\ni = i + 1\ngoto L0\nL1:\nprint s")
    assert not verifier.verify(orig, off_by_one).passed


def test_removing_loop_increment_detected_as_timeout(verifier):
    orig = P("i = 0\nL0:\nt0 = i < 3\nifFalse t0 goto L1\ni = i + 1\ngoto L0\nL1:\nprint i")
    broken = P("i = 0\nL0:\nt0 = i < 3\nifFalse t0 goto L1\ngoto L0\nL1:\nprint i")
    result = verifier.verify(orig, broken)
    assert not result.passed and "timeout" in result.reason


def test_wrong_branch_change_caught_by_random_inputs(verifier):
    orig = P("t0 = x > 5\nifFalse t0 goto L0\nprint 1\ngoto L1\nL0:\nprint 0\nL1:")
    wrong_branch = P("t0 = x > 5\nifFalse t0 goto L0\nprint 1\ngoto L1\nL0:\nprint 1\nL1:")
    assert not verifier.verify(orig, wrong_branch).passed


def test_off_by_one_condition_caught_by_boundary_inputs(verifier):
    # Only x == 5 distinguishes these; uniform random sampling would almost never hit it.
    orig = P("t0 = x > 5\nifFalse t0 goto L0\nprint 1\ngoto L1\nL0:\nprint 0\nL1:")
    flipped = P("t0 = x >= 5\nifFalse t0 goto L0\nprint 1\ngoto L1\nL0:\nprint 0\nL1:")
    result = verifier.verify(orig, flipped)
    assert not result.passed and result.details["inputs"] == {"x": 5}


def test_removing_trapping_division_is_rejected(verifier):
    # original fails when b == 0; deleting the "dead" division would change behaviour
    orig = P("t0 = a / b\nprint a")
    cand = P("print a")
    result = verifier.verify(orig, cand)
    assert not result.passed


def test_symbolic_catches_divisor_set_change(verifier):
    verifier_no_zero = Verifier(value_range=(1, 50), num_random=5)
    orig = P("t0 = a / b\nprint a")
    cand = P("print a")
    # edge cases include all-zero inputs, but symbolic verification flags it independently
    result = verifier_no_zero._symbolic_verify(orig, cand)
    assert not result.passed and "division" in result.reason


def test_both_timeouts_are_inconclusive_and_rejected(verifier):
    loop = P("L0:\ngoto L0\nprint 1")
    result = Verifier(max_steps=100).verify(loop, loop.copy())
    assert not result.passed and "inconclusive" in result.reason


def test_same_runtime_error_is_equivalent(verifier):
    orig = P("print 1\nt0 = 5 / 0\nprint t0")
    cand = P("print 1\nt0 = 5 / 0\nprint 7")
    assert verifier.verify(orig, cand).passed  # both print [1] then fail identically


def test_candidate_reading_unassigned_variable_fails(verifier):
    orig = P("x = 3\nt0 = x + 1\nprint t0")
    cand = P("t0 = x + 1\nprint t0")   # dropped the definition of x
    assert not verifier.verify(orig, cand).passed


def test_symbolic_trace_canonical_forms():
    a, _ = symbolic_trace(P("t0 = x * 2\nt1 = t0 + y\nprint t1"))
    b, _ = symbolic_trace(P("t0 = y + x\nt1 = t0 + x\nprint t1"))
    assert a == b
    c, _ = symbolic_trace(P("t0 = x > y\nprint t0"))
    d, _ = symbolic_trace(P("t0 = y < x\nprint t0"))
    assert c == d


def test_input_sets_include_boundary_values(verifier):
    sets = verifier.input_sets(["a"], {7})
    for k in (6, 7, 8):
        assert {"a": k} in sets


def test_input_sets_include_edge_cases(verifier):
    sets = verifier.input_sets(["a", "b"])
    assert len(sets) == 25
    for edge in (0, 1, -1, 99, -99):
        assert {"a": edge, "b": edge} in sets
    assert all(-100 <= v <= 100 for s in sets for v in s.values())
