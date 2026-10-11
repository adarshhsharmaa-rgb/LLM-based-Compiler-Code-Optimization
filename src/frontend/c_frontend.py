"""C front-end for the live demo: parses a small subset of real C into the
project's existing AST, so an ordinary ``.c`` file can go through the same
TAC generator and optimization agents.

Supported
---------
* ``#include`` lines (ignored), ``//`` and ``/* */`` comments
* ``int main() { ... }`` with an optional final ``return <expr>;``
* ``int`` variables, several per declaration (``int a = 1, b, c = a + 2;``)
* C block scoping: a variable declared inside ``{ }`` (or in a ``for`` header)
  is separate from an outer variable of the same name; it is renamed
  (``x`` -> ``x_2``) in the generated code. Using an undeclared variable or
  declaring one twice in the same scope is an error, as in C.
* ``=``, ``+= -= *= /= %=``, ``x++``, ``x--``, ``++x``, ``--x`` as statements
* ``if`` / ``else if`` / ``else``, ``while``, ``for`` (bodies with or without braces)
* ``+ - * / %``, comparisons, ``&& || !``, unary minus, parentheses
* ``printf("...%d...", expr, ...)``: every ``%d`` value is printed; the text
  around it is ignored (the TAC ``print`` instruction prints integers only)
* ``scanf("%d", &x)``: ``x`` becomes a program *input*, which the verifier
  tests with many different values

Not supported (reported with a clear error): functions other than ``main``,
arrays, pointers, ``float``/``char``, ``break``/``continue``/``do``/``switch``,
bitwise operators, the ternary operator, and ``++``/assignment inside expressions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .ast_nodes import (
    Assignment,
    BinaryExpr,
    Expression,
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
from .tac_generator import TACGenerator


class CFrontendError(Exception):
    def __init__(self, message: str, line: int | None = None):
        super().__init__(f"C error at line {line}: {message}" if line else f"C error: {message}")
        self.line = line


@dataclass
class CProgram:
    ast: Program
    inputs: list[tuple[str, str]] = field(default_factory=list)   # (input name, C variable)
    notes: list[str] = field(default_factory=list)


_TOKEN_RE = re.compile(r"""
      (?P<ws>\s+)
    | (?P<line_comment>//[^\n]*)
    | (?P<block_comment>/\*.*?\*/)
    | (?P<preproc>\#[^\n]*)
    | (?P<float>\d+\.\d*|\.\d+)
    | (?P<number>\d+)
    | (?P<ident>[A-Za-z_]\w*)
    | (?P<string>"(?:\\.|[^"\\\n])*")
    | (?P<char>'(?:\\.|[^'\\\n])+')
    | (?P<op>\+\+|--|\+=|-=|\*=|/=|%=|==|!=|<=|>=|&&|\|\||<<|>>|->|[-+*/%=<>!(){};,&|^~?:\[\].])
