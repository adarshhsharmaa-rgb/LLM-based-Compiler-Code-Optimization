from src.agents.code_analyzer import CodeAnalyzer, OpportunityType as OT
from src.tac.program import TACProgram


def analyze(text):
    return CodeAnalyzer().analyze(TACProgram.from_string(text))


def of_type(opps, otype):
    return [o for o in opps if o.type == otype]


def test_constant_fold_detected():
    opps = of_type(analyze("t0 = 3 + 5\nprint t0"), OT.CONSTANT_FOLD)
    assert len(opps) == 1
    assert opps[0].location == 0 and opps[0].priority == 100
    assert opps[0].details["value"] == "8"


def test_constant_fold_unary_and_comparison():
    opps = of_type(analyze("t0 = -4\nt1 = 3 < 5\nt2 = - 7\nprint t1\nprint t2"), OT.CONSTANT_FOLD)
    assert [o.location for o in opps] == [2] or {o.details["value"] for o in opps} >= {"1"}
    assert any(o.details["value"] == "1" for o in opps)


def test_constant_fold_skips_division_by_zero():
    assert not of_type(analyze("t0 = 5 / 0\nprint t0"), OT.CONSTANT_FOLD)


def test_algebraic_identities():
    text = "\n".join([
        "t0 = x + 0", "t1 = 0 + x", "t2 = x - 0", "t3 = x * 1", "t4 = 1 * x",
        "t5 = x * 0", "t6 = 0 * x", "t7 = x / 1", "t8 = x - x",
    ] + [f"print t{i}" for i in range(9)])
    opps = of_type(analyze(text), OT.ALGEBRAIC_SIMPLIFY)
    replacement = {o.location: o.details["replacement"] for o in opps}
    assert replacement == {0: "x", 1: "x", 2: "x", 3: "x", 4: "x", 5: "0", 6: "0", 7: "x", 8: "0"}
    assert all(o.priority == 90 for o in opps)


def test_dead_code_detected():
    opps = of_type(analyze("x = 10\ny = 20\nt0 = y * 3\nprint x"), OT.DEAD_CODE)
    assert sorted(o.location for o in opps) == [1, 2] or sorted(o.location for o in opps) == [2]
    assert 2 in {o.location for o in opps}


def test_dead_code_overwritten_store():
    opps = of_type(analyze("x = 1\nx = 2\nprint x"), OT.DEAD_CODE)
    assert [o.location for o in opps] == [0]


def test_dead_code_respects_loops():
    # i is read at the loop head on the back edge, so its update is NOT dead
    text = "i = 0\nL0:\nt0 = i < 3\nifFalse t0 goto L1\ni = i + 1\ngoto L0\nL1:\nprint 0"
    locations = {o.location for o in of_type(analyze(text), OT.DEAD_CODE)}
    assert 4 not in locations and 0 not in locations


def test_dead_code_never_removes_control_flow_or_prints():
    text = "L0:\nifFalse c goto L1\nprint c\ngoto L0\nL1:"
    assert not of_type(analyze(text), OT.DEAD_CODE)


def test_dead_code_keeps_possibly_trapping_division():
    opps = of_type(analyze("t0 = a / b\nt1 = a / 2\nprint a"), OT.DEAD_CODE)
    assert [o.location for o in opps] == [1]


def test_cse_detected():
    opps = of_type(analyze("t0 = a + b\nt1 = a + b\nt2 = t0 * t1\nprint t2"), OT.CSE)
    assert len(opps) == 1 and opps[0].location == 1 and opps[0].details["source"] == "t0"


def test_cse_commutative():
    opps = of_type(analyze("t0 = a * b\nt1 = b * a\nt2 = t0 + t1\nprint t2"), OT.CSE)
    assert len(opps) == 1


def test_cse_not_applied_when_operand_redefined():
    assert not of_type(analyze("t0 = a + b\na = 5\nt1 = a + b\nt2 = t0 + t1\nprint t2"), OT.CSE)


def test_cse_not_applied_when_first_result_redefined():
    assert not of_type(analyze("t0 = a + b\nt0 = 1\nt1 = a + b\nt2 = t0 + t1\nprint t2"), OT.CSE)


def test_cse_not_across_basic_blocks():
    assert not of_type(analyze("t0 = a + b\nL0:\nt1 = a + b\nprint t1\nprint t0"), OT.CSE)


def test_strength_reduction():
    opps = of_type(analyze("t0 = x * 2\nt1 = 8 * x\nt2 = x * 6\nprint t0\nprint t1\nprint t2"),
                   OT.STRENGTH_REDUCTION)
    by_loc = {o.location: o.details for o in opps}
    assert set(by_loc) == {0, 1}
    assert by_loc[0]["operator"] == "+" and by_loc[0]["arg2"] == "x"
    assert by_loc[1]["operator"] == "<<" and by_loc[1]["arg2"] == "3"


def test_copy_propagation_detected():
    opps = of_type(analyze("t0 = 5\nx = t0\nt1 = x + 1\nprint t1"), OT.COPY_PROPAGATION)
    propagate = [o for o in opps if o.details["mode"] == "propagate"]
    assert {o.details["var"] for o in propagate} == {"t0", "x"}


def test_copy_propagation_blocked_by_redefinition():
    opps = of_type(analyze("x = y\ny = 3\nt0 = x + 1\nprint t0"), OT.COPY_PROPAGATION)
    assert not [o for o in opps if o.details.get("var") == "x" and o.details["mode"] == "propagate"]


def test_copy_propagation_not_through_loop_merge():
    text = "s = 0\nL0:\nt0 = s + 1\ns = t0\nifFalse c goto L1\ngoto L0\nL1:\nprint s"
    opps = of_type(analyze(text), OT.COPY_PROPAGATION)
    sites = [s for o in opps if o.details["mode"] == "propagate" and o.details["var"] == "s"
             for s in o.details["sites"]]
    # s = 0 does not reach "t0 = s + 1" on every path (back edge carries s = t0)
    assert [2, "arg1"] not in sites


def test_copy_coalescing():
    opps = of_type(analyze("t0 = a + b\nx = t0\nprint x"), OT.COPY_PROPAGATION)
    assert any(o.details["mode"] == "coalesce" and o.location == 1 for o in opps)


def test_sorted_by_priority():
    opps = analyze("t0 = 3 + 5\nt1 = x * 1\ny = 7\nt2 = a + b\nt3 = a + b\nt4 = x * 4\nz = t0\n"
                   "print t1\nprint t2\nprint t3\nprint t4\nprint z")
    priorities = [o.priority for o in opps]
    assert priorities == sorted(priorities, reverse=True)
    assert {o.type for o in opps} == set(OT)


def test_empty_program():
    assert analyze("") == []
