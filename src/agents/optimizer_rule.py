"""Rule-based optimizer agent: applies one Opportunity to a copy of the program.

Every method works on a deep copy and returns it. If the opportunity no longer
matches the program (stale location), the copy is returned unchanged and the
cost evaluator will reject it as "no improvement".
"""
from __future__ import annotations

from ..tac import dataflow
from ..tac.instruction import TACInstruction, TACOp, is_literal
from ..tac.interpreter import TACRuntimeError, eval_binary, eval_unary
from ..tac.program import TACProgram
from .code_analyzer import Opportunity, OpportunityType, may_trap


def _forward_copy(instrs: list[TACInstruction], loc: int) -> None:
    """Replace uses of the copy ``x = y`` at ``loc`` wherever it is available,
    then delete the copy if ``x`` is no longer live after it."""
    copy_ins = instrs[loc]
    pair = (copy_ins.result, copy_ins.arg1)
    avail_in = dataflow.available_copies(instrs)
    for j, other in enumerate(instrs):
        if pair in avail_in[j]:
            for field_name in other.operand_fields():
                if getattr(other, field_name) == pair[0]:
                    setattr(other, field_name, pair[1])
    _, live_out = dataflow.liveness(instrs)
    if pair[0] not in live_out[loc]:
        del instrs[loc]


class RuleBasedOptimizer:
    def propose(self, program: TACProgram, opportunity: Opportunity) -> TACProgram:
        new_prog = program.copy()  # ALWAYS deep copy
        if not 0 <= opportunity.location < len(new_prog):
            return new_prog
        match opportunity.type:
            case OpportunityType.CONSTANT_FOLD:
                return self._apply_constant_fold(new_prog, opportunity)
            case OpportunityType.ALGEBRAIC_SIMPLIFY:
                return self._apply_algebraic_simplify(new_prog, opportunity)
            case OpportunityType.DEAD_CODE:
                return self._apply_dead_code_elim(new_prog, opportunity)
            case OpportunityType.CSE:
                return self._apply_cse(new_prog, opportunity)
            case OpportunityType.STRENGTH_REDUCTION:
                return self._apply_strength_reduction(new_prog, opportunity)
            case OpportunityType.COPY_PROPAGATION:
                return self._apply_copy_propagation(new_prog, opportunity)
        return new_prog

    # ------------------------------------------------------------------ #
    def _apply_constant_fold(self, prog: TACProgram, opp: Opportunity) -> TACProgram:
        ins = prog.instructions[opp.location]
        try:
            if ins.op == TACOp.BINARY and is_literal(ins.arg1) and is_literal(ins.arg2):
                value = eval_binary(ins.operator, int(ins.arg1), int(ins.arg2))
            elif ins.op == TACOp.UNARY and is_literal(ins.arg1):
                value = eval_unary(ins.operator, int(ins.arg1))
            else:
                return prog
        except TACRuntimeError:
            return prog
        prog.instructions[opp.location] = TACInstruction(TACOp.ASSIGN, result=ins.result, arg1=str(value))
        if opp.details.get("forward"):
            _forward_copy(prog.instructions, opp.location)
        return prog

    def _apply_algebraic_simplify(self, prog: TACProgram, opp: Opportunity) -> TACProgram:
        ins = prog.instructions[opp.location]
        if ins.op != TACOp.BINARY or opp.details.get("before") != ins.to_string():
            return prog
        prog.instructions[opp.location] = TACInstruction(
            TACOp.ASSIGN, result=ins.result, arg1=opp.details["replacement"])
        return prog

    def _apply_dead_code_elim(self, prog: TACProgram, opp: Opportunity) -> TACProgram:
        ins = prog.instructions[opp.location]
        if ins.defined_var() is None or ins.defined_var() != opp.details.get("var") or may_trap(ins):
            return prog
        del prog.instructions[opp.location]
        return prog

    def _apply_cse(self, prog: TACProgram, opp: Opportunity) -> TACProgram:
        ins = prog.instructions[opp.location]
        if ins.op != TACOp.BINARY:
            return prog
        prog.instructions[opp.location] = TACInstruction(
            TACOp.ASSIGN, result=ins.result, arg1=opp.details["source"])
        return prog

    def _apply_strength_reduction(self, prog: TACProgram, opp: Opportunity) -> TACProgram:
        ins = prog.instructions[opp.location]
        if ins.op != TACOp.BINARY or ins.operator != "*":
            return prog
        prog.instructions[opp.location] = TACInstruction(
            TACOp.BINARY, result=ins.result, arg1=opp.details["arg1"],
            operator=opp.details["operator"], arg2=opp.details["arg2"])
        return prog

    def _apply_copy_propagation(self, prog: TACProgram, opp: Opportunity) -> TACProgram:
        instrs = prog.instructions
        if opp.details.get("mode") == "coalesce":
            def_idx = opp.details["def_index"]
            first, second = instrs[def_idx], instrs[opp.location]
            if (def_idx + 1 != opp.location or second.op != TACOp.ASSIGN
                    or second.arg1 != first.result or first.result != opp.details["temp"]):
                return prog
            first.result = second.result
            del instrs[opp.location]
            return prog

        x, y = opp.details["var"], opp.details["value"]
        copy_ins = instrs[opp.location]
        if copy_ins.op != TACOp.ASSIGN or copy_ins.result != x or copy_ins.arg1 != y:
            return prog
        for j, field_name in opp.details["sites"]:
            if getattr(instrs[j], field_name) == x:
                setattr(instrs[j], field_name, y)
        # The copy itself is now often dead; remove it in the same step so the
        # transformation is a measurable improvement on its own.
        _, live_out = dataflow.liveness(instrs)
        if x not in live_out[opp.location]:
            del instrs[opp.location]
        return prog
