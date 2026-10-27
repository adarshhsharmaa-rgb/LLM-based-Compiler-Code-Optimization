"""Tokenizer for the mini-language."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()
    IDENT = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    MOD = auto()
    ASSIGN = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMI = auto()
    COMMA = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    PRINT = auto()
    INT = auto()
    EOF = auto()


KEYWORDS = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "print": TokenType.PRINT,
    "int": TokenType.INT,
}

TWO_CHAR_TOKENS = {
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
    "<=": TokenType.LTE,
    ">=": TokenType.GTE,
    "&&": TokenType.AND,
    "||": TokenType.OR,
}

ONE_CHAR_TOKENS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.MOD,
    "=": TokenType.ASSIGN,
    "<": TokenType.LT,
    ">": TokenType.GT,
    "!": TokenType.NOT,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    ";": TokenType.SEMI,
    ",": TokenType.COMMA,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    line: int
    col: int


class LexerError(Exception):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"Lexer error at line {line}, col {col}: {message}")
        self.line = line
        self.col = col


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else ""

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _skip_whitespace_and_comments(self) -> None:
        while self.pos < len(self.source):
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
            elif ch == "/" and self._peek(1) == "/":
                while self.pos < len(self.source) and self._peek() != "\n":
                    self._advance()
            elif ch == "/" and self._peek(1) == "*":
                start_line, start_col = self.line, self.col
                self._advance()
                self._advance()
                while not (self._peek() == "*" and self._peek(1) == "/"):
                    if self.pos >= len(self.source):
                        raise LexerError("unterminated block comment", start_line, start_col)
                    self._advance()
                self._advance()
                self._advance()
            else:
                break

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while True:
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                tokens.append(Token(TokenType.EOF, "", self.line, self.col))
                return tokens
            line, col = self.line, self.col
            ch = self._peek()

            if ch.isdigit():
                start = self.pos
                while self._peek().isdigit():
                    self._advance()
                if self._peek().isalpha() or self._peek() == "_":
                    raise LexerError(f"invalid number literal starting with {self.source[start:self.pos + 1]!r}",
                                     line, col)
                tokens.append(Token(TokenType.NUMBER, self.source[start:self.pos], line, col))
                continue

            if ch.isalpha() or ch == "_":
                start = self.pos
                while self._peek().isalnum() or self._peek() == "_":
                    self._advance()
                word = self.source[start:self.pos]
                tokens.append(Token(KEYWORDS.get(word, TokenType.IDENT), word, line, col))
                continue

            two = ch + self._peek(1)
            if two in TWO_CHAR_TOKENS:
                self._advance()
                self._advance()
                tokens.append(Token(TWO_CHAR_TOKENS[two], two, line, col))
                continue

            if ch in ONE_CHAR_TOKENS:
                self._advance()
                tokens.append(Token(ONE_CHAR_TOKENS[ch], ch, line, col))
                continue

            if ch in "&|":
                raise LexerError(f"unexpected character {ch!r} (did you mean '{ch}{ch}'?)", line, col)
            raise LexerError(f"unexpected character {ch!r}", line, col)
