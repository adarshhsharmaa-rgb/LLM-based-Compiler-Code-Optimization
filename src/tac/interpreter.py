"""Reference interpreter for TAC. Used by the verifier as the ground truth.

Semantics:
  * Values are unbounded Python ints (no wrap-around).
  * ``/`` truncates toward zero and ``%`` takes the sign of the dividend (C semantics).
  * Comparisons and logical operators yield 1 or 0; 0 is false, anything else true.
  * Reading a variable that was never assigned (and not supplied as an input)
    raises UndefinedVariableError.
"""
from __future__ import annotations

from .instruction import TACOp, is_literal
from .program import TACProgram

# Results larger than this many bits raise ValueOverflowError so runaway
# programs (e.g. repeated squaring in a loop) cannot exhaust memory.
MAX_VALUE_BITS = 1024
MAX_SHIFT = 64


class TACRuntimeError(Exception):
    """Base class for runtime failures. ``outputs`` holds what was printed so far."""

    def __init__(self, message: str, outputs: list[int] | None = None):
        super().__init__(message)
        self.outputs: list[int] = list(outputs or [])


class ExecutionTimeout(TACRuntimeError):
    pass


class DivisionByZeroError(TACRuntimeError):
    pass


class UndefinedVariableError(TACRuntimeError):
    pass


class UnknownLabelError(TACRuntimeError):
    pass


class ValueOverflowError(TACRuntimeError):
    pass


class InvalidOperationError(TACRuntimeError):
    pass


def trunc_div(a: int, b: int) -> int:
    if b == 0:
        raise DivisionByZeroError("division by zero")
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def c_mod(a: int, b: int) -> int:
    if b == 0:
        raise DivisionByZeroError("modulo by zero")
    return a - b * trunc_div(a, b)


def eval_binary(op: str, a: int, b: int) -> int:
    match op:
        case "+":
            r = a + b
        case "-":
            r = a - b
        case "*":
            r = a * b
        case "/":
            r = trunc_div(a, b)
        case "%":
            r = c_mod(a, b)
        case "<<":
            if b < 0 or b > MAX_SHIFT:
                raise InvalidOperationError(f"invalid shift amount {b}")
            r = a << b
        case "==":
            r = int(a == b)
        case "!=":
            r = int(a != b)
        case "<":
            r = int(a < b)
        case ">":
            r = int(a > b)
        case "<=":
            r = int(a <= b)
        case ">=":
            r = int(a >= b)
        case "&&":
            r = int(bool(a) and bool(b))
        case "||":
            r = int(bool(a) or bool(b))
        case _:
            raise InvalidOperationError(f"unknown binary operator {op!r}")
    if r.bit_length() > MAX_VALUE_BITS:
        raise ValueOverflowError("integer value exceeds interpreter limit")
    return r


def eval_unary(op: str, a: int) -> int:
    match op:
        case "-":
            return -a
        case "!":
            return int(a == 0)
    raise InvalidOperationError(f"unknown unary operator {op!r}")


class TACInterpreter:
    def execute(self, program: TACProgram, inputs: dict[str, int] | None = None,
                max_steps: int = 10000) -> list[int]:
        instrs = program.instructions
        env: dict[str, int] = dict(inputs or {})
        outputs: list[int] = []

        label_map: dict[str, int] = {}
        for idx, ins in enumerate(instrs):
            if ins.op == TACOp.LABEL:
                label_map.setdefault(ins.label, idx)

        def value(operand: str) -> int:
            if is_literal(operand):
                return int(operand)
            try:
                return env[operand]
            except KeyError:
                raise UndefinedVariableError(f"read of undefined variable {operand!r}", outputs) from None

        def jump(label: str) -> int:
            try:
                return label_map[label]
            except KeyError:
                raise UnknownLabelError(f"jump to unknown label {label!r}", outputs) from None

        pc = 0
        steps = 0
        n = len(instrs)
        while pc < n:
            steps += 1
            if steps > max_steps:
                raise ExecutionTimeout(f"exceeded {max_steps} steps", outputs)
            ins = instrs[pc]
            next_pc = pc + 1
            try:
                match ins.op:
                    case TACOp.ASSIGN:
                        env[ins.result] = value(ins.arg1)
                    case TACOp.BINARY:
                        env[ins.result] = eval_binary(ins.operator, value(ins.arg1), value(ins.arg2))
                    case TACOp.UNARY:
                        env[ins.result] = eval_unary(ins.operator, value(ins.arg1))
                    case TACOp.LABEL | TACOp.NOP:
                        pass
                    case TACOp.GOTO:
                        next_pc = jump(ins.label)
                    case TACOp.IF_GOTO:
                        if value(ins.arg1) != 0:
                            next_pc = jump(ins.label)
                    case TACOp.IF_FALSE_GOTO:
                        if value(ins.arg1) == 0:
                            next_pc = jump(ins.label)
                    case TACOp.PRINT:
                        outputs.append(value(ins.arg1))
            except TACRuntimeError as exc:
                # attach the outputs produced before the failure
                exc.outputs = list(outputs)
                raise
            pc = next_pc
        return outputs
