import pytest

from src.agents.cost_evaluator import CostEvaluator
from src.tac.program import TACProgram


def cost(text):
    return CostEvaluator().evaluate(TACProgram.from_string(text))


def test_cost_breakdown_counts():
    c = cost("t0 = 3\nt1 = t0 + x\nx = t1\nL0:\nifFalse x goto L1\ngoto L0\nL1:\nprint x")
    assert c.instruction_count == 8
    assert c.arithmetic_ops == 1
    assert c.temp_vars == 2
    assert c.memory_ops == 2
    assert c.branch_ops == 2
    assert c.weighted_total == pytest.approx(8 * 1.0 + 1 * 2.0 + 2 * 0.5 + 2 * 1.5 + 2 * 1.0)


def test_comparisons_and_shifts_are_not_arithmetic():
    c = cost("t0 = a < b\nt1 = a << 2\nt2 = a && b\nprint t0")
    assert c.arithmetic_ops == 0


def test_each_arithmetic_operator_counts():
    c = cost("t0 = a + b\nt1 = a - b\nt2 = a * b\nt3 = a / b\nt4 = a % b")
    assert c.arithmetic_ops == 5


def test_temp_vars_counted_once():
    assert cost("t0 = 1\nt0 = 2\nt1 = t0\nprint t1").temp_vars == 2


def test_user_variables_are_not_temps():
    assert cost("x = 1\ntotal = x\nt = total\nprint t").temp_vars == 0


def test_empty_program_cost_is_zero():
    c = cost("")
    assert c.weighted_total == 0
    assert CostEvaluator().reduction_percentage(c, c) == 0.0


def test_optimized_version_is_cheaper():
    ev = CostEvaluator()
    orig = cost("t0 = 3\nt1 = 5\nt2 = t0 + t1\nx = t2\nprint x")
    opt = cost("print 8")
    assert ev.is_improvement(orig, opt)
    assert not ev.is_improvement(opt, orig)
    assert ev.reduction_percentage(orig, opt) == pytest.approx(
        (orig.weighted_total - opt.weighted_total) / orig.weighted_total * 100)


def test_equal_cost_is_not_improvement():
    ev = CostEvaluator()
    a = cost("t0 = x * 2\nprint t0")
    b = cost("t0 = x + x\nprint t0")
    assert a.weighted_total == b.weighted_total
    assert not ev.is_improvement(a, b)


def test_each_rule_transformation_lowers_cost():
    ev = CostEvaluator()
    pairs = [
        ("t0 = 3 + 5\nprint t0", "t0 = 8\nprint t0"),            # fold: BINARY -> ASSIGN
        ("t0 = x * 1\nprint t0", "t0 = x\nprint t0"),            # algebraic
        ("y = 1\nprint 2", "print 2"),                            # dead code
        ("t0 = a + b\nt1 = a + b\nprint t1", "t0 = a + b\nt1 = t0\nprint t1"),  # CSE
        ("t0 = x * 4\nprint t0", "t0 = x << 2\nprint t0"),       # strength reduction
        ("t0 = 5\nprint t0", "print 5"),                          # copy propagation
    ]
    for before, after in pairs:
        assert ev.is_improvement(cost(before), cost(after)), before


def test_to_dict():
    d = cost("print 1").to_dict()
    assert set(d) == {"instruction_count", "arithmetic_ops", "temp_vars", "memory_ops",
                      "branch_ops", "weighted_total"}
