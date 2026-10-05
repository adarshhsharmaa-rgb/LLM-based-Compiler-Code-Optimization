"""Recursive-descent parser producing an AST ``Program``.

Grammar::

    program        -> statement*
    statement      -> varDecl | assignment | ifStmt | whileStmt | forStmt | printStmt
    varDecl        -> "int" IDENT ("=" expression)? ";"
    assignment     -> IDENT "=" expression ";"
    ifStmt         -> "if" "(" expression ")" block ("else" block)?
    whileStmt      -> "while" "(" expression ")" block
    forStmt        -> "for" "(" statement expression ";" IDENT "=" expression ")" block
    printStmt      -> "print" "(" expression ")" ";"
    block          -> "{" statement* "}"
    expression     -> logicalOr
    logicalOr      -> logicalAnd ("||" logicalAnd)*
    logicalAnd     -> comparison ("&&" comparison)*
    comparison     -> addition (("==" | "!=" | "<" | ">" | "<=" | ">=") addition)?
    addition       -> multiplication (("+" | "-") multiplication)*
    multiplication -> unary (("*" | "/" | "%") unary)*
    unary          -> ("!" | "-") unary | primary
    primary        -> NUMBER | IDENT | "(" expression ")"

On a syntax error the parser records it, resynchronises at the next statement
boundary and keeps going, so one ParseError can report several problems.
"""
from __future__ import annotations

from .ast_nodes import (
    Assignment,
    BinaryExpr,
    Expression,
    ForStmt,
    IfStmt,
    NumberLit,
    PrintStmt,
    Program,
    Statement,
    UnaryExpr,
    VarDecl,
    VarRef,
    WhileStmt,
)
from .lexer import Token, TokenType


class ParseError(Exception):
    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or [message]


class _SyntaxError(Exception):
    """Internal: a single syntax error, caught by the recovery loop."""


_COMPARISON = {
    TokenType.EQ: "==", TokenType.NEQ: "!=", TokenType.LT: "<",
    TokenType.GT: ">", TokenType.LTE: "<=", TokenType.GTE: ">=",
}
_ADDITIVE = {TokenType.PLUS: "+", TokenType.MINUS: "-"}
_MULTIPLICATIVE = {TokenType.STAR: "*", TokenType.SLASH: "/", TokenType.MOD: "%"}
_STATEMENT_STARTS = {TokenType.INT, TokenType.IF, TokenType.WHILE, TokenType.FOR, TokenType.PRINT}


def _describe(tok: Token) -> str:
    return "end of input" if tok.type == TokenType.EOF else f"'{tok.value}'"


