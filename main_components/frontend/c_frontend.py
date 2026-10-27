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
* ``return`` anywhere in ``main`` and ``exit(...)``: the program stops there
* character literals (``'a'`` is 97), ``0x1F``, ``010`` and the ``LL``/``U`` suffixes
* ``bool`` with ``true``/``false`` (a stored value is normalised to 0 or 1)
* integer type aliases: ``typedef long long ll;`` and ``#define ll long long``
* ``using namespace std;`` is ignored, so C-style C++ (``scanf``/``printf``) is read too

Strict mode (``compile_c(source, strict=True)``, used for the real-program dataset)
keeps everything a run of the program shows:
* text printed by ``printf``/``puts``/``putchar`` becomes ``print <code>``, one code
  per distinct piece of text (``CProgram.texts``); spaces and newlines are separators
* ``a && b`` / ``a || b`` is refused when ``b`` divides, because TAC evaluates both
  sides and C would not

Not supported (reported with a clear error): functions other than ``main``,
arrays, pointers, ``float``/``char`` variables, ``break``/``continue``/``do``/``switch``,
bitwise operators, the ternary operator, ``++``/assignment inside expressions,
``scanf`` inside a loop, and macros other than type aliases.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .ast_nodes import (
    Assignment,
    BinaryExpr,
    ExitStmt,
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
    texts: dict[str, int] = field(default_factory=dict)           # strict mode: printed text -> its code


_TOKEN_RE = re.compile(r"""
      (?P<ws>\s+)
    | (?P<line_comment>//[^\n]*)
    | (?P<block_comment>/\*.*?\*/)
    | (?P<preproc>\#[^\n]*)
    | (?P<float>\d+\.\d*|\.\d+)
    | (?P<number>(?:0[xX][0-9a-fA-F]+|\d+)[uUlL]{0,3}(?![\w.]))
    | (?P<ident>[A-Za-z_]\w*)
    | (?P<string>"(?:\\.|[^"\\\n])*")
    | (?P<char>'(?:\\.|[^'\\\n])+')
    | (?P<op>\+\+|--|\+=|-=|\*=|/=|%=|==|!=|<=|>=|&&|\|\||<<|>>|->|[-+*/%=<>!(){};,&|^~?:\[\].])
""", re.VERBOSE | re.DOTALL)

_INT_WORDS = {"int", "long", "short", "unsigned", "signed", "__int64"}
_BOOL_WORDS = {"bool", "_Bool"}
_TYPE_WORDS = _INT_WORDS | _BOOL_WORDS | {"const"}
_BAD_TYPES = {"float", "double", "char", "void", "struct"}
_UNSUPPORTED_STMTS = {"break", "continue", "do", "switch", "goto", "case", "default"}
_RESERVED_NAMES = {"print", "goto", "nop", "ifFalse"}   # words with a meaning in TAC text
_COMPOUND = {"+=": "+", "-=": "-", "*=": "*", "/=": "/", "%=": "%"}
_ESCAPES = {"n": 10, "t": 9, "r": 13, "0": 0, "\\": 92, "'": 39, '"': 34}
_BLANKS = {9, 10, 13, 32}                    # characters that only separate printed values
_YIELDS_BOOL = {"==", "!=", "<", ">", "<=", ">=", "&&", "||"}
_LENGTH = r"(?:l{1,2}|h{1,2}|I64)?"          # printf/scanf length modifiers
_PRINTF_SPEC_RE = re.compile(r"%[-+ 0#]*\d*(?:\.\d+)?" + _LENGTH + r"([a-zA-Z])")
_SCANF_SPEC_RE = re.compile(r"%" + _LENGTH + r"([a-zA-Z])")
_DEFINE_RE = re.compile(r"^[ \t]*#[ \t]*define[ \t]+(\w+)(\(?)(.*)$", re.MULTILINE)
_PERCENT = ""                          # stands for a literal %% inside a format string
TEXT_CODE_BASE = 1_000_000                   # strict mode: the first printed text gets this code


@dataclass
class _Tok:
    kind: str
    text: str
    line: int


def _char_value(text: str, line: int) -> int:
    body = text[1:-1]
    if len(body) == 1:
        return ord(body)
    if len(body) == 2 and body[0] == "\\" and body[1] in _ESCAPES:
        return _ESCAPES[body[1]]
    raise CFrontendError(f"character literal {text} is not supported", line)


def _int_value(text: str) -> int:
    digits = text.rstrip("uUlL")
    if digits[:2] in ("0x", "0X"):
        return int(digits, 16)
    return int(digits, 8) if len(digits) > 1 and digits[0] == "0" else int(digits)


def _type_aliases(source: str, tokens: list[_Tok]) -> set[str]:
    """Names that ``#define`` makes another spelling of an integer type.

    Any other macro changes what the text means, so a program that uses one is refused.
    """
    aliases: set[str] = set()
    used = {t.text for t in tokens if t.kind == "ident"}
    for m in _DEFINE_RE.finditer(source):
        name, is_function_like = m.group(1), m.group(2)
        body = re.sub(r"//.*|/\*.*?\*/", "", m.group(3)).split()
        if not is_function_like and body and set(body) <= _INT_WORDS:
            aliases.add(name)
        elif name in used:
            line = source.count("\n", 0, m.start()) + 1
            raise CFrontendError(f"macro '{name}' is not supported (only integer type aliases are)", line)
    return aliases


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
            kind, text = "number", str(_char_value(text, line))
        elif kind == "number":
            text = str(_int_value(text))
        if kind not in ("ws", "line_comment", "block_comment", "preproc"):
            tokens.append(_Tok(kind, text, line))
        line += text.count("\n")
        pos = m.end()
    tokens.append(_Tok("eof", "", line))
    return tokens


class _Parser:
    def __init__(self, tokens: list[_Tok], type_aliases: set[str] | None = None, strict: bool = False):
        self.toks = tokens
        self.pos = 0
        self.loop_depth = 0
        self.strict = strict
        self.type_words = _TYPE_WORDS | set(type_aliases or ())
        self.bools: set[str] = set()        # generated names of bool variables
        self.texts: dict[str, int] = {}
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
            elif self.at("typedef"):
                self._typedef()
            elif self.at("using") and [t.text for t in self.toks[self.pos + 1:self.pos + 4]] == ["namespace", "std", ";"]:
                self.pos += 4       # C-style C++: the names it brings in are not ones we accept anyway
            elif self._is_type_start():
                if self._looks_like_function():
                    self.fail("only main() is supported; other functions are not")
                out += self._declaration()
            else:
                self.fail(f"unexpected '{self.tok.text}' outside main()")
        return out

    def _typedef(self) -> None:
        """typedef long long ll;  -- ``ll`` becomes another integer type word."""
        tok = self.advance()
        seen = 0
        while self.tok.kind == "ident" and self.tok.text in self.type_words and self.peek().text != ";":
            seen += self.advance().text not in _BOOL_WORDS | {"const"}
        if not seen or self.tok.kind != "ident" or self.peek().text != ";":
            self.fail("only typedefs of integer types are supported", tok)
        self.type_words = self.type_words | {self.advance().text}
        self.expect(";")

    def _statements_until_eof(self) -> list[Statement]:
        out: list[Statement] = []
        while self.tok.kind != "eof":
            out += self._statement(top_level=True)
        return out

    def _is_type_start(self) -> bool:
        if self.tok.kind == "ident" and self.tok.text in _BAD_TYPES and self.peek().text != "(":
            self.fail(f"type '{self.tok.text}' is not supported (int only)")
        return self.tok.kind == "ident" and self.tok.text in self.type_words

    def _is_main_start(self) -> bool:
        i = self.pos
        while self.toks[i].kind == "ident" and self.toks[i].text in (self.type_words | {"void"}):
            i += 1
        return self.toks[i].text == "main" and self.toks[i + 1].text == "("

    def _looks_like_function(self) -> bool:
        i = self.pos
        while self.toks[i].kind == "ident" and self.toks[i].text in self.type_words:
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
            if t.text == "typedef":
                self._typedef()
                return []
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
            if t.text in ("puts", "putchar") and self.peek().text == "(":
                if self.strict:
                    return self._text_call()
                self._skip_call()
                self.note(f"{t.text}() prints text, which is ignored (only integers are printed)")
                return []
            if t.text == "exit" and self.peek().text == "(":
                self._skip_call()
                return [ExitStmt()]
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

    def _store(self, name: str, value: Expression) -> Expression:
        """The value as it lands in ``name``: a bool keeps only 0 or 1."""
        if name not in self.bools:
            return value
        if isinstance(value, NumberLit) and value.value in (0, 1):
            return value
        if isinstance(value, BinaryExpr) and value.op in _YIELDS_BOOL:
            return value
        if isinstance(value, UnaryExpr) and value.op == "!":
            return value
        return UnaryExpr("!", UnaryExpr("!", value))

    def _declaration(self) -> list[Statement]:
        is_bool = False
        while self.tok.kind == "ident" and self.tok.text in self.type_words:
            is_bool |= self.advance().text in _BOOL_WORDS
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
            generated = self.declare(name, name_tok)
            if is_bool:
                self.bools.add(generated)
                init = self._store(generated, init) if init is not None else None
            out.append(VarDecl(generated, init))
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
            return Assignment(name, self._store(name, BinaryExpr(op, VarRef(name), NumberLit(1))))
        name_tok = self.tok
        c_name = self.ident()
        if self.at("["):
            self.fail("arrays are not supported")
        if self.at("("):
            self.fail(f"calling function '{c_name}' is not supported", name_tok)
        name = self.resolve(c_name, name_tok)
        if self.at("++") or self.at("--"):
            op = self.advance().text[0]
            return Assignment(name, self._store(name, BinaryExpr(op, VarRef(name), NumberLit(1))))
        if self.tok.text in _COMPOUND and self.tok.kind == "op":
            op = _COMPOUND[self.advance().text]
            return Assignment(name, self._store(name, BinaryExpr(op, VarRef(name), self._expression())))
        if not self.at("="):
            self.fail(f"expected an assignment to '{c_name}', got '{self.tok.text or 'end of file'}'")
        self.advance()
        value = self._expression()
        if self.at("="):
            self.fail("chained assignment (a = b = c) is not supported")
        return Assignment(name, self._store(name, value))

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
        self.advance()
        if not self.at(";"):
            self._expression()
        self.expect(";")
        if top_level and (self.at("}") or self.tok.kind == "eof"):
            return []                   # the end of main(): nothing left to skip
        return [ExitStmt()]

    def _format_string(self) -> str:
        """Consumes  ( "format"  and returns the format, a literal %% replaced by a marker."""
        self.expect("(")
        if self.tok.kind != "string":
            self.fail("expected a format string")
        return self.advance().text[1:-1].replace("%%", _PERCENT)

    def _text(self, chunk: str) -> list[Statement]:
        """Strict mode: the print for a piece of literal text (nothing for blank text)."""
        words = re.sub(r"\\[ntr]", " ", chunk).replace(_PERCENT, "%").split()
        if not self.strict or not words:
            return []
        code = self.texts.setdefault(" ".join(words), TEXT_CODE_BASE + len(self.texts))
        return [PrintStmt(NumberLit(code))]

    def _printf(self) -> list[Statement]:
        tok = self.advance()
        fmt = self._format_string()
        out: list[Statement] = []
        pos = specs = 0
        for m in _PRINTF_SPEC_RE.finditer(fmt):
            out += self._text(fmt[pos:m.start()])
            pos, specs = m.end(), specs + 1
            spec = m.group(1)
            if spec not in ("d", "i", "u") and not (spec == "c" and self.strict):
                self.fail(f"printf format '%{spec}' is not supported (only %d)", tok)
            self.expect(",")
            value = self._expression()
            if not (spec == "c" and isinstance(value, NumberLit) and value.value in _BLANKS):
                out.append(PrintStmt(value))
        out += self._text(fmt[pos:])
        if self.at(","):
            self.fail("printf has more arguments than %d specifiers", tok)
        self.expect(")")
        self.expect(";")
        if not self.strict:
            if re.sub(r"\\n|\\t|\s", "", _PRINTF_SPEC_RE.sub("", fmt)):
                self.note("text inside printf is ignored: only the %d values are printed")
            if not specs:
                self.note("a printf without %d prints nothing in TAC")
        return out

    def _text_call(self) -> list[Statement]:
        """Strict mode: puts("text") and putchar(c)."""
        tok = self.advance()
        self.expect("(")
        if tok.text == "puts":
            if self.tok.kind != "string":
                self.fail("puts() of something other than a string literal is not supported", tok)
            out = self._text(self.advance().text[1:-1])
        else:
            value = self._expression()
            blank = isinstance(value, NumberLit) and value.value in _BLANKS
            out = [] if blank else [PrintStmt(value)]
        self.expect(")")
        self.expect(";")
        return out

    def _scanf(self) -> list[Statement]:
        tok = self.advance()
        if self.loop_depth:
            self.fail("scanf inside a loop is not supported", tok)
        fmt = self._format_string()
        specs = _SCANF_SPEC_RE.findall(fmt)
        if any(s not in ("d", "i", "u") for s in specs):
            self.fail("scanf only supports %d", tok)
        out: list[Statement] = []
        for _ in specs:
            self.expect(",")
            self.expect("&")
            name_tok = self.tok
            c_name = self.ident()
            name = self.resolve(c_name, name_tok)
            if name in self.bools:
                self.fail("scanf into a bool is not supported", name_tok)
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
            tok = self.advance()
            right = sub()
            if self.strict and tok.text in ("&&", "||") and _may_trap(right):
                self.fail(f"'{tok.text}' with a division on its right needs short-circuit evaluation, "
                          "which TAC does not have", tok)
            expr = BinaryExpr(tok.text, expr, right)
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
            if t.text in ("true", "false"):
                self.advance()
                return NumberLit(int(t.text == "true"))
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


def _may_trap(expr: Expression) -> bool:
    """True if evaluating ``expr`` could divide by zero."""
    if isinstance(expr, BinaryExpr):
        if expr.op in ("/", "%") and not (isinstance(expr.right, NumberLit) and expr.right.value != 0):
            return True
        return _may_trap(expr.left) or _may_trap(expr.right)
    return isinstance(expr, UnaryExpr) and _may_trap(expr.operand)


def parse_c(source: str, strict: bool = False) -> CProgram:
    """Parse C source into the project's AST (see the module docstring for ``strict``)."""
    tokens = _tokenize(source)
    parser = _Parser(tokens, _type_aliases(source, tokens), strict)
    statements = parser.parse()
    return CProgram(Program(statements), parser.inputs, parser.notes, parser.texts)


def compile_c(source: str, strict: bool = False):
    """Parse C and lower it to TAC. Returns (TACProgram, CProgram)."""
    cprog = parse_c(source, strict)
    return TACGenerator().generate(cprog.ast), cprog
