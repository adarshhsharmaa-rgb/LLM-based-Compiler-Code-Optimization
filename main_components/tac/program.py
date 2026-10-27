"""TACProgram container plus a text parser for TAC listings."""
from __future__ import annotations

import dataclasses
import re

from .instruction import (
    BINARY_OPS,
    UNARY_OPS,
    TACInstruction,
    TACOp,
    is_literal,
    is_temp,
    is_variable,
)
from . import dataflow


class TACParseError(ValueError):
    pass


_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _is_operand(tok: str) -> bool:
    return is_literal(tok) or bool(_IDENT_RE.match(tok))


class TACProgram:
    def __init__(self, instructions: list[TACInstruction] | None = None):
        self.instructions: list[TACInstruction] = list(instructions or [])

    # ------------------------------------------------------------------ #
    def to_string(self) -> str:
        return "\n".join(ins.to_string() for ins in self.instructions)

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return f"TACProgram({len(self.instructions)} instructions)"

    def copy(self) -> "TACProgram":
        # Every field of TACInstruction is an immutable str/enum, so replacing
        # each dataclass yields a fully independent deep copy.
        return TACProgram([dataclasses.replace(ins) for ins in self.instructions])

    def __len__(self) -> int:
        return len(self.instructions)

    def __iter__(self):
        return iter(self.instructions)

    def __getitem__(self, idx):
        return self.instructions[idx]

    def __eq__(self, other) -> bool:
        return isinstance(other, TACProgram) and self.instructions == other.instructions

    # ------------------------------------------------------------------ #
    def get_all_variables(self, include_temps: bool = True) -> set[str]:
        names: set[str] = set()
        for ins in self.instructions:
            candidates = [ins.defined_var(), *ins.used_vars()]
            for name in candidates:
                if is_variable(name) and (include_temps or not is_temp(name)):
                    names.add(name)
        return names

    def get_input_variables(self) -> set[str]:
        """Variables that may be read before being written (free/input variables).

        Uses a must-analysis of definite assignment, so a variable written on only
        one branch of an if/else and read afterwards counts as an input.
        """
        instrs = self.instructions
        assigned = dataflow.definitely_assigned(instrs)
        reach = dataflow.reachable(dataflow.successors(instrs))
        inputs: set[str] = set()
        for i, ins in enumerate(instrs):
            if i not in reach:
                continue
            for v in ins.used_vars():
                if v not in assigned[i]:
                    inputs.add(v)
        return inputs

    def has_control_flow(self) -> bool:
        return dataflow.has_control_flow(self.instructions)

    # ------------------------------------------------------------------ #
    @classmethod
    def from_string(cls, text: str) -> "TACProgram":
        """Parse TAC in the format produced by ``to_string``.

        Accepted line forms::

            L0:                      label
            goto L0
            if x goto L1
            ifFalse x goto L1
            print x
            nop
            x = y                    copy / constant
            x = y op z               binary
            x = -y  |  x = - y  |  x = !y   unary

        Blank lines and ``//`` or ``#`` comments are ignored.
        """
        instructions: list[TACInstruction] = []
        for lineno, raw in enumerate(text.splitlines(), start=1):
            line = re.split(r"//|#", raw, maxsplit=1)[0].strip().rstrip(";").strip()
            if not line:
                continue
            instructions.append(_parse_line(line, lineno))
        prog = cls(instructions)
        _validate_labels(prog)
        return prog


def _parse_line(line: str, lineno: int) -> TACInstruction:
    def fail(msg: str):
        raise TACParseError(f"TAC line {lineno}: {msg}: {line!r}")

    if line.endswith(":") and " " not in line:
        name = line[:-1]
        if not _IDENT_RE.match(name):
            fail("invalid label")
        return TACInstruction(TACOp.LABEL, label=name)

    toks = line.split()
    head = toks[0]
    if head == "goto":
        if len(toks) != 2 or not _IDENT_RE.match(toks[1]):
            fail("malformed goto")
        return TACInstruction(TACOp.GOTO, label=toks[1])
    if head in ("if", "ifFalse"):
        if len(toks) != 4 or toks[2] != "goto" or not _is_operand(toks[1]) or not _IDENT_RE.match(toks[3]):
            fail(f"malformed {head}")
        op = TACOp.IF_GOTO if head == "if" else TACOp.IF_FALSE_GOTO
        return TACInstruction(op, arg1=toks[1], label=toks[3])
    if head == "print":
        if len(toks) != 2 or not _is_operand(toks[1]):
            fail("malformed print")
        return TACInstruction(TACOp.PRINT, arg1=toks[1])
    if head == "nop" and len(toks) == 1:
        return TACInstruction(TACOp.NOP)

    parsed = _parse_assignment(toks)
    if parsed is None:
        # Retry with operators split out, so "x=y+z" or "x = a<<2" also parse.
        spaced = re.sub(r"(==|!=|<=|>=|&&|\|\||<<|[=+\-*/%<>!])", r" \1 ", line)
        parsed = _parse_assignment(_retokenize(spaced.split()))
    if parsed is None:
        fail("unrecognised instruction")
    return parsed


def _parse_assignment(toks: list[str]) -> TACInstruction | None:
    if len(toks) < 3 or toks[1] != "=" or not _IDENT_RE.match(toks[0]):
        return None
    target = toks[0]
    rhs = toks[2:]
    if len(rhs) == 1:
        tok = rhs[0]
        if _is_operand(tok):
            return TACInstruction(TACOp.ASSIGN, result=target, arg1=tok)
        if tok[0] in UNARY_OPS and _is_operand(tok[1:]):
            return TACInstruction(TACOp.UNARY, result=target, operator=tok[0], arg1=tok[1:])
        return None
    if len(rhs) == 2:
        if rhs[0] in UNARY_OPS and _is_operand(rhs[1]):
            return TACInstruction(TACOp.UNARY, result=target, operator=rhs[0], arg1=rhs[1])
        return None
    if len(rhs) == 3:
        a, op, b = rhs
        if op in BINARY_OPS and _is_operand(a) and _is_operand(b):
            return TACInstruction(TACOp.BINARY, result=target, arg1=a, operator=op, arg2=b)
    return None


def _retokenize(parts: list[str]) -> list[str]:
    """Merge a '-' with a following number when it is a sign, not an operator."""
    out: list[str] = []
    i = 0
    while i < len(parts):
        p = parts[i]
        prev = out[-1] if out else None
        is_sign_position = prev is None or prev == "=" or prev in BINARY_OPS
        if p == "-" and i + 1 < len(parts) and parts[i + 1].isdigit() and is_sign_position and prev != "=":
            out.append("-" + parts[i + 1])
            i += 2
            continue
        out.append(p)
        i += 1
    return out


def _validate_labels(prog: TACProgram) -> None:
    labels = [ins.label for ins in prog.instructions if ins.op == TACOp.LABEL]
    if len(labels) != len(set(labels)):
        raise TACParseError("duplicate label definition")
    defined = set(labels)
    for ins in prog.instructions:
        if ins.is_jump() and ins.label not in defined:
            raise TACParseError(f"jump to undefined label {ins.label!r}")
