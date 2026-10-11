"""Orchestrator: drives the Analyze -> Propose -> Verify -> Evaluate -> Accept/Reject loop."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from ..tac.printer import format_tac
from ..tac.program import TACProgram
from .code_analyzer import CodeAnalyzer, Opportunity
from .cost_evaluator import CostBreakdown, CostEvaluator
from .decision_log import DecisionLogger
from .optimization_specialist import (
    DEFAULT_MODE,
    OptimizationSpecialist,
    Proposal,
    Route,
    is_provably_minimal,
)
from .optimizer_llm import DEFAULT_PROVIDER, create_llm_optimizer
from .verifier import Verifier


@dataclass
class OptimizationResult:
    program_name: str
    original_tac: TACProgram
    optimized_tac: TACProgram
    original_cost: CostBreakdown
    final_cost: CostBreakdown
    cost_reduction_pct: float
    iterations: int
    accepted_count: int
    rejected_count: int
    invalid_count: int
    optimization_types_applied: list[str]
    log: DecisionLogger
    output_match: bool         # True if optimized produces same output as original
    # For LLM tracking:
    llm_proposals: int
    llm_valid: int
    # One record per proposal: {"iteration", "source", "type", "outcome", "cost_before", "cost_after"}
    proposals: list[dict] = field(default_factory=list)
    # cost_history[k] = program cost after iteration k (index 0 = original cost)
    cost_history: list[float] = field(default_factory=list)
    final_check_reason: str = ""
    llm_calls: int = 0                # requests sent to the LLM (including unusable replies)
    stopped_reason: str = ""          # set when the run stopped early (e.g. program too long to verify)
    hit_iteration_cap: bool = False   # True if max_iterations stopped the loop before convergence
    optimizer_mode: str = "rule"      # the specialist's routing policy: "rule", "llm" or "hybrid"
    llm_provider: str = ""            # LLM backend the specialist could route to ("" if none)
    llm_model: str = ""

    def format_report(self) -> str:
        """Full per-program report: decision log, result summary and both TAC listings."""
        lines = [self.log.format_log(), "=== RESULT ==="]
        lines.append(f"  Original cost: {self.original_cost.weighted_total:.1f}")
        lines.append(f"  Final cost:    {self.final_cost.weighted_total:.1f}")
        lines.append(f"  Reduction:     {self.cost_reduction_pct:.1f}%")
        lines.append(f"  Iterations:    {self.iterations}")
        lines.append(f"  Accepted:      {self.accepted_count}")
        lines.append(f"  Rejected:      {self.rejected_count}")
        lines.append(f"  Invalid:       {self.invalid_count}")
        if self.llm_provider:
            lines.append(f"  Routing:       {self.optimizer_mode} (LLM: {self.llm_provider} {self.llm_model})")
        if self.llm_proposals:
            lines.append(f"  LLM proposals: {self.llm_proposals} ({self.llm_valid} passed verification)")
        match_text = "PASS ✓" if self.output_match else "FAIL ✗"
        lines.append(f"  Output match:  {match_text}")
        lines.append("=== Original TAC ===")
        lines.append(format_tac(self.original_tac, prefix="  "))
        lines.append("=== Optimized TAC ===")
        lines.append(format_tac(self.optimized_tac, prefix="  "))
        return "\n".join(lines)


class Orchestrator:
    def __init__(self, use_llm: bool = False, max_iterations: int = 50,
                 llm_model: str | None = None, max_llm_calls: int = 5,
                 llm_provider: str = DEFAULT_PROVIDER, optimizer_mode: str | None = None,
                 offline: bool = False):
        """``optimizer_mode`` is the Optimization Specialist's routing policy ("rule", "llm"
        or "hybrid"). ``use_llm`` is the older switch and means "hybrid". ``offline`` makes
        the LLM the local Ollama model instead of a cloud one."""
        self.analyzer = CodeAnalyzer()
        self.specialist = OptimizationSpecialist(optimizer_mode or DEFAULT_MODE, max_llm_calls=max_llm_calls)
        if optimizer_mode in ("llm", "hybrid") or (optimizer_mode is None and use_llm):
            self.specialist.llm_optimizer = create_llm_optimizer(llm_provider, llm_model, offline=offline)
        self.verifier = Verifier()
        self.cost_evaluator = CostEvaluator()
        self.max_iterations = max_iterations

    # The LLM proposer lives in the specialist; this keeps ``orchestrator.llm_optimizer`` working.
    @property
    def llm_optimizer(self):
        return self.specialist.llm_optimizer

    @llm_optimizer.setter
    def llm_optimizer(self, value) -> None:
        self.specialist.llm_optimizer = value

    is_provably_minimal = staticmethod(is_provably_minimal)

    @staticmethod
    def _opportunity_key(opp: Opportunity) -> tuple:
        return (opp.type.value, opp.location, opp.description)

    def optimize(self, program: TACProgram, program_name: str = "") -> OptimizationResult:
        logger = DecisionLogger(program_name)
        specialist = self.specialist
        current = program.copy()
        outcomes: Counter = Counter()        # every proposal, by outcome
        llm_outcomes: Counter = Counter()    # the LLM's share of them
        types_applied: list[str] = []
        attempted_opportunities: set[tuple] = set()  # track to avoid infinite loops
        llm_calls = 0
        proposals: list[dict] = []
        cost_history = [self.cost_evaluator.evaluate(current).weighted_total]
        iteration = 0
        hit_cap = False
        stopped_reason = ""

        for iteration in range(1, self.max_iterations + 1):
            # 1. ANALYZE (leaving out opportunities already turned down for this program)
            opportunities = [o for o in self.analyzer.analyze(current)
                             if self._opportunity_key(o) not in attempted_opportunities]
            logger.log_analysis(iteration, opportunities)

            # 2-5. PROPOSE -> VERIFY -> EVALUATE -> ACCEPT/REJECT. The specialist routes the
            # step to the rules or to the LLM; if that proposal is turned down, it may give
            # the same step to the other one.
            tried: list[Route] = []
            outcome = None
            while outcome not in ("accepted", "unverifiable"):
                decision = specialist.route(current, opportunities, llm_calls, tried)
                if decision.route is None:
                    if not tried and decision.llm_note:
                        logger.log_info(iteration, f"LLM not consulted: {decision.llm_note}")
                    break
                tried.append(decision.route)
                if specialist.llm_attached:
                    logger.log_route(iteration, decision.route.value,
                                     specialist.route_label(decision.route), decision.reason)
                proposal = specialist.propose(current, decision, opportunities)
                if proposal.source == "llm":
                    llm_calls += 1
                else:
                    attempted_opportunities.add(self._opportunity_key(proposal.opportunity))
                outcome = self._judge(iteration, current, proposal, logger, proposals)
                outcomes[outcome] += 1
                if proposal.source == "llm":
                    llm_outcomes[outcome] += 1
                if outcome == "accepted":
                    current = proposal.candidate
                    types_applied.append(proposal.type)
                    # Reset attempted set after acceptance -- new opportunities may appear
                    attempted_opportunities.clear()

            if outcome == "unverifiable":
                # The program itself does not finish within the verifier's step limit, so no
                # change to it can be checked by running it. Every other proposal would fail
                # the same way, so stop here instead of grinding through all of them.
                stopped_reason = (f"the program does not finish within {self.verifier.max_steps:,} steps, "
                                  "so changes to it cannot be verified")
                logger.log_info(iteration, f"Stopped: {stopped_reason}")
                cost_history.append(cost_history[-1])
                break
            cost_history.append(self.cost_evaluator.evaluate(current).weighted_total)
            if outcome != "accepted" and not opportunities:
                break       # nothing was accepted and the rules have nothing left to try
        else:
            # The loop used every iteration. That only counts as "stopped by the cap"
            # if there was still something left to try.
            remaining = [o for o in self.analyzer.analyze(current)
                         if self._opportunity_key(o) not in attempted_opportunities]
            if self.max_iterations > 0 and remaining:
                hit_cap = True
                logger.log_info(iteration, f"Stopped: reached max_iterations={self.max_iterations}")

        # Final verification
        final_match, final_reason = self._final_output_check(program, current)

        orig_cost = self.cost_evaluator.evaluate(program)
        fin_cost = self.cost_evaluator.evaluate(current)
        llm = specialist.llm_optimizer if specialist.llm_attached else None

        return OptimizationResult(
            program_name=program_name,
            original_tac=program,
            optimized_tac=current,
            original_cost=orig_cost,
            final_cost=fin_cost,
            cost_reduction_pct=self.cost_evaluator.reduction_percentage(orig_cost, fin_cost),
            iterations=iteration,
            accepted_count=outcomes["accepted"],
            rejected_count=outcomes["rejected"],
            invalid_count=outcomes["invalid"],
            optimization_types_applied=types_applied,
            log=logger,
            output_match=final_match,
            llm_proposals=llm_outcomes["accepted"] + llm_outcomes["rejected"] + llm_outcomes["invalid"],
            llm_valid=llm_outcomes["accepted"] + llm_outcomes["rejected"],
            proposals=proposals,
            cost_history=cost_history,
            final_check_reason=final_reason,
            hit_iteration_cap=hit_cap,
            llm_calls=llm_calls,
            stopped_reason=stopped_reason,
            optimizer_mode=specialist.mode if llm is not None else "rule",
            llm_provider=getattr(llm, "provider", ""),
            llm_model=getattr(llm, "model", ""),
        )

    # ------------------------------------------------------------------ #
    def _judge(self, iteration: int, current: TACProgram, proposal: Proposal, logger: DecisionLogger,
               proposals: list[dict]) -> str:
        """Send one proposal through the verify and cost gates (the same for rules and LLM).

        Returns "accepted", "rejected" (correct but not cheaper), "invalid" (failed
        verification), "no_proposal" (the LLM returned nothing usable) or "unverifiable".
        """
        # 2. PROPOSE
        if proposal.source == "llm":
            logger.log_llm_proposal(iteration, proposal.reasoning, proposal.candidate, tac_before=current)
            if proposal.candidate is None:
                return "no_proposal"
        else:
            logger.log_proposal(iteration, proposal.opportunity, proposal.candidate, tac_before=current)

        # 3. VERIFY
        ver_result = self.verifier.verify(current, proposal.candidate)
        logger.log_verification(iteration, ver_result)
        if (ver_result.details or {}).get("inconclusive"):
            logger.log_reject(iteration, "Could not be verified (program runs too long)")
            return "unverifiable"
        record = {"iteration": iteration, "source": proposal.source, "type": proposal.type,
                  "outcome": "invalid", "cost_before": None, "cost_after": None}
        proposals.append(record)
        if not ver_result.passed:
            logger.log_reject(iteration, f"Verification failed: {ver_result.reason}")
            return "invalid"

        # 4. EVALUATE
        old_cost = self.cost_evaluator.evaluate(current)
        new_cost = self.cost_evaluator.evaluate(proposal.candidate)
        logger.log_cost(iteration, old_cost, new_cost)
        record["cost_before"] = old_cost.weighted_total
        record["cost_after"] = new_cost.weighted_total

        # 5. ACCEPT / REJECT
        if not self.cost_evaluator.is_improvement(old_cost, new_cost):
            record["outcome"] = "rejected"
            logger.log_reject(iteration, "No cost improvement")
            return "rejected"
        record["outcome"] = "accepted"
        logger.log_accept(iteration, f"Cost reduced: {old_cost.weighted_total} → {new_cost.weighted_total}")
        return "accepted"

    def _final_output_check(self, original: TACProgram, optimized: TACProgram) -> tuple[bool, str]:
        """End-to-end check of the final program against the untouched original."""
        if optimized == original:
            return True, "no changes were made, so the program is unchanged"
        result = self.verifier.verify(original, optimized)
        return result.passed, result.reason
