"""Code Analyzer agent: finds optimisation opportunities in a TAC program.

All detections are backed by dataflow analyses over the instruction-level CFG
(see ``src/tac/dataflow.py``), so they are sound for programs with branches
and loops, not just straight-line code.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..tac import dataflow
from ..tac.instruction import (
    ARITHMETIC_OPS,
    COMMUTATIVE_OPS,
    TACInstruction,
    TACOp,
    is_literal,
    is_variable,
)
from ..tac.interpreter import TACRuntimeError, eval_binary, eval_unary
from ..tac.program import TACProgram


class OpportunityType(Enum):
    CONSTANT_FOLD = "CONSTANT_FOLD"
    ALGEBRAIC_SIMPLIFY = "ALGEBRAIC_SIMPLIFY"
    DEAD_CODE = "DEAD_CODE"
    CSE = "CSE"
    STRENGTH_REDUCTION = "STRENGTH_REDUCTION"
    COPY_PROPAGATION = "COPY_PROPAGATION"


PRIORITIES = {
    OpportunityType.CONSTANT_FOLD: 100,
    OpportunityType.ALGEBRAIC_SIMPLIFY: 90,
    OpportunityType.DEAD_CODE: 80,
    OpportunityType.CSE: 70,
    OpportunityType.STRENGTH_REDUCTION: 60,
    OpportunityType.COPY_PROPAGATION: 50,
}


@dataclass
class Opportunity:
    type: OpportunityType
    priority: int
    location: int          # instruction index
    description: str
    details: dict = field(default_factory=dict)


def may_trap(ins: TACInstruction) -> bool:
    """True if executing ``ins`` might raise at runtime (so it must not be deleted)."""
    if ins.op != TACOp.BINARY:
        return False
    if ins.operator in ("/", "%"):
        return not (is_literal(ins.arg2) and int(ins.arg2) != 0)
    if ins.operator == "<<":
        return not (is_literal(ins.arg2) and 0 <= int(ins.arg2) <= 64)
    return False


def _make(otype: OpportunityType, location: int, description: str, **details) -> Opportunity:
    return Opportunity(otype, PRIORITIES[otype], location, description, details)


class CodeAnalyzer:
    def analyze(self, program: TACProgram) -> list[Opportunity]:
        instrs = program.instructions
        if not instrs:
            return []
        _, live_out = dataflow.liveness(instrs)
        opportunities: list[Opportunity] = []
        opportunities += self._constant_folding(instrs)
        opportunities += self._algebraic(instrs)
        opportunities += self._dead_code(instrs, live_out)
        opportunities += self._cse(instrs)
        opportunities += self._strength_reduction(instrs)
        opportunities += self._copy_propagation(instrs, live_out)
        opportunities.sort(key=lambda o: (-o.priority, o.location, o.description))
        return opportunities

    # ------------------------------------------------------------------ #
    def _constant_folding(self, instrs: list[TACInstruction]) -> list[Opportunity]:
        out = []
        for i, ins in enumerate(instrs):
            try:
                if ins.op == TACOp.BINARY and is_literal(ins.arg1) and is_literal(ins.arg2):
                    value = eval_binary(ins.operator, int(ins.arg1), int(ins.arg2))
                elif ins.op == TACOp.UNARY and is_literal(ins.arg1):
                    value = eval_unary(ins.operator, int(ins.arg1))
                else:
                    continue
            except TACRuntimeError:
                continue  # e.g. 5 / 0 -- folding would hide the runtime error
            # Folding a comparison/logical/shift/unary op into a copy would *raise*
            # the weighted cost (copies are dearer than non-arithmetic ops), so those
            # folds also forward the constant into its uses in the same step.
            forward = not (ins.op == TACOp.BINARY and ins.operator in ARITHMETIC_OPS)
            after = f"{ins.result} = {value}" + (f" (forwarded into uses of {ins.result})" if forward else "")
            out.append(_make(OpportunityType.CONSTANT_FOLD, i,
                             f"Fold {ins.to_string()} -> {after}",
                             value=str(value), forward=forward, before=ins.to_string(), after=after))
        return out

    def _algebraic(self, instrs: list[TACInstruction]) -> list[Opportunity]:
        out = []
        for i, ins in enumerate(instrs):
            if ins.op != TACOp.BINARY:
                continue
            a, b, op = ins.arg1, ins.arg2, ins.operator
            if is_literal(a) and is_literal(b):
                continue  # constant folding handles it
            replacement = None
            rule = ""
            if op == "+" and b == "0":
                replacement, rule = a, "x + 0 = x"
            elif op == "+" and a == "0":
                replacement, rule = b, "0 + x = x"
            elif op == "-" and b == "0":
                replacement, rule = a, "x - 0 = x"
            elif op == "-" and a == b:
                replacement, rule = "0", "x - x = 0"
            elif op == "*" and b == "1":
                replacement, rule = a, "x * 1 = x"
            elif op == "*" and a == "1":
                replacement, rule = b, "1 * x = x"
            elif op == "*" and (a == "0" or b == "0"):
                replacement, rule = "0", "x * 0 = 0"
            elif op == "/" and b == "1":
                replacement, rule = a, "x / 1 = x"
            elif op == "%" and b == "1":
                replacement, rule = "0", "x % 1 = 0"
            if replacement is None:
                continue
            after = f"{ins.result} = {replacement}"
            out.append(_make(OpportunityType.ALGEBRAIC_SIMPLIFY, i,
                             f"Simplify {ins.to_string()} -> {after} ({rule})",
                             replacement=replacement, rule=rule,
                             before=ins.to_string(), after=after))
        return out

    def _dead_code(self, instrs: list[TACInstruction], live_out: list[set[str]]) -> list[Opportunity]:
        out = []
        for i, ins in enumerate(instrs):
            d = ins.defined_var()
            if d is None:
                continue
            if ins.op == TACOp.ASSIGN and ins.arg1 == d:
                reason = "self-assignment has no effect"
            elif d not in live_out[i] and not may_trap(ins):
                reason = f"'{d}' is never read afterwards"
            else:
                continue
            out.append(_make(OpportunityType.DEAD_CODE, i,
                             f"Remove dead {ins.to_string()} ({reason})",
                             var=d, reason=reason, before=ins.to_string(), after="(removed)"))
        return out

    def _cse(self, instrs: list[TACInstruction]) -> list[Opportunity]:
        """Local (per basic block) available-expression analysis."""
        out = []
        for start, end in dataflow.basic_blocks(instrs):
            available: dict[tuple[str, str, str], tuple[int, str]] = {}
            for i in range(start, end):
                ins = instrs[i]
                key = None
                if ins.op == TACOp.BINARY:
                    a, b = ins.arg1, ins.arg2
                    if ins.operator in COMMUTATIVE_OPS and b < a:
                        a, b = b, a
                    key = (ins.operator, a, b)
                    if key in available:
                        first_idx, source = available[key]
                        if source != ins.result:
                            after = f"{ins.result} = {source}"
                            out.append(_make(OpportunityType.CSE, i,
                                             f"Reuse {source} (instr {first_idx}) for {ins.to_string()}",
                                             source=source, first=first_idx,
                                             before=ins.to_string(), after=after))
                d = ins.defined_var()
                if d is not None:
                    available = {k: v for k, v in available.items()
                                 if d not in (k[1], k[2]) and v[1] != d}
                    if key is not None and key not in available and d not in (key[1], key[2]):
                        available[key] = (i, d)
        return out

    def _strength_reduction(self, instrs: list[TACInstruction]) -> list[Opportunity]:
        out = []
        for i, ins in enumerate(instrs):
            if ins.op != TACOp.BINARY or ins.operator != "*":
                continue
            if is_literal(ins.arg2) and is_variable(ins.arg1):
                var, const = ins.arg1, int(ins.arg2)
            elif is_literal(ins.arg1) and is_variable(ins.arg2):
                var, const = ins.arg2, int(ins.arg1)
            else:
                continue
            if const < 2 or const & (const - 1):
                continue
            k = const.bit_length() - 1
            if k == 1:
                new = {"operator": "+", "arg1": var, "arg2": var}
                after = f"{ins.result} = {var} + {var}"
            else:
                new = {"operator": "<<", "arg1": var, "arg2": str(k)}
                after = f"{ins.result} = {var} << {k}"
            out.append(_make(OpportunityType.STRENGTH_REDUCTION, i,
                             f"Reduce {ins.to_string()} -> {after}",
                             before=ins.to_string(), after=after, **new))
        return out

    def _copy_propagation(self, instrs: list[TACInstruction],
                          live_out: list[set[str]]) -> list[Opportunity]:
        out = []
        avail_in = dataflow.available_copies(instrs)
        seen_pairs: set[tuple[str, str]] = set()
        for i, ins in enumerate(instrs):
            if ins.op != TACOp.ASSIGN or ins.result == ins.arg1:
                continue
            pair = (ins.result, ins.arg1)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            x, y = pair
            sites = []
            for j, other in enumerate(instrs):
                if pair not in avail_in[j]:
                    continue
                for field_name in other.operand_fields():
                    if getattr(other, field_name) == x:
                        sites.append([j, field_name])
            if not sites:
                continue
            out.append(_make(OpportunityType.COPY_PROPAGATION, i,
                             f"Propagate {x} = {y} into {len(sites)} use(s)",
                             mode="propagate", var=x, value=y, sites=sites,
                             before=ins.to_string(),
                             after=f"uses of {x} -> {y} at instr {', '.join(str(s[0]) for s in sites)}"))

        # Copy coalescing: "T = a op b; x = T" with T dead afterwards -> "x = a op b".
        for i in range(len(instrs) - 1):
            first, second = instrs[i], instrs[i + 1]
            if (first.op in (TACOp.BINARY, TACOp.UNARY)
                    and second.op == TACOp.ASSIGN
                    and second.arg1 == first.result
                    and second.result != first.result
                    and first.result not in live_out[i + 1]):
                x = second.result
                coalesced = TACInstruction(first.op, result=x, arg1=first.arg1,
                                           arg2=first.arg2, operator=first.operator)
                out.append(_make(OpportunityType.COPY_PROPAGATION, i + 1,
                                 f"Coalesce {first.to_string()}; {second.to_string()} -> {coalesced.to_string()}",
                                 mode="coalesce", def_index=i, var=x, temp=first.result,
                                 before=f"{first.to_string()}; {second.to_string()}",
                                 after=coalesced.to_string()))
        return out
