import pytest

from src.frontend import compile_source
from src.tac.instruction import TACInstruction, TACOp
from src.tac.interpreter import (
    DivisionByZeroError,
    ExecutionTimeout,
    TACInterpreter,
    UndefinedVariableError,
    UnknownLabelError,
    c_mod,
    eval_binary,
    trunc_div,
)
from src.tac.program import TACProgram


def run_tac(text, inputs=None, max_steps=10000):
    return TACInterpreter().execute(TACProgram.from_string(text), inputs, max_steps)


def test_arithmetic():
    assert run_tac("t0 = 3 + 5\nt1 = t0 * 2\nt2 = t1 - 1\nprint t2") == [15]


@pytest.mark.parametrize("a,b,q,r", [(7, 2, 3, 1), (-7, 2, -3, -1), (7, -2, -3, 1), (-7, -2, 3, -1), (0, 5, 0, 0)])
def test_division_truncates_toward_zero(a, b, q, r):
    assert trunc_div(a, b) == q
    assert c_mod(a, b) == r
    assert a == b * q + r


@pytest.mark.parametrize("op,a,b,expected", [
    ("==", 3, 3, 1), ("==", 3, 4, 0), ("!=", 3, 4, 1), ("<", 2, 3, 1), (">", 2, 3, 0),
    ("<=", 3, 3, 1), (">=", 2, 3, 0), ("&&", 5, -1, 1), ("&&", 5, 0, 0), ("||", 0, 0, 0),
    ("||", 0, 7, 1), ("<<", -3, 2, -12),
])
def test_comparison_and_logical_ops(op, a, b, expected):
    assert eval_binary(op, a, b) == expected


def test_unary_ops():
    assert run_tac("t0 = -x\nt1 = !x\nt2 = !t1\nprint t0\nprint t1\nprint t2", {"x": 4}) == [-4, 0, 1]


def test_inputs_are_used():
    assert run_tac("t0 = a + b\nprint t0", {"a": 2, "b": 40}) == [42]


def test_while_loop():
    src = "int s = 0; int i = 0; while (i < 10) { s = s + i; i = i + 1; } print(s);"
    assert TACInterpreter().execute(compile_source(src)) == [45]


def test_if_goto_and_if_false_goto():
    text = "if c goto L0\nprint 1\ngoto L1\nL0:\nprint 2\nL1:\nifFalse c goto L2\nprint 3\nL2:"
    assert run_tac(text, {"c": 1}) == [2, 3]
    assert run_tac(text, {"c": 0}) == [1]


def test_nested_loops_and_prints_in_order():
    src = "for (int i = 0; i < 2; i = i + 1) { for (int j = 0; j < 2; j = j + 1) { print(i * 10 + j); } }"
    assert TACInterpreter().execute(compile_source(src)) == [0, 1, 10, 11]


def test_division_by_zero_raises_with_partial_output():
    with pytest.raises(DivisionByZeroError) as exc:
        run_tac("print 1\nt0 = x / 0\nprint t0", {"x": 3})
    assert exc.value.outputs == [1]
    with pytest.raises(DivisionByZeroError):
        run_tac("t0 = 5 % y\nprint t0", {"y": 0})


def test_timeout_on_infinite_loop():
    with pytest.raises(ExecutionTimeout) as exc:
        run_tac("L0:\nprint 1\ngoto L0", max_steps=50)
    assert len(exc.value.outputs) == 17  # 3 instructions per iteration


def test_undefined_variable():
    with pytest.raises(UndefinedVariableError, match="'ghost'"):
        run_tac("print ghost")


def test_unknown_label():
    prog = TACProgram([TACInstruction(TACOp.GOTO, label="nowhere")])
    with pytest.raises(UnknownLabelError):
        TACInterpreter().execute(prog)


def test_nop_and_empty_program():
    assert TACInterpreter().execute(TACProgram([TACInstruction(TACOp.NOP)])) == []
    assert TACInterpreter().execute(TACProgram()) == []


def test_inputs_dict_is_not_mutated():
    inputs = {"x": 1}
    run_tac("x = 5\nprint x", inputs)
    assert inputs == {"x": 1}


def test_negative_literals():
    assert run_tac("t0 = -5\nt1 = t0 - -3\nprint t1") == [-2]


def test_program_text_roundtrip():
    prog = compile_source("int a = -3; while (a < 0) { a = a + 1; } if (!a) { print(a % 2); }")
    assert TACProgram.from_string(prog.to_string()) == prog


def test_input_variable_detection():
    prog = TACProgram.from_string("t0 = a + 1\nb = t0\nprint b\nprint c")
    assert prog.get_input_variables() == {"a", "c"}
    # assigned on only one branch -> still an input
    branchy = TACProgram.from_string("ifFalse k goto L0\ny = 1\nL0:\nprint y")
    assert branchy.get_input_variables() == {"k", "y"}


def test_get_all_variables():
    prog = TACProgram.from_string("t0 = a + 1\nb = t0\nprint b")
    assert prog.get_all_variables() == {"t0", "a", "b"}
    assert prog.get_all_variables(include_temps=False) == {"a", "b"}
