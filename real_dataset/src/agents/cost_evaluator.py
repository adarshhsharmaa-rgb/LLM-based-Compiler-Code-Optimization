"""Cost Evaluator agent: static cost of a TAC program, plus its execution time.

The static cost is a weighted count of what the program text contains. The execution time
is measured by running the program: every executed instruction adds its latency
(``LATENCY``), and the figure is the average over a fixed set of inputs. Work inside a loop
therefore counts once per iteration, and a multiplication counts for more than the shift
that replaces it; the static cost can see neither.

``model`` decides what "cheaper" means when a proposal is judged:

  ``static``  a lower static cost (the default; the Review 2 results use it)
  ``time``    a lower execution time, or the same time and a lower static cost
"""
from __future__ import annotations

import random
from dataclasses import asdict, dataclass

from ..tac.instruction import ARITHMETIC_OPS, JUMP_OPS, TACInstruction, TACOp, is_temp
from ..tac.interpreter import TACInterpreter, TACRuntimeError
from ..tac.program import TACProgram

COST_MODELS = ("static", "time")

# Abstract machine cycles per executed instruction (typical x86-64 latencies, rounded).
LATENCY = {
    "copy": 1.0,        # x = y, x = 5
    "simple": 1.0,      # + - << comparisons logical operators, unary - and !
    "multiply": 3.0,
    "divide": 20.0,     # / and %
    "jump": 1.0,        # goto
    "branch": 2.0,      # if / ifFalse
    "print": 1.0,
}
PROFILE_RANDOM_RUNS = 20
PROFILE_EDGES = (0, 1, -1, 99, -99)
PROFILE_SEED = 2024
_TIME_EPS = 1e-9


def instruction_latency(ins: TACInstruction) -> float:
    match ins.op:
        case TACOp.ASSIGN:
            return LATENCY["copy"]
        case TACOp.BINARY:
            if ins.operator == "*":
                return LATENCY["multiply"]
            return LATENCY["divide"] if ins.operator in ("/", "%") else LATENCY["simple"]
        case TACOp.UNARY:
            return LATENCY["simple"]
        case TACOp.GOTO:
            return LATENCY["jump"]
        case TACOp.IF_GOTO | TACOp.IF_FALSE_GOTO:
            return LATENCY["branch"]
        case TACOp.PRINT:
            return LATENCY["print"]
    return 0.0          # labels and nops take no time


def profile_inputs(variables: list[str]) -> list[dict[str, int]]:
    """The inputs every program is timed on: 20 random sets and 5 edge cases.

    A variable's values depend only on its name, so a program and a candidate that reads
    fewer inputs are still timed on the same values. Half of the random sets are positive,
    since sizes and counts usually are.
    """
    if not variables:
        return [{}]
    sets = []
    for k in range(PROFILE_RANDOM_RUNS):
        lo = 1 if k % 2 else -100
        sets.append({v: random.Random(f"{PROFILE_SEED}/{k}/{v}").randint(lo, 100) for v in variables})
    sets.extend({v: edge for v in variables} for edge in PROFILE_EDGES)
    return sets


@dataclass
class CostBreakdown:
    instruction_count: int
    arithmetic_ops: int       # BINARY instructions with +, -, *, /, %
    temp_vars: int            # count of distinct t0, t1, ... variables
    memory_ops: int           # ASSIGN (copy) instructions
    branch_ops: int           # GOTO, IF_GOTO, IF_FALSE_GOTO
    weighted_total: float     # the static cost
    exec_time: float = 0.0    # average cycles per run over the profile inputs

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

    def __init__(self, model: str = "static", max_steps: int = 100_000):
        if model not in COST_MODELS:
            raise ValueError(f"unknown cost model {model!r}; choose from {list(COST_MODELS)}")
        self.model = model
        self.max_steps = max_steps
        self.interpreter = TACInterpreter()
        self._timed: dict[str, float] = {}      # program text -> execution time (the loop re-asks)

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
        return CostBreakdown(**counts, weighted_total=round(weighted, 4), exec_time=self.execution_time(program))

    def execution_time(self, program: TACProgram) -> float:
        """Average cycles one run takes, over the profile inputs."""
        key = program.to_string()
        if key not in self._timed:
            if len(self._timed) > 64:
                self._timed.clear()
            latency = [instruction_latency(ins) for ins in program.instructions]
            sets = profile_inputs(sorted(program.get_input_variables()))
            total = 0.0
            for inputs in sets:
                counts = [0] * len(latency)
                try:
                    self.interpreter.execute(program, inputs, max_steps=self.max_steps, counts=counts)
                except TACRuntimeError:
                    pass                    # a run that stops early still took the time it ran
                total += sum(c * cycles for c, cycles in zip(counts, latency))
            self._timed[key] = round(total / len(sets), 4)
        return self._timed[key]

    def is_improvement(self, old: CostBreakdown, new: CostBreakdown) -> bool:
        if self.model == "time":
            if abs(new.exec_time - old.exec_time) > _TIME_EPS:
                return new.exec_time < old.exec_time
        return new.weighted_total < old.weighted_total

    def reduction_percentage(self, old: CostBreakdown, new: CostBreakdown) -> float:
        if old.weighted_total == 0:
            return 0.0
        return (old.weighted_total - new.weighted_total) / old.weighted_total * 100

    def time_reduction_percentage(self, old: CostBreakdown, new: CostBreakdown) -> float:
        if old.exec_time == 0:
            return 0.0
        return (old.exec_time - new.exec_time) / old.exec_time * 100
