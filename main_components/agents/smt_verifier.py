"""SMT verification: prove two loop-free TAC programs equivalent for every input, with Z3.

Differential testing shows that two programs agree on the inputs that were tried. For a
program without loops there are finitely many paths, so the whole behaviour can be written
as one formula over the inputs:

  * each path is followed symbolically; a branch splits it in two, and a division splits
    off the case "the divisor is zero", where the run stops with what it printed so far;
  * the paths of a program are folded into one description of a run:
    (how it ended, how many values it printed, the values);
  * Z3 is asked for inputs on which the two descriptions differ. "unsat" means there are
    none: the programs are equivalent for all inputs. "sat" comes with a counterexample.

Integers are unbounded, as in the reference interpreter, and ``/`` and ``%`` follow C.
Programs with loops are not handled here (``unsupported``): the verifier keeps testing
them. Z3 is optional; without the ``z3-solver`` package every call answers ``unsupported``.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..tac.instruction import TACOp, is_literal
from ..tac.interpreter import MAX_SHIFT
from ..tac.program import TACProgram

MAX_OUTCOMES = 256              # paths per program before giving up
KIND_OK, KIND_DIVISION, KIND_SHIFT = 0, 1, 2
_JUMPS = (TACOp.GOTO, TACOp.IF_GOTO, TACOp.IF_FALSE_GOTO)


@dataclass
class SmtResult:
    status: str                             # "proved", "refuted", "unknown" or "unsupported"
    reason: str = ""
    counterexample: dict[str, int] | None = None
    paths: int = 0                          # paths examined in the two programs together


class _Unsupported(Exception):
    pass


def z3_available() -> bool:
    try:
        import z3  # noqa: F401
    except ImportError:
        return False
    return True


def is_loop_free(program: TACProgram) -> bool:
    """True if every jump goes forward to a label that exists."""
    labels: dict[str, int] = {}
    for idx, ins in enumerate(program.instructions):
        if ins.op == TACOp.LABEL:
            labels.setdefault(ins.label, idx)
    return all(ins.label in labels and labels[ins.label] > idx
               for idx, ins in enumerate(program.instructions) if ins.op in _JUMPS)


def _outcomes(z3, program: TACProgram, input_var) -> list[tuple]:
    """Every way a run can end: (path condition, kind, printed values)."""
    if not is_loop_free(program):
        raise _Unsupported("the program has a loop")
    instrs = program.instructions
    labels: dict[str, int] = {}
    for idx, ins in enumerate(instrs):
        if ins.op == TACOp.LABEL:
            labels.setdefault(ins.label, idx)
    out: list[tuple] = []
    one, zero = z3.IntVal(1), z3.IntVal(0)

    def truth(cond):
        return z3.If(cond, one, zero)

    def trunc_div(a, b):
        quotient = z3.If(a >= 0, a, -a) / z3.If(b >= 0, b, -b)      # both operands non-negative here
        return z3.If((a >= 0) == (b >= 0), quotient, -quotient)

    def binary(op, a, b):
        match op:
            case "+":
                return a + b
            case "-":
                return a - b
            case "*":
                return a * b
            case "/":
                return trunc_div(a, b)
            case "%":
                return a - b * trunc_div(a, b)
            case "==":
                return truth(a == b)
            case "!=":
                return truth(a != b)
            case "<":
                return truth(a < b)
            case ">":
                return truth(a > b)
            case "<=":
                return truth(a <= b)
            case ">=":
                return truth(a >= b)
            case "&&":
                return truth(z3.And(a != 0, b != 0))
            case "||":
                return truth(z3.Or(a != 0, b != 0))
        raise _Unsupported(f"operator {op}")

    def emit(cond, kind, prints):
        out.append((cond, kind, list(prints)))
        if len(out) > MAX_OUTCOMES:
            raise _Unsupported(f"more than {MAX_OUTCOMES} paths")

    def run(pc, env, cond, prints):
        def val(operand):
            if is_literal(operand):
                return z3.IntVal(int(operand))
            if operand not in env:              # read before written: a program input
                env[operand] = input_var(operand)
            return env[operand]

        while pc < len(instrs):
            ins = instrs[pc]
            nxt = pc + 1
            match ins.op:
                case TACOp.ASSIGN:
                    env[ins.result] = val(ins.arg1)
                case TACOp.BINARY:
                    a, b = val(ins.arg1), val(ins.arg2)
                    if ins.operator in ("/", "%"):
                        divisor_zero = z3.simplify(b == 0)
                        if not z3.is_false(divisor_zero):
                            emit(z3.And(cond, divisor_zero), KIND_DIVISION, prints)
                            if z3.is_true(divisor_zero):
                                return
                            cond = z3.And(cond, z3.Not(divisor_zero))
                    if ins.operator == "<<":
                        if not is_literal(ins.arg2):
                            raise _Unsupported("shift by a variable")
                        amount = int(ins.arg2)
                        if amount < 0 or amount > MAX_SHIFT:
                            emit(cond, KIND_SHIFT, prints)
                            return
                        env[ins.result] = a * (1 << amount)
                    else:
                        env[ins.result] = binary(ins.operator, a, b)
                case TACOp.UNARY:
                    a = val(ins.arg1)
                    if ins.operator == "-":
                        env[ins.result] = -a
                    elif ins.operator == "!":
                        env[ins.result] = truth(a == 0)
                    else:
                        raise _Unsupported(f"operator {ins.operator}")
                case TACOp.PRINT:
                    prints = prints + [val(ins.arg1)]
                case TACOp.GOTO:
                    nxt = labels[ins.label]
                case TACOp.IF_GOTO | TACOp.IF_FALSE_GOTO:
                    nonzero = val(ins.arg1) != 0
                    taken = z3.simplify(nonzero if ins.op == TACOp.IF_GOTO else z3.Not(nonzero))
                    if z3.is_true(taken):
                        nxt = labels[ins.label]
                    elif not z3.is_false(taken):
                        run(labels[ins.label], dict(env), z3.And(cond, taken), prints)
                        cond = z3.And(cond, z3.Not(taken))
            pc = nxt
        emit(cond, KIND_OK, prints)

    run(0, {}, z3.BoolVal(True), [])
    return out


def smt_equivalent(original: TACProgram, candidate: TACProgram, timeout_ms: int = 3000) -> SmtResult:
    """Ask Z3 whether any input makes the two programs behave differently."""
    try:
        import z3
    except ImportError:
        return SmtResult("unsupported", "the z3-solver package is not installed")
    inputs: dict[str, object] = {}

    def input_var(name: str):
        return inputs.setdefault(name, z3.Int(name))

    try:
        runs_a = _outcomes(z3, original, input_var)
        runs_b = _outcomes(z3, candidate, input_var)
    except _Unsupported as exc:
        return SmtResult("unsupported", str(exc))
    except RecursionError:
        return SmtResult("unsupported", "branches nested too deeply")
    paths = len(runs_a) + len(runs_b)
    width = max(len(prints) for _, _, prints in runs_a + runs_b)

    def describe(runs):
        """(kind, number of prints, values...) of a run, as one expression per field.

        The path conditions of a program are exhaustive and exclusive, so the last path
        can serve as the "otherwise" case."""
        fields = None
        for cond, kind, prints in reversed(runs):
            row = [z3.IntVal(kind), z3.IntVal(len(prints)), *prints, *[z3.IntVal(0)] * (width - len(prints))]
            fields = row if fields is None else [z3.If(cond, r, f) for r, f in zip(row, fields)]
        return fields

    solver = z3.Solver()
    solver.set("timeout", timeout_ms)
    solver.add(z3.Or(*[x != y for x, y in zip(describe(runs_a), describe(runs_b))]))
    answer = solver.check()
    if answer == z3.unsat:
        return SmtResult("proved", f"no input tells them apart ({paths} paths)", paths=paths)
    if answer == z3.sat:
        model = solver.model()
        example = {name: model.eval(var, model_completion=True).as_long() for name, var in sorted(inputs.items())}
        return SmtResult("refuted", "Z3 found inputs on which they differ", example, paths)
    return SmtResult("unknown", f"Z3 gave no answer within {timeout_ms} ms", paths=paths)
