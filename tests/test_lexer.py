import pytest

from src.frontend.lexer import Lexer, LexerError, TokenType as T


def types(src):
    return [t.type for t in Lexer(src).tokenize()]


def test_all_single_char_tokens():
    assert types("+ - * / % = < > ! ( ) { } ; ,") == [
        T.PLUS, T.MINUS, T.STAR, T.SLASH, T.MOD, T.ASSIGN, T.LT, T.GT, T.NOT,
        T.LPAREN, T.RPAREN, T.LBRACE, T.RBRACE, T.SEMI, T.COMMA, T.EOF]


def test_two_char_operators():
    assert types("== != <= >= && ||") == [T.EQ, T.NEQ, T.LTE, T.GTE, T.AND, T.OR, T.EOF]


def test_two_char_operators_without_spaces():
    assert types("a<=b==c!=d") == [T.IDENT, T.LTE, T.IDENT, T.EQ, T.IDENT, T.NEQ, T.IDENT, T.EOF]


def test_keywords_and_identifiers():
    toks = Lexer("if else while for print int iffy _x x1").tokenize()
    assert [t.type for t in toks] == [T.IF, T.ELSE, T.WHILE, T.FOR, T.PRINT, T.INT,
                                      T.IDENT, T.IDENT, T.IDENT, T.EOF]
    assert toks[6].value == "iffy"


def test_numbers():
    toks = Lexer("0 42 1234").tokenize()
    assert [(t.type, t.value) for t in toks[:-1]] == [(T.NUMBER, "0"), (T.NUMBER, "42"), (T.NUMBER, "1234")]


def test_line_comment_is_skipped():
    assert types("int x; // comment ; { }\nprint(x);") == [
        T.INT, T.IDENT, T.SEMI, T.PRINT, T.LPAREN, T.IDENT, T.RPAREN, T.SEMI, T.EOF]


def test_block_comment_is_skipped():
    assert types("a /* b \n c */ d") == [T.IDENT, T.IDENT, T.EOF]


def test_line_and_column_tracking():
    toks = Lexer("int x;\n  x = 5;").tokenize()
    x2 = toks[3]
    assert (x2.value, x2.line, x2.col) == ("x", 2, 3)
    five = toks[5]
    assert (five.line, five.col) == (2, 7)


def test_eof_position_and_empty_source():
    toks = Lexer("").tokenize()
    assert len(toks) == 1 and toks[0].type == T.EOF


@pytest.mark.parametrize("src,line,col", [("int x = 5 @ 3;", 1, 11), ("a\n  $", 2, 3)])
def test_unexpected_character_reports_position(src, line, col):
    with pytest.raises(LexerError) as exc:
        Lexer(src).tokenize()
    assert exc.value.line == line and exc.value.col == col
    assert f"line {line}, col {col}" in str(exc.value)


def test_single_ampersand_is_error():
    with pytest.raises(LexerError, match="did you mean '&&'"):
        Lexer("a & b").tokenize()


def test_invalid_number_literal():
    with pytest.raises(LexerError, match="invalid number"):
        Lexer("int x = 12abc;").tokenize()


def test_unterminated_block_comment():
    with pytest.raises(LexerError, match="unterminated"):
        Lexer("/* never closed").tokenize()
