"""Cost Evaluator agent: weighted static cost of a TAC program."""
from __future__ import annotations

from dataclasses import asdict, dataclass

from ..tac.instruction import ARITHMETIC_OPS, JUMP_OPS, TACOp, is_temp
from ..tac.program import TACProgram


@dataclass
class CostBreakdown:
    instruction_count: int
    arithmetic_ops: int       # BINARY instructions with +, -, *, /, %
    temp_vars: int            # count of distinct t0, t1, ... variables
    memory_ops: int           # ASSIGN (copy) instructions
    branch_ops: int           # GOTO, IF_GOTO, IF_FALSE_GOTO
    weighted_total: float

    def to_dict(self) -> dict:
        return asdict(self)


class CostEvaluator:
    WEIGHTS = {
        "instruction_count": 1.0,
        "arithmetic_ops": 2.0,
        "temp_vars": 0.5,
        "memory_ops": 1.5,
        "branch_ops": 1.0,
    }

    def evaluate(self, program: TACProgram) -> CostBreakdown:
        instruction_count = len(program)
        arithmetic_ops = 0
        memory_ops = 0
        branch_ops = 0
        temps: set[str] = set()
        for ins in program.instructions:
            if ins.op == TACOp.BINARY and ins.operator in ARITHMETIC_OPS:
                arithmetic_ops += 1
            elif ins.op == TACOp.ASSIGN:
                memory_ops += 1
            elif ins.op in JUMP_OPS:
                branch_ops += 1
            for name in (ins.defined_var(), *ins.used_vars()):
                if is_temp(name):
                    temps.add(name)
        counts = {
            "instruction_count": instruction_count,
            "arithmetic_ops": arithmetic_ops,
            "temp_vars": len(temps),
            "memory_ops": memory_ops,
            "branch_ops": branch_ops,
        }
        weighted = sum(counts[k] * w for k, w in self.WEIGHTS.items())
        return CostBreakdown(**counts, weighted_total=round(weighted, 4))

    def is_improvement(self, old: CostBreakdown, new: CostBreakdown) -> bool:
        return new.weighted_total < old.weighted_total

    def reduction_percentage(self, old: CostBreakdown, new: CostBreakdown) -> float:
        if old.weighted_total == 0:
            return 0.0
        return (old.weighted_total - new.weighted_total) / old.weighted_total * 100
