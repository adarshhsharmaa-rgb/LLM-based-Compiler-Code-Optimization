"""Verification agent. A candidate is accepted only if BOTH checks pass.

1. Differential testing: run original and candidate on 20 random input sets plus
   5 edge-case sets (plus boundary values around every literal when there are
   free inputs) and compare printed output *and* failure mode (division by
   zero, timeout, ...). For a program with no free input variables there is
   exactly one possible execution, so a match is a proof of equivalence.

2. Symbolic verification (straight-line code only): evaluate both programs over
   symbolic inputs. ``+``, ``-``, ``*`` and constant shifts are normalised to
   canonical integer polynomials (so ``x*2`` == ``x+x`` and ``a+b`` == ``b+a``);
   other operators become canonicalised opaque terms. The sequence of printed
   expressions must match, and so must the set of divisors that could trap
   before each print.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..tac.instruction import TACOp, is_literal
from ..tac.interpreter import (
    ExecutionTimeout,
    TACInterpreter,
    TACRuntimeError,
    eval_binary,
    eval_unary,
)
from ..tac.program import TACProgram


@dataclass
class VerificationResult:
    passed: bool
    method: str
    reason: str
    details: dict | None = None


# ====================================================================== #
# Symbolic domain: canonical integer polynomials
# ====================================================================== #
# A Poly is a tuple of (monomial, coefficient) pairs sorted canonically, where a
# monomial is a sorted tuple of atoms. Atoms are ("v", name) for variables or
# ("f", op, args...) for opaque operations whose args are Polys.
Poly = tuple


def _canon(terms: dict) -> Poly:
    return tuple(sorted(((m, c) for m, c in terms.items() if c != 0), key=repr))


def p_const(c: int) -> Poly:
    return _canon({(): c})


def p_var(name: str) -> Poly:
    return _canon({(("v", name),): 1})


def p_atom(atom: tuple) -> Poly:
    return _canon({(atom,): 1})


def p_const_value(p: Poly) -> int | None:
    if not p:
        return 0
    if len(p) == 1 and p[0][0] == ():
        return p[0][1]
    return None


def p_add(p: Poly, q: Poly, sign: int = 1) -> Poly:
    terms: dict = {}
    for m, c in p:
        terms[m] = terms.get(m, 0) + c
    for m, c in q:
        terms[m] = terms.get(m, 0) + sign * c
    return _canon(terms)


def p_mul(p: Poly, q: Poly) -> Poly:
    terms: dict = {}
    for m1, c1 in p:
        for m2, c2 in q:
            m = tuple(sorted(m1 + m2, key=repr))
            terms[m] = terms.get(m, 0) + c1 * c2
    return _canon(terms)


def p_neg(p: Poly) -> Poly:
    return p_mul(p, p_const(-1))


def _sign_canonical(p: Poly) -> Poly:
    """Choose between p and -p deterministically (for == / != comparisons)."""
    n = p_neg(p)
    return min(p, n, key=repr)


def symbolic_binary(op: str, a: Poly, b: Poly) -> tuple[Poly, Poly | None]:
    """Returns (result, trap_divisor). trap_divisor is set for / and % whose
    divisor is not a known non-zero constant."""
    ca, cb = p_const_value(a), p_const_value(b)
    if ca is not None and cb is not None:
        try:
            return p_const(eval_binary(op, ca, cb)), None
        except TACRuntimeError:
            pass  # e.g. constant division by zero: keep it symbolic and record the trap
    match op:
        case "+":
            return p_add(a, b), None
        case "-":
            return p_add(a, b, -1), None
        case "*":
            return p_mul(a, b), None
        case "<<" if cb is not None and 0 <= cb <= 64:
            return p_mul(a, p_const(1 << cb)), None
        case "/" | "%":
            trap = None if (cb is not None and cb != 0) else _sign_canonical(b)
            if cb == 1:
                return (a if op == "/" else p_const(0)), None
            if cb == -1 and op == "%":
                return p_const(0), None
            if cb == -1 and op == "/":
                return p_neg(a), None
            return p_atom(("f", op, a, b)), trap
        case "<" | "<=":
            d = p_add(a, b, -1)
            dc = p_const_value(d)
            if dc is not None:
                return p_const(int(dc < 0 if op == "<" else dc <= 0)), None
            return p_atom(("f", op, d)), None
        case ">" | ">=":
            return symbolic_binary("<" if op == ">" else "<=", b, a)
        case "==" | "!=":
            d = p_add(a, b, -1)
            dc = p_const_value(d)
            if dc is not None:
                return p_const(int((dc == 0) == (op == "=="))), None
            return p_atom(("f", op, _sign_canonical(d))), None
        case "&&" | "||":
            x, y = sorted((a, b), key=repr)
            return p_atom(("f", op, x, y)), None
        case "<<":
            return p_atom(("f", op, a, b)), _sign_canonical(b)
    return p_atom(("f", op, a, b)), None


def symbolic_unary(op: str, a: Poly) -> Poly:
    ca = p_const_value(a)
    if ca is not None:
        return p_const(eval_unary(op, ca))
    if op == "-":
        return p_neg(a)
    return p_atom(("f", "==", _sign_canonical(a)))  # !x  ==  (x == 0)


def symbolic_trace(program: TACProgram) -> tuple[list[tuple[Poly, frozenset]], frozenset]:
    """Symbolically execute straight-line TAC.

    Returns ([(printed_expr, traps_before_print), ...], all_traps).
    """
    env: dict[str, Poly] = {}
    traps: set = set()
    events: list[tuple[Poly, frozenset]] = []

    def val(operand: str) -> Poly:
        if is_literal(operand):
            return p_const(int(operand))
        if operand not in env:
            env[operand] = p_var(operand)   # free input variable
        return env[operand]

    for ins in program.instructions:
        match ins.op:
            case TACOp.ASSIGN:
                env[ins.result] = val(ins.arg1)
            case TACOp.BINARY:
                res, trap = symbolic_binary(ins.operator, val(ins.arg1), val(ins.arg2))
                if trap is not None:
                    traps.add(trap)
                    if trap == p_const(0):
                        break  # division by a constant zero always traps: the rest is unreachable
                env[ins.result] = res
            case TACOp.UNARY:
                env[ins.result] = symbolic_unary(ins.operator, val(ins.arg1))
            case TACOp.PRINT:
                events.append((val(ins.arg1), frozenset(traps)))
            case TACOp.NOP:
                pass
            case _:
                raise ValueError("symbolic_trace only supports straight-line code")
    return events, frozenset(traps)


# ====================================================================== #
@dataclass
class _Outcome:
    outputs: tuple
    error: str | None = None
    timed_out: bool = False

    def describe(self) -> str:
        if self.timed_out:
            return f"timeout after printing {list(self.outputs)}"
        if self.error:
            return f"{self.error} after printing {list(self.outputs)}"
        return f"printed {list(self.outputs)}"


@dataclass
class Verifier:
    num_random: int = 20
    value_range: tuple[int, int] = (-100, 100)
    seed: int = 2024
    max_steps: int = 100_000
    max_boundary_constants: int = 15
    num_mixed: int = 10
    interpreter: TACInterpreter = field(default_factory=TACInterpreter)

    def verify(self, original: TACProgram, candidate: TACProgram) -> VerificationResult:
        # Run differential testing first (fast)
        diff_result = self._differential_test(original, candidate)
        if not diff_result.passed:
            return diff_result

        # Run symbolic verification second (more thorough)
        sym_result = self._symbolic_verify(original, candidate)
        if not sym_result.passed:
            return sym_result

        n = diff_result.details["tested"]
        if sym_result.details.get("skipped"):
            return VerificationResult(
                passed=True, method="differential",
                reason=f"differential: {n}/{n} inputs matched, symbolic: skipped (control flow)",
                details={"differential": diff_result.details, "symbolic": sym_result.details})
        return VerificationResult(
            passed=True, method="both",
            reason=f"differential: {n}/{n} inputs matched, symbolic: equivalent",
            details={"differential": diff_result.details, "symbolic": sym_result.details})

    # ------------------------------------------------------------------ #
    def input_sets(self, variables: list[str], constants: set[int] | None = None) -> list[dict[str, int]]:
        """20 random sets + 5 edge cases (all 0 / 1 / -1 / 99 / -99).

        When the programs have free inputs, boundary-value sets are added too:
        for every literal c in either program, all inputs = c-1, c, c+1, plus
        random mixes drawn from that pool. This catches off-by-one changes such
        as ``x > 5`` -> ``x >= 5`` that uniform random sampling would miss.
        """
        rng = random.Random(self.seed)
        lo, hi = self.value_range
        sets = [{v: rng.randint(lo, hi) for v in variables} for _ in range(self.num_random)]
        for edge in (0, 1, -1, 99, -99):
            sets.append({v: edge for v in variables})
        if variables and constants:
            pool = sorted({k for c in sorted(constants)[:self.max_boundary_constants]
                           for k in (c - 1, c, c + 1)})
            sets.extend({v: k for v in variables} for k in pool)
            if len(variables) > 1:
                sets.extend({v: rng.choice(pool) for v in variables} for _ in range(self.num_mixed))
        return sets

    @staticmethod
    def _constants(*programs: TACProgram) -> set[int]:
        found: set[int] = set()
        for prog in programs:
            for ins in prog.instructions:
                for field_name in ins.operand_fields():
                    value = getattr(ins, field_name)
                    if is_literal(value):
                        found.add(int(value))
        return found

    def _run(self, program: TACProgram, inputs: dict[str, int]) -> _Outcome:
        try:
            out = self.interpreter.execute(program, inputs, max_steps=self.max_steps)
            return _Outcome(tuple(out))
        except ExecutionTimeout as exc:
            return _Outcome(tuple(exc.outputs), "ExecutionTimeout", timed_out=True)
        except TACRuntimeError as exc:
            return _Outcome(tuple(exc.outputs), type(exc).__name__)

    def _differential_test(self, original: TACProgram, candidate: TACProgram) -> VerificationResult:
        variables = sorted(original.get_input_variables() | candidate.get_input_variables())
        sets = self.input_sets(variables, self._constants(original, candidate))
        cache: dict[tuple, tuple[_Outcome, _Outcome]] = {}
        for idx, inputs in enumerate(sets):
            key = tuple(sorted(inputs.items()))
            if key not in cache:
                cache[key] = (self._run(original, inputs), self._run(candidate, inputs))
            orig, cand = cache[key]
            if orig.timed_out and cand.timed_out:
                return VerificationResult(
                    False, "differential",
                    f"inconclusive: both programs exceeded {self.max_steps} steps on inputs {inputs}",
                    {"inputs": inputs, "test_index": idx, "tested": idx + 1})
            if orig != cand:
                return VerificationResult(
                    False, "differential",
                    f"output mismatch on inputs {inputs}: original {orig.describe()}, "
                    f"candidate {cand.describe()}",
                    {"inputs": inputs, "test_index": idx, "tested": idx + 1,
                     "original": orig.describe(), "candidate": cand.describe()})
        return VerificationResult(True, "differential", f"{len(sets)}/{len(sets)} inputs matched",
                                  {"tested": len(sets), "input_variables": variables,
                                   "distinct_executions": len(cache)})

    def _symbolic_verify(self, original: TACProgram, candidate: TACProgram) -> VerificationResult:
        if original.has_control_flow() or candidate.has_control_flow():
            return VerificationResult(True, "symbolic", "skipped: control flow present "
                                      "(differential testing only)", {"skipped": True})
        orig_events, orig_traps = symbolic_trace(original)
        cand_events, cand_traps = symbolic_trace(candidate)
        if len(orig_events) != len(cand_events):
            return VerificationResult(False, "symbolic",
                                      f"print count differs: {len(orig_events)} vs {len(cand_events)}",
                                      {"skipped": False})
        for k, ((pe, pt), (ce, ct)) in enumerate(zip(orig_events, cand_events)):
            if pe != ce:
                return VerificationResult(False, "symbolic",
                                          f"print #{k + 1} is not symbolically equivalent",
                                          {"skipped": False, "print_index": k})
            if pt != ct:
                return VerificationResult(False, "symbolic",
                                          f"possible division-by-zero behaviour differs before print #{k + 1}",
                                          {"skipped": False, "print_index": k})
        if orig_traps != cand_traps:
            return VerificationResult(False, "symbolic",
                                      "possible division-by-zero behaviour differs",
                                      {"skipped": False})
        return VerificationResult(True, "symbolic", "equivalent",
                                  {"skipped": False, "prints": len(orig_events)})
