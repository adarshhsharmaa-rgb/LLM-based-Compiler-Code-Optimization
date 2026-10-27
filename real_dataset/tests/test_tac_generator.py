from src.frontend import compile_source
from src.tac.instruction import TACOp
from src.tac.interpreter import TACInterpreter


def lines(src):
    return compile_source(src).to_string().splitlines()


def run(src, inputs=None):
    return TACInterpreter().execute(compile_source(src), inputs)


def test_number_literal_and_var_decl():
    assert lines("int x = 5;") == ["t0 = 5", "x = t0"]


def test_var_decl_without_initializer_is_zero():
    assert lines("int x;") == ["x = 0"]


def test_binary_expression():
    assert lines("int x = 3 + 5;") == ["t0 = 3", "t1 = 5", "t2 = t0 + t1", "x = t2"]


def test_var_ref_needs_no_instruction():
    assert lines("x = y;") == ["x = y"]
    assert lines("print(a);") == ["print a"]


def test_unary_expression():
    assert lines("x = -y;") == ["t0 = -y", "x = t0"]
    assert lines("x = !y;") == ["t0 = !y", "x = t0"]


def test_assignment_and_print():
    assert lines("x = a * b; print(x + 1);") == [
        "t0 = a * b", "x = t0", "t1 = 1", "t2 = x + t1", "print t2"]


def test_if_else_structure():
    out = lines("if (x) { y = 1; } else { y = 2; }")
    assert out == ["ifFalse x goto L0", "t0 = 1", "y = t0", "goto L1",
                   "L0:", "t1 = 2", "y = t1", "L1:"]


def test_if_without_else_structure():
    assert lines("if (x) { print(x); }") == ["ifFalse x goto L0", "print x", "L0:"]


def test_while_structure():
    out = lines("while (i < n) { i = i + 1; }")
    assert out == ["L0:", "t0 = i < n", "ifFalse t0 goto L1", "t1 = 1", "t2 = i + t1",
                   "i = t2", "goto L0", "L1:"]


def test_for_structure():
    prog = compile_source("for (int i = 0; i < 2; i = i + 1) { print(i); }")
    ops = [ins.op for ins in prog]
    assert ops == [TACOp.ASSIGN, TACOp.ASSIGN, TACOp.LABEL, TACOp.ASSIGN, TACOp.BINARY,
                   TACOp.IF_FALSE_GOTO, TACOp.PRINT, TACOp.ASSIGN, TACOp.BINARY, TACOp.ASSIGN,
                   TACOp.GOTO, TACOp.LABEL]
    # the update runs after the body, right before the back-edge
    assert prog[-2].label == prog[2].label


def test_temporaries_and_labels_are_unique():
    prog = compile_source("int a = 1 + 2; int b = 3 * 4; while (a < b) { a = a + 1; } if (a) { print(a); }")
    temps = [ins.result for ins in prog if ins.result and ins.result.startswith("t")]
    assert len(temps) == len(set(temps))
    labels = [ins.label for ins in prog if ins.op == TACOp.LABEL]
    assert len(labels) == len(set(labels))


def test_temp_names_avoid_user_identifiers():
    prog = compile_source("int t0 = 1; int t1 = t0 + 2; print(t1);")
    defined = [ins.result for ins in prog if ins.result]
    assert defined.count("t0") == 1 and defined.count("t1") == 1
    assert TACInterpreter().execute(prog) == [3]


def test_nested_expression_instruction_count():
    # (1 + 2) * (3 - 4): 4 literal loads + 3 binary + 1 store
    assert len(compile_source("x = (1 + 2) * (3 - 4);")) == 8


def test_generated_code_semantics():
    assert run("int s = 0; for (int i = 1; i <= 4; i = i + 1) { s = s + i * i; } print(s);") == [30]
    assert run("int x = 7; if (x > 5 && x < 10) { print(1); } else { print(0); }") == [1]
    assert run("print(n * 2);", {"n": 21}) == [42]
