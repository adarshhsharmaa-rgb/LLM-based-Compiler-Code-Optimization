import pytest

from src.frontend.ast_nodes import (
    Assignment, BinaryExpr, ForStmt, IfStmt, NumberLit, PrintStmt, UnaryExpr, VarDecl, VarRef, WhileStmt,
)
from src.frontend.lexer import Lexer
from src.frontend.parser import ParseError, Parser


def parse(src):
    return Parser(Lexer(src).tokenize()).parse()


def expr(src):
    return parse(f"print({src});").statements[0].value


def test_var_decl_with_and_without_init():
    prog = parse("int x = 5; int y;")
    assert prog.statements == [VarDecl("x", NumberLit(5)), VarDecl("y", None)]


def test_assignment():
    assert parse("x = a + b;").statements == [Assignment("x", BinaryExpr("+", VarRef("a"), VarRef("b")))]


def test_print():
    assert parse("print(x);").statements == [PrintStmt(VarRef("x"))]


def test_if_else():
    stmt = parse("if (x > 5) { y = 1; } else { y = 2; }").statements[0]
    assert isinstance(stmt, IfStmt)
    assert stmt.condition == BinaryExpr(">", VarRef("x"), NumberLit(5))
    assert stmt.then_body == [Assignment("y", NumberLit(1))]
    assert stmt.else_body == [Assignment("y", NumberLit(2))]


def test_if_without_else():
    stmt = parse("if (x) { print(x); }").statements[0]
    assert stmt.else_body is None


def test_while():
    stmt = parse("while (i < 10) { i = i + 1; }").statements[0]
    assert isinstance(stmt, WhileStmt)
    assert stmt.body == [Assignment("i", BinaryExpr("+", VarRef("i"), NumberLit(1)))]


def test_for_with_declaration_init():
    stmt = parse("for (int i = 0; i < 3; i = i + 1) { print(i); }").statements[0]
    assert isinstance(stmt, ForStmt)
    assert stmt.init == VarDecl("i", NumberLit(0))
    assert stmt.condition == BinaryExpr("<", VarRef("i"), NumberLit(3))
    assert stmt.update == Assignment("i", BinaryExpr("+", VarRef("i"), NumberLit(1)))
    assert stmt.body == [PrintStmt(VarRef("i"))]


def test_for_with_assignment_init():
    stmt = parse("for (i = 0; i < 3; i = i + 1) { }").statements[0]
    assert stmt.init == Assignment("i", NumberLit(0)) and stmt.body == []


def test_nested_blocks():
    stmt = parse("while (a) { if (b) { while (c) { print(1); } } }").statements[0]
    inner = stmt.body[0].then_body[0]
    assert isinstance(inner, WhileStmt) and inner.body == [PrintStmt(NumberLit(1))]


def test_multiplication_binds_tighter_than_addition():
    assert expr("1 + 2 * 3") == BinaryExpr("+", NumberLit(1), BinaryExpr("*", NumberLit(2), NumberLit(3)))


def test_left_associativity():
    assert expr("10 - 4 - 3") == BinaryExpr("-", BinaryExpr("-", NumberLit(10), NumberLit(4)), NumberLit(3))
    assert expr("8 / 4 % 3") == BinaryExpr("%", BinaryExpr("/", NumberLit(8), NumberLit(4)), NumberLit(3))


def test_parentheses_override_precedence():
    assert expr("(1 + 2) * 3") == BinaryExpr("*", BinaryExpr("+", NumberLit(1), NumberLit(2)), NumberLit(3))


def test_logical_precedence():
    # a || b && c  ==  a || (b && c);  comparisons bind tighter than &&
    e = expr("a || b && c < d")
    assert e == BinaryExpr("||", VarRef("a"),
                           BinaryExpr("&&", VarRef("b"), BinaryExpr("<", VarRef("c"), VarRef("d"))))


def test_comparison_binds_looser_than_arithmetic():
    assert expr("a + 1 == b * 2") == BinaryExpr(
        "==", BinaryExpr("+", VarRef("a"), NumberLit(1)), BinaryExpr("*", VarRef("b"), NumberLit(2)))


def test_unary_operators():
    assert expr("-x") == UnaryExpr("-", VarRef("x"))
    assert expr("!!x") == UnaryExpr("!", UnaryExpr("!", VarRef("x")))
    assert expr("-2 * 3") == BinaryExpr("*", UnaryExpr("-", NumberLit(2)), NumberLit(3))


def test_all_comparison_operators():
    for op in ["==", "!=", "<", ">", "<=", ">="]:
        assert expr(f"a {op} b").op == op


def test_error_message_format():
    with pytest.raises(ParseError) as exc:
        parse("int x = 5")
    assert str(exc.value) == "Parse error at line 1, col 10: expected ';', got end of input"


def test_error_reports_got_token():
    with pytest.raises(ParseError, match=r"line 2, col 8: expected '\)', got ';'"):
        parse("int a;\nprint(a;")


def test_missing_expression():
    with pytest.raises(ParseError, match="expected expression"):
        parse("x = ;")


def test_error_recovery_reports_multiple_errors():
    with pytest.raises(ParseError) as exc:
        parse("int x = ;\nint y = 2;\nprint(y\nz = 1;\n} ")
    errors = exc.value.errors
    assert len(errors) >= 2
    assert "line 1" in errors[0]
    assert any("line 3" in e or "line 4" in e for e in errors[1:])
    assert "more error" in str(exc.value)


def test_unclosed_block():
    with pytest.raises(ParseError, match=r"expected '\}'"):
        parse("while (x) { x = x - 1;")


def test_else_without_if_is_error():
    with pytest.raises(ParseError, match="expected statement"):
        parse("else { }")
