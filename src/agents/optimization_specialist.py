"""Optimization Specialist: proposes one candidate transformation per request.

It owns both ways of producing a proposal and routes every request to one of
them:

  * Option A, rule-based -- apply the highest-priority opportunity reported by
    the Code Analysis Specialist. Deterministic, instant, always available.
  * Option B, LLM-based  -- send the TAC to a language model and ask for one
    semantics-preserving optimization. The model is a cloud one, or a local
    Ollama model when offline (see ``optimizer_llm.py``).

The routing policy is the ``mode``:

  ``rule``    always Option A.
  ``hybrid``  Option A first; Option B when the rule proposal for this step was
              turned down, or when the rules have nothing left to try.
  ``llm``     Option B first; Option A when the LLM cannot be used (not
              running, call budget used up) or its proposal was turned down.

With no LLM attached every mode routes to the rules, so the program is always
optimized. Whatever the route, a proposal is only a suggestion: the
Orchestrator still sends it through the Verification Module and the Cost
Evaluator.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..tac.instruction import TACOp, is_literal
from ..tac.program import TACProgram
from .code_analyzer import Opportunity
from .optimizer_rule import RuleBasedOptimizer

MODES = ("rule", "llm", "hybrid")
DEFAULT_MODE = "hybrid"
MODE_SUMMARIES = {
    "rule": "rule-based only",
    "hybrid": "rules first, the LLM when they are turned down or run out",
    "llm": "LLM first, the rules when it is turned down or unavailable",
}


class Route(Enum):
    RULE = "rule"
    LLM = "llm"


@dataclass
class RoutingDecision:
    route: Route | None        # None: nobody can propose anything (more) for this step
    reason: str
    llm_note: str = ""         # why the LLM was passed over, if it was


@dataclass
class Proposal:
    source: str                             # "rule" or "llm"
    type: str                               # the opportunity type, or "LLM"
    candidate: TACProgram | None            # None: the LLM returned no usable TAC
    reasoning: str
    opportunity: Opportunity | None = None  # set for rule-based proposals


def is_provably_minimal(program: TACProgram) -> bool:
    """True if the program is nothing but ``print <constant>`` lines.

    Every print must stay (it is observable output) and nothing else is
    left, so no optimizer can lower the cost -- asking the LLM would only
    waste a call.
    """
    return all(ins.op == TACOp.PRINT and is_literal(ins.arg1) for ins in program.instructions)


class OptimizationSpecialist:
    def __init__(self, mode: str = DEFAULT_MODE, llm_optimizer=None, max_llm_calls: int = 5):
        if mode not in MODES:
            raise ValueError(f"unknown optimizer mode {mode!r}; choose from {list(MODES)}")
        self.mode = mode
        self.rule_optimizer = RuleBasedOptimizer()
        self.llm_optimizer = llm_optimizer
        self.max_llm_calls = max_llm_calls

    @property
    def llm_attached(self) -> bool:
        """True if there is a real routing choice to make."""
        return self.llm_optimizer is not None and self.mode != "rule"

    def route_label(self, route: Route) -> str:
        if route is Route.RULE:
            return "Rule-based optimizer"
        name = getattr(self.llm_optimizer, "label", "")
        return f"LLM optimizer ({name})" if name else "LLM optimizer"

    # ------------------------------------------------------------------ #
    def route(self, program: TACProgram, opportunities: list[Opportunity], llm_calls: int = 0,
              tried: tuple | list = ()) -> RoutingDecision:
        """Decide who proposes next for ``program``.

        ``opportunities`` are the analyzer's findings that are still worth
        trying, ``llm_calls`` is how many LLM requests this program has used,
        and ``tried`` lists the routes whose proposal was already turned down
        in the current step.
        """
        order = [Route.RULE, Route.LLM] if self.mode != "llm" else [Route.LLM, Route.RULE]
        if not self.llm_attached:
            order = [Route.RULE]
        passed_over: list[str] = []
        llm_note = ""
        for route in order:
            if route in tried:
                name = "rule-based" if route is Route.RULE else "LLM"
                passed_over.append(f"the {name} proposal was turned down")
            elif route is Route.RULE and not opportunities:
                passed_over.append("the rules have nothing left to try")
            elif route is Route.LLM and (llm_note := self._llm_blocker(program, llm_calls)):
                passed_over.append(f"LLM not used, {llm_note}")
            else:
                return RoutingDecision(route, self._reason(route, opportunities, passed_over), llm_note)
        return RoutingDecision(None, "; ".join(passed_over), llm_note)

    def _llm_blocker(self, program: TACProgram, llm_calls: int) -> str:
        """Why the LLM cannot be asked right now ('' if it can)."""
        llm = self.llm_optimizer
        if not llm.available:
            reason = getattr(llm, "unavailable_reason", "")
            return f"unavailable ({reason})" if reason else "unavailable"
        if llm_calls >= self.max_llm_calls:
            return f"call budget used up ({self.max_llm_calls} per program)"
        if is_provably_minimal(program):
            return "program is only constant prints (provably minimal)"
        return ""

    @staticmethod
    def _reason(route: Route, opportunities: list[Opportunity], passed_over: list[str]) -> str:
        if passed_over:
            return "; ".join(passed_over)
        if route is Route.LLM:
            return "LLM-first mode"
        best = opportunities[0]
        return f"highest-priority opportunity is {best.type.value} (priority {best.priority})"

    # ------------------------------------------------------------------ #
    def propose(self, program: TACProgram, decision: RoutingDecision,
                opportunities: list[Opportunity]) -> Proposal:
        """Produce the candidate for a routing decision (the program is never modified)."""
        if decision.route is Route.RULE:
            opportunity = opportunities[0]      # the analyzer ranks them, best first
            candidate = self.rule_optimizer.propose(program, opportunity)
            return Proposal("rule", opportunity.type.value, candidate, opportunity.description, opportunity)
        candidate, reasoning = self.llm_optimizer.propose(program)
        return Proposal("llm", "LLM", candidate, reasoning)