""", re.VERBOSE | re.DOTALL)

_TYPE_WORDS = {"int", "long", "short", "unsigned", "signed", "const"}
_BAD_TYPES = {"float", "double", "char", "void", "struct", "bool", "_Bool"}
_UNSUPPORTED_STMTS = {"break", "continue", "do", "switch", "goto", "case", "default", "typedef"}
_RESERVED_NAMES = {"print", "goto", "nop", "ifFalse"}   # words with a meaning in TAC text
_COMPOUND = {"+=": "+", "-=": "-", "*=": "*", "/=": "/", "%=": "%"}


@dataclass
class _Tok:
    kind: str
    text: str
    line: int


def _tokenize(source: str) -> list[_Tok]:
    tokens: list[_Tok] = []
    pos, line = 0, 1
    while pos < len(source):
        m = _TOKEN_RE.match(source, pos)
        if not m:
            raise CFrontendError(f"unexpected character {source[pos]!r}", line)
        kind, text = m.lastgroup, m.group()
        if kind == "float":
            raise CFrontendError("floating-point numbers are not supported (int only)", line)
        if kind == "char":
            raise CFrontendError("character literals are not supported (int only)", line)
        if kind not in ("ws", "line_comment", "block_comment", "preproc"):
            tokens.append(_Tok(kind, text, line))
        line += text.count("\n")
        pos = m.end()
    tokens.append(_Tok("eof", "", line))
    return tokens


class _Parser:
    def __init__(self, tokens: list[_Tok]):
        self.toks = tokens
        self.pos = 0
        self.loop_depth = 0
        self.inputs: list[tuple[str, str]] = []
        self.notes: list[str] = []
        # Scopes map a C name to the name used in the generated code.
        self.scopes: list[dict[str, str]] = [{}]
        self.active: set[str] = set()       # generated names currently in scope
        self.allocated: set[str] = set()    # every generated name ever used

    # ----------------------------------------------------------- scopes
    def push_scope(self) -> None:
        self.scopes.append({})

    def pop_scope(self) -> None:
        for generated in self.scopes.pop().values():
            self.active.discard(generated)

    def _fresh(self, base: str) -> str:
        n = 2
        while f"{base}_{n}" in self.allocated:
            n += 1
        return f"{base}_{n}"

    def declare(self, name: str, tok: "_Tok") -> str:
        if name in self.scopes[-1]:
            self.fail(f"'{name}' is already declared in this scope", tok)
        # A name still in use by an enclosing scope must not be overwritten: rename.
        generated = name if name not in self.active else self._fresh(name)
        self.scopes[-1][name] = generated
        self.active.add(generated)
        self.allocated.add(generated)
        return generated

    def resolve(self, name: str, tok: "_Tok") -> str:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        self.fail(f"'{name}' is not declared", tok)
        raise AssertionError("unreachable")

    # ---------------------------------------------------------- helpers
    @property
    def tok(self) -> _Tok:
        return self.toks[self.pos]

    def peek(self, offset: int = 1) -> _Tok:
        return self.toks[min(self.pos + offset, len(self.toks) - 1)]

    def at(self, text: str) -> bool:
        return self.tok.text == text and self.tok.kind in ("op", "ident")

    def advance(self) -> _Tok:
        t = self.tok
        if t.kind != "eof":
            self.pos += 1
        return t

    def fail(self, message: str, tok: _Tok | None = None):
        raise CFrontendError(message, (tok or self.tok).line)

    def expect(self, text: str) -> _Tok:
        if not self.at(text):
            got = self.tok.text or "end of file"
            self.fail(f"expected '{text}', got '{got}'")
        return self.advance()

    def note(self, message: str) -> None:
        if message not in self.notes:
            self.notes.append(message)

    def ident(self) -> str:
        t = self.tok
        if t.kind != "ident":
            self.fail(f"expected a variable name, got '{t.text or 'end of file'}'")
        if t.text in _RESERVED_NAMES:
            self.fail(f"'{t.text}' cannot be used as a variable name here (it is a TAC keyword)")
        self.advance()
        return t.text

    # ---------------------------------------------------------- program
    def parse(self) -> list[Statement]:
        has_main = any(t.kind == "ident" and t.text == "main" and self.toks[i + 1].text == "("
                       for i, t in enumerate(self.toks[:-1]))
        if not has_main:   # a bare snippet: just statements
            return self._statements_until_eof()
        out: list[Statement] = []
        while self.tok.kind != "eof":
            if self._is_main_start():
                out += self._main()
            elif self._is_type_start():
                if self._looks_like_function():
                    self.fail("only main() is supported; other functions are not")
                out += self._declaration()
            else:
                self.fail(f"unexpected '{self.tok.text}' outside main()")
        return out

    def _statements_until_eof(self) -> list[Statement]:
        out: list[Statement] = []
        while self.tok.kind != "eof":
            out += self._statement(top_level=True)
        return out

    def _is_type_start(self) -> bool:
        if self.tok.kind == "ident" and self.tok.text in _BAD_TYPES and self.peek().text != "(":
            self.fail(f"type '{self.tok.text}' is not supported (int only)")
        return self.tok.kind == "ident" and self.tok.text in _TYPE_WORDS

    def _is_main_start(self) -> bool:
        i = self.pos
        while self.toks[i].kind == "ident" and self.toks[i].text in (_TYPE_WORDS | {"void"}):
            i += 1
        return self.toks[i].text == "main" and self.toks[i + 1].text == "("

    def _looks_like_function(self) -> bool:
        i = self.pos
        while self.toks[i].kind == "ident" and self.toks[i].text in _TYPE_WORDS:
            i += 1
        return self.toks[i].kind == "ident" and self.toks[i + 1].text == "("

    def _main(self) -> list[Statement]:
        while not self.at("main"):
            self.advance()
        self.advance()
        self.expect("(")
        while not self.at(")"):
            if self.tok.kind == "eof":
                self.fail("unterminated parameter list of main()")
            self.advance()   # (void) or (int argc, char **argv): ignored
        self.expect(")")
        self.expect("{")
        self.push_scope()
        body: list[Statement] = []
        while not self.at("}"):
            if self.tok.kind == "eof":
                self.fail("missing '}' at the end of main()")
            body += self._statement(top_level=True)
        self.expect("}")
        self.pop_scope()
        return body

    # ------------------------------------------------------- statements
    def _block_or_statement(self) -> list[Statement]:
        self.push_scope()
        try:
            if self.at("{"):
                self.advance()
                body: list[Statement] = []
                while not self.at("}"):
                    if self.tok.kind == "eof":
                        self.fail("missing '}'")
                    body += self._statement()
                self.advance()
                return body
            return self._statement()
        finally:
            self.pop_scope()

    def _statement(self, top_level: bool = False) -> list[Statement]:
        t = self.tok
        if self.at(";"):
            self.advance()
            return []
        if self.at("{"):
            return self._block_or_statement()
        if t.kind == "ident":
            if t.text in _UNSUPPORTED_STMTS:
                self.fail(f"'{t.text}' is not supported")
            if self._is_type_start():
                return self._declaration()
            if t.text == "if":
                return [self._if()]
            if t.text == "while":
                return [self._while()]
            if t.text == "for":
                return self._for()
            if t.text == "return":
                return self._return(top_level)
            if t.text == "printf":
                return self._printf()
            if t.text == "scanf":
                return self._scanf()
            if t.text in ("puts", "putchar"):
                self._skip_call()
                self.note(f"{t.text}() prints text, which is ignored (only integers are printed)")
                return []
            if self.peek().text == "(":
                self.fail(f"calling function '{t.text}' is not supported")
        stmt = self._assignment_like()
        self.expect(";")
        return [stmt]

    def _skip_call(self) -> None:
        self.advance()
        self.expect("(")
        depth = 1
        while depth:
            if self.tok.kind == "eof":
                self.fail("unterminated function call")
            depth += self.at("(") - self.at(")")
            self.advance()
        self.expect(";")

    def _declaration(self) -> list[Statement]:
        while self.tok.kind == "ident" and self.tok.text in _TYPE_WORDS:
            self.advance()
        out: list[Statement] = []
        while True:
            if self.at("*"):
                self.fail("pointers are not supported")
            name_tok = self.tok
            name = self.ident()
            if self.at("["):
                self.fail("arrays are not supported")
            init = None
            if self.at("="):
                self.advance()
                init = self._expression()
            out.append(VarDecl(self.declare(name, name_tok), init))
            if self.at(","):
                self.advance()
                continue
            break
        self.expect(";")
        return out

    def _assignment_like(self) -> Statement:
        """x = e | x op= e | x++ | x-- | ++x | --x   (no trailing semicolon)"""
        if self.at("++") or self.at("--"):
            op = self.advance().text[0]
            name_tok = self.tok
            name = self.resolve(self.ident(), name_tok)
            return Assignment(name, BinaryExpr(op, VarRef(name), NumberLit(1)))
        name_tok = self.tok
        c_name = self.ident()
        if self.at("["):
            self.fail("arrays are not supported")
        if self.at("("):
            self.fail(f"calling function '{c_name}' is not supported", name_tok)
        name = self.resolve(c_name, name_tok)
        if self.at("++") or self.at("--"):
            op = self.advance().text[0]
            return Assignment(name, BinaryExpr(op, VarRef(name), NumberLit(1)))
        if self.tok.text in _COMPOUND and self.tok.kind == "op":
            op = _COMPOUND[self.advance().text]
            return Assignment(name, BinaryExpr(op, VarRef(name), self._expression()))
        if not self.at("="):
            self.fail(f"expected an assignment to '{c_name}', got '{self.tok.text or 'end of file'}'")
        self.advance()
        value = self._expression()
        if self.at("="):
            self.fail("chained assignment (a = b = c) is not supported")
        return Assignment(name, value)

    def _condition(self) -> Expression:
        self.expect("(")
        cond = self._expression()
        self.expect(")")
        return cond

    def _if(self) -> IfStmt:
        self.advance()
        cond = self._condition()
        then_body = self._block_or_statement()
        else_body = None
        if self.at("else"):
            self.advance()
            else_body = self._block_or_statement()   # "else if" parses as else { if ... }
        return IfStmt(cond, then_body, else_body)

    def _while(self) -> WhileStmt:
        self.advance()
        cond = self._condition()
        self.loop_depth += 1
        body = self._block_or_statement()
        self.loop_depth -= 1
        return WhileStmt(cond, body)

    def _for(self) -> list[Statement]:
        """for (init; cond; update) body  ==  init; while (cond) { body; update; }"""
        self.advance()
        self.expect("(")
        self.push_scope()          # a variable declared in the for header lives until the loop ends
        init: list[Statement] = []
        if self.at(";"):
            self.advance()
        elif self._is_type_start():
            init = self._declaration()
        else:
            init.append(self._assignment_like())
            while self.at(","):
                self.advance()
                init.append(self._assignment_like())
            self.expect(";")
        cond: Expression = NumberLit(1) if self.at(";") else self._expression()
        self.expect(";")
        update: list[Statement] = []
        while not self.at(")"):
            update.append(self._assignment_like())
            if self.at(","):
                self.advance()
        self.expect(")")
        self.loop_depth += 1
        body = self._block_or_statement()
        self.loop_depth -= 1
        self.pop_scope()
        return init + [WhileStmt(cond, body + update)]

    def _return(self, top_level: bool) -> list[Statement]:
        tok = self.advance()
        if not self.at(";"):
            self._expression()
        self.expect(";")
        if not top_level or not (self.at("}") or self.tok.kind == "eof"):
            self.fail("'return' is only supported as the last statement of main()", tok)
        return []

    def _format_string(self) -> str:
        """Consumes  ( "format"  and returns the format with literal %% removed."""
        self.expect("(")
        if self.tok.kind != "string":
            self.fail("expected a format string")
        return self.advance().text[1:-1].replace("%%", "")

    def _printf(self) -> list[Statement]:
        tok = self.advance()
        fmt = self._format_string()
        specs = re.findall(r"%[-+ 0#]*\d*(?:\.\d+)?(?:l{1,2}|h{1,2})?([a-zA-Z])", fmt)
        bad = [s for s in specs if s not in ("d", "i", "u")]
        if bad:
            self.fail(f"printf format '%{bad[0]}' is not supported (only %d)", tok)
        out: list[Statement] = []
        for _ in specs:
            self.expect(",")
            out.append(PrintStmt(self._expression()))
        if self.at(","):
            self.fail("printf has more arguments than %d specifiers", tok)
        self.expect(")")
        self.expect(";")
        if re.sub(r"%[-+ 0#]*\d*(?:\.\d+)?(?:l{1,2}|h{1,2})?[a-zA-Z]|\\n|\\t|\s", "", fmt):
            self.note("text inside printf is ignored: only the %d values are printed")
        if not specs:
            self.note("a printf without %d prints nothing in TAC")
        return out

    def _scanf(self) -> list[Statement]:
        tok = self.advance()
        if self.loop_depth:
            self.fail("scanf inside a loop is not supported", tok)
        fmt = self._format_string()
        specs = re.findall(r"%(?:l{1,2}|h{1,2})?([a-zA-Z])", fmt)
        if any(s not in ("d", "i", "u") for s in specs):
            self.fail("scanf only supports %d", tok)
        out: list[Statement] = []
        for _ in specs:
            self.expect(",")
            self.expect("&")
            name_tok = self.tok
            c_name = self.ident()
            name = self.resolve(c_name, name_tok)
            # Each scanf reads a fresh value: model it as a distinct program input.
            input_name = f"in_{c_name}"
            if input_name in self.allocated:
                input_name = self._fresh(input_name)
            self.allocated.add(input_name)
            self.active.add(input_name)      # inputs stay reserved for the whole program
            self.inputs.append((input_name, c_name))
            out.append(Assignment(name, VarRef(input_name)))
        self.expect(")")
        self.expect(";")
        return out

    # ------------------------------------------------------ expressions
    def _expression(self) -> Expression:
        expr = self._logical_or()
        if self.at("?"):
            self.fail("the ternary operator (?:) is not supported")
        return expr

    def _binary(self, sub, ops) -> Expression:
        expr = sub()
        while self.tok.kind == "op" and self.tok.text in ops:
            op = self.advance().text
            expr = BinaryExpr(op, expr, sub())
        return expr

    def _logical_or(self) -> Expression:
        return self._binary(self._logical_and, {"||"})

    def _logical_and(self) -> Expression:
        return self._binary(self._equality, {"&&"})

    def _equality(self) -> Expression:
        return self._binary(self._relational, {"==", "!="})

    def _relational(self) -> Expression:
        return self._binary(self._additive, {"<", ">", "<=", ">="})

    def _additive(self) -> Expression:
        expr = self._binary(self._multiplicative, {"+", "-"})
        if self.tok.kind == "op" and self.tok.text in ("&", "|", "^", "<<", ">>", "~"):
            self.fail(f"bitwise operator '{self.tok.text}' is not supported")
        return expr

    def _multiplicative(self) -> Expression:
        return self._binary(self._unary, {"*", "/", "%"})

    def _unary(self) -> Expression:
        if self.at("-"):
            self.advance()
            return UnaryExpr("-", self._unary())
        if self.at("!"):
            self.advance()
            return UnaryExpr("!", self._unary())
        if self.at("+"):
            self.advance()
            return self._unary()
        if self.at("++") or self.at("--"):
            self.fail("++ / -- inside an expression is not supported (use it as its own statement)")
        if self.at("&") or self.at("*") or self.at("~"):
            self.fail(f"operator '{self.tok.text}' is not supported here")
        return self._primary()

    def _primary(self) -> Expression:
        t = self.tok
        if t.kind == "number":
            self.advance()
            return NumberLit(int(t.text))
        if t.kind == "ident":
            if self.peek().text == "(":
                self.fail(f"calling function '{t.text}' is not supported")
            name = self.ident()
            if self.at("["):
                self.fail("arrays are not supported")
            if self.at("++") or self.at("--"):
                self.fail("++ / -- inside an expression is not supported (use it as its own statement)")
            return VarRef(self.resolve(name, t))
        if self.at("("):
            self.advance()
            expr = self._expression()
            self.expect(")")
            return expr
        if t.kind == "string":
            self.fail("strings are not supported")
        self.fail(f"expected an expression, got '{t.text or 'end of file'}'")
        raise AssertionError("unreachable")


def parse_c(source: str) -> CProgram:
    """Parse C source into the project's AST."""
    parser = _Parser(_tokenize(source))
    statements = parser.parse()
    return CProgram(Program(statements), parser.inputs, parser.notes)


def compile_c(source: str):
    """Parse C and lower it to TAC. Returns (TACProgram, CProgram)."""
    cprog = parse_c(source)
    return TACGenerator().generate(cprog.ast), cprog