class Parser:
    def __init__(self, tokens: list[Token]):
        if not tokens or tokens[-1].type != TokenType.EOF:
            last = tokens[-1] if tokens else None
            tokens = list(tokens) + [Token(TokenType.EOF, "", last.line if last else 1,
                                           last.col if last else 1)]
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------------ helpers
    def _peek(self, offset: int = 0) -> Token:
        idx = min(self.pos + offset, len(self.tokens) - 1)
        return self.tokens[idx]

    def _check(self, ttype: TokenType) -> bool:
        return self._peek().type == ttype

    def _advance(self) -> Token:
        tok = self._peek()
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def _match(self, *ttypes: TokenType) -> Token | None:
        if self._peek().type in ttypes:
            return self._advance()
        return None

    def _error(self, expected: str, tok: Token | None = None) -> _SyntaxError:
        tok = tok or self._peek()
        return _SyntaxError(f"Parse error at line {tok.line}, col {tok.col}: "
                            f"expected {expected}, got {_describe(tok)}")

    def _expect(self, ttype: TokenType, expected: str) -> Token:
        if self._check(ttype):
            return self._advance()
        raise self._error(expected)

    def _synchronize(self, start_pos: int) -> None:
        if self.pos == start_pos:
            self._advance()
        while not self._check(TokenType.EOF):
            prev = self.tokens[self.pos - 1] if self.pos > 0 else None
            if prev is not None and prev.type in (TokenType.SEMI, TokenType.RBRACE):
                return
            if self._peek().type in _STATEMENT_STARTS:
                return
            self._advance()

    # ------------------------------------------------------------ program
    def parse(self) -> Program:
        statements: list[Statement] = []
        errors: list[str] = []
        while not self._check(TokenType.EOF):
            start = self.pos
            try:
                statements.append(self._statement())
            except _SyntaxError as exc:
                errors.append(str(exc))
                self._synchronize(start)
        if errors:
            msg = errors[0]
            if len(errors) > 1:
                msg += f" (and {len(errors) - 1} more error{'s' if len(errors) > 2 else ''})"
            raise ParseError(msg, errors)
        return Program(statements)

    # ---------------------------------------------------------- statements
    def _statement(self) -> Statement:
        tok = self._peek()
        match tok.type:
            case TokenType.INT:
                return self._var_decl()
            case TokenType.IDENT:
                return self._assignment()
            case TokenType.IF:
                return self._if_stmt()
            case TokenType.WHILE:
                return self._while_stmt()
            case TokenType.FOR:
                return self._for_stmt()
            case TokenType.PRINT:
                return self._print_stmt()
        raise self._error("statement")

    def _var_decl(self) -> VarDecl:
        self._expect(TokenType.INT, "'int'")
        name = self._expect(TokenType.IDENT, "identifier").value
        init = None
        if self._match(TokenType.ASSIGN):
            init = self._expression()
        self._expect(TokenType.SEMI, "';'")
        return VarDecl(name, init)

    def _assignment(self, require_semi: bool = True) -> Assignment:
        name = self._expect(TokenType.IDENT, "identifier").value
        self._expect(TokenType.ASSIGN, "'='")
        value = self._expression()
        if require_semi:
            self._expect(TokenType.SEMI, "';'")
        return Assignment(name, value)

    def _if_stmt(self) -> IfStmt:
        self._expect(TokenType.IF, "'if'")
        self._expect(TokenType.LPAREN, "'('")
        cond = self._expression()
        self._expect(TokenType.RPAREN, "')'")
        then_body = self._block()
        else_body = None
        if self._match(TokenType.ELSE):
            else_body = self._block()
        return IfStmt(cond, then_body, else_body)

    def _while_stmt(self) -> WhileStmt:
        self._expect(TokenType.WHILE, "'while'")
        self._expect(TokenType.LPAREN, "'('")
        cond = self._expression()
        self._expect(TokenType.RPAREN, "')'")
        return WhileStmt(cond, self._block())

    def _for_stmt(self) -> ForStmt:
        self._expect(TokenType.FOR, "'for'")
        self._expect(TokenType.LPAREN, "'('")
        if self._check(TokenType.INT):
            init: Statement = self._var_decl()
        elif self._check(TokenType.IDENT):
            init = self._assignment()
        else:
            raise self._error("for-loop initialiser (declaration or assignment)")
        cond = self._expression()
        self._expect(TokenType.SEMI, "';'")
        update = self._assignment(require_semi=False)
        self._expect(TokenType.RPAREN, "')'")
        return ForStmt(init, cond, update, self._block())

    def _print_stmt(self) -> PrintStmt:
        self._expect(TokenType.PRINT, "'print'")
        self._expect(TokenType.LPAREN, "'('")
        value = self._expression()
        self._expect(TokenType.RPAREN, "')'")
        self._expect(TokenType.SEMI, "';'")
        return PrintStmt(value)

    def _block(self) -> list[Statement]:
        self._expect(TokenType.LBRACE, "'{'")
        body: list[Statement] = []
        while not self._check(TokenType.RBRACE):
            if self._check(TokenType.EOF):
                raise self._error("'}'")
            body.append(self._statement())
        self._advance()
        return body

    # --------------------------------------------------------- expressions
    def _expression(self) -> Expression:
        return self._logical_or()

    def _logical_or(self) -> Expression:
        expr = self._logical_and()
        while self._match(TokenType.OR):
            expr = BinaryExpr("||", expr, self._logical_and())
        return expr

    def _logical_and(self) -> Expression:
        expr = self._comparison()
        while self._match(TokenType.AND):
            expr = BinaryExpr("&&", expr, self._comparison())
        return expr

    def _comparison(self) -> Expression:
        expr = self._addition()
        tok = self._match(*_COMPARISON)
        if tok:
            expr = BinaryExpr(_COMPARISON[tok.type], expr, self._addition())
        return expr

    def _addition(self) -> Expression:
        expr = self._multiplication()
        while (tok := self._match(*_ADDITIVE)):
            expr = BinaryExpr(_ADDITIVE[tok.type], expr, self._multiplication())
        return expr

    def _multiplication(self) -> Expression:
        expr = self._unary()
        while (tok := self._match(*_MULTIPLICATIVE)):
            expr = BinaryExpr(_MULTIPLICATIVE[tok.type], expr, self._unary())
        return expr

    def _unary(self) -> Expression:
        if self._match(TokenType.NOT):
            return UnaryExpr("!", self._unary())
        if self._match(TokenType.MINUS):
            return UnaryExpr("-", self._unary())
        return self._primary()

    def _primary(self) -> Expression:
        tok = self._peek()
        if tok.type == TokenType.NUMBER:
            self._advance()
            return NumberLit(int(tok.value))
        if tok.type == TokenType.IDENT:
            self._advance()
            return VarRef(tok.value)
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._expression()
            self._expect(TokenType.RPAREN, "')'")
            return expr
        raise self._error("expression")
