"""TAC instruction representation.

A TAC instruction has at most one operator and at most two operands.  Operands
are strings: either a variable name (``x``, ``t3``) or an integer literal
(``5``, ``-12``).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

_INT_RE = re.compile(r"^-?\d+$")
_TEMP_RE = re.compile(r"^t\d+$")

ARITHMETIC_OPS = frozenset({"+", "-", "*", "/", "%"})
COMPARISON_OPS = frozenset({"==", "!=", "<", ">", "<=", ">="})
LOGICAL_OPS = frozenset({"&&", "||"})
# Shift only appears as the result of strength reduction; the source language
# has no shift operator.
SHIFT_OPS = frozenset({"<<"})
BINARY_OPS = ARITHMETIC_OPS | COMPARISON_OPS | LOGICAL_OPS | SHIFT_OPS
UNARY_OPS = frozenset({"-", "!"})
COMMUTATIVE_OPS = frozenset({"+", "*", "==", "!=", "&&", "||"})


def is_literal(value: str | None) -> bool:
    """True if ``value`` is an integer literal operand."""
    return value is not None and bool(_INT_RE.match(value))


def is_temp(name: str | None) -> bool:
    """True if ``name`` looks like a compiler temporary (t0, t1, ...)."""
    return name is not None and bool(_TEMP_RE.match(name))


def is_variable(value: str | None) -> bool:
    return value is not None and not is_literal(value)


class TACOp(Enum):
    ASSIGN = "ASSIGN"               # result = arg1
    BINARY = "BINARY"               # result = arg1 operator arg2
    UNARY = "UNARY"                 # result = operator arg1
    LABEL = "LABEL"                 # label:
    GOTO = "GOTO"                   # goto label
    IF_GOTO = "IF_GOTO"             # if arg1 goto label
    IF_FALSE_GOTO = "IF_FALSE_GOTO" # ifFalse arg1 goto label
    PRINT = "PRINT"                 # print arg1
    NOP = "NOP"


JUMP_OPS = frozenset({TACOp.GOTO, TACOp.IF_GOTO, TACOp.IF_FALSE_GOTO})
DEFINING_OPS = frozenset({TACOp.ASSIGN, TACOp.BINARY, TACOp.UNARY})


@dataclass
class TACInstruction:
    op: TACOp
    result: str | None = None
    arg1: str | None = None
    arg2: str | None = None
    operator: str | None = None
    label: str | None = None

    def to_string(self) -> str:
        match self.op:
            case TACOp.ASSIGN:
                return f"{self.result} = {self.arg1}"
            case TACOp.BINARY:
                return f"{self.result} = {self.arg1} {self.operator} {self.arg2}"
            case TACOp.UNARY:
                return f"{self.result} = {self.operator}{self.arg1}"
            case TACOp.LABEL:
                return f"{self.label}:"
            case TACOp.GOTO:
                return f"goto {self.label}"
            case TACOp.IF_GOTO:
                return f"if {self.arg1} goto {self.label}"
            case TACOp.IF_FALSE_GOTO:
                return f"ifFalse {self.arg1} goto {self.label}"
            case TACOp.PRINT:
                return f"print {self.arg1}"
            case TACOp.NOP:
                return "nop"
        raise ValueError(f"Unknown TAC op: {self.op}")

    def __str__(self) -> str:
        return self.to_string()

    # ------------------------------------------------------------------ #
    # Def/use helpers used by the dataflow analyses
    # ------------------------------------------------------------------ #
    def defined_var(self) -> str | None:
        """Variable written by this instruction, if any."""
        if self.op in DEFINING_OPS:
            return self.result
        return None

    def operand_fields(self) -> list[str]:
        """Names of the fields that hold operands read by this instruction."""
        match self.op:
            case TACOp.BINARY:
                return ["arg1", "arg2"]
            case TACOp.ASSIGN | TACOp.UNARY | TACOp.IF_GOTO | TACOp.IF_FALSE_GOTO | TACOp.PRINT:
                return ["arg1"]
        return []

    def used_vars(self) -> list[str]:
        """Variables (not literals) read by this instruction."""
        out = []
        for field_name in self.operand_fields():
            value = getattr(self, field_name)
            if is_variable(value):
                out.append(value)
        return out

    def is_jump(self) -> bool:
        return self.op in JUMP_OPS
