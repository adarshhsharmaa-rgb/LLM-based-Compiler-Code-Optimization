"""Orchestrator: drives the Analyze -> Propose -> Verify -> Evaluate -> Accept/Reject loop."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..tac.instruction import TACOp, is_literal
from ..tac.printer import format_tac
from ..tac.program import TACProgram
from .code_analyzer import CodeAnalyzer, Opportunity
from .cost_evaluator import CostBreakdown, CostEvaluator
from .decision_log import DecisionLogger
from .optimizer_llm import DEFAULT_PROVIDER, create_llm_optimizer
from .optimizer_rule import RuleBasedOptimizer
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
    hit_iteration_cap: bool = False   # True if max_iterations stopped the loop before convergence

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
                 llm_provider: str = DEFAULT_PROVIDER):
        self.analyzer = CodeAnalyzer()
        self.rule_optimizer = RuleBasedOptimizer()
        self.llm_optimizer = create_llm_optimizer(llm_provider, llm_model) if use_llm else None
        self.verifier = Verifier()
        self.cost_evaluator = CostEvaluator()
        self.max_iterations = max_iterations
        self.max_llm_calls = max_llm_calls

    @staticmethod
    def _opportunity_key(opp: Opportunity) -> tuple:
        return (opp.type.value, opp.location, opp.description)

    def optimize(self, program: TACProgram, program_name: str = "") -> OptimizationResult:
        logger = DecisionLogger(program_name)
        current = program.copy()
        accepted = 0
        rejected = 0
        invalid = 0
        types_applied: list[str] = []
        attempted_opportunities: set[tuple] = set()  # track to avoid infinite loops
        llm_proposals = 0
        llm_valid = 0
        llm_calls = 0
        proposals: list[dict] = []
        cost_history = [self.cost_evaluator.evaluate(current).weighted_total]
        iteration = 0
        hit_cap = False

        for iteration in range(1, self.max_iterations + 1):
            # 1. ANALYZE
            opportunities = self.analyzer.analyze(current)
            # Filter out already-attempted opportunities
            opportunities = [o for o in opportunities
                             if self._opportunity_key(o) not in attempted_opportunities]

            if not opportunities:
                logger.log_analysis(iteration, [])
                # Rule-based search is exhausted; give the LLM a chance if enabled.
                if self._llm_ready(llm_calls) and self.is_provably_minimal(current):
                    logger.log_info(iteration, "LLM not consulted: program is only constant prints "
                                               "(provably minimal)")
                if self._llm_ready(llm_calls, current):
                    llm_calls += 1
                    outcome, current = self._llm_step(iteration, current, logger, proposals)
                    llm_proposals += outcome != "no_proposal"
                    llm_valid += outcome in ("accepted", "rejected")
                    if outcome == "accepted":
                        accepted += 1
                        types_applied.append("LLM")
                        attempted_opportunities.clear()
                        cost_history.append(self.cost_evaluator.evaluate(current).weighted_total)
                        continue
                    rejected += outcome == "rejected"
                    invalid += outcome == "invalid"
                cost_history.append(cost_history[-1])
                break

            opportunity = opportunities[0]
            logger.log_analysis(iteration, opportunities)
            attempted_opportunities.add(self._opportunity_key(opportunity))

            # 2. PROPOSE
            candidate = self.rule_optimizer.propose(current, opportunity)
            logger.log_proposal(iteration, opportunity, candidate, tac_before=current)

            # 3. VERIFY
            ver_result = self.verifier.verify(current, candidate)
            logger.log_verification(iteration, ver_result)
            record = {"iteration": iteration, "source": "rule", "type": opportunity.type.value,
                      "outcome": None, "cost_before": None, "cost_after": None}
            proposals.append(record)

            step_accepted = False
            if not ver_result.passed:
                invalid += 1
                record["outcome"] = "invalid"
                logger.log_reject(iteration, f"Verification failed: {ver_result.reason}")
            else:
                # 4. EVALUATE
                old_cost = self.cost_evaluator.evaluate(current)
                new_cost = self.cost_evaluator.evaluate(candidate)
                logger.log_cost(iteration, old_cost, new_cost)
                record["cost_before"] = old_cost.weighted_total
                record["cost_after"] = new_cost.weighted_total

                if not self.cost_evaluator.is_improvement(old_cost, new_cost):
                    rejected += 1
                    record["outcome"] = "rejected"
                    logger.log_reject(iteration, "No cost improvement")
                else:
                    # 5. ACCEPT
                    accepted += 1
                    record["outcome"] = "accepted"
                    types_applied.append(opportunity.type.value)
                    logger.log_accept(iteration,
                                      f"Cost reduced: {old_cost.weighted_total} → {new_cost.weighted_total}")
                    current = candidate
                    # Reset attempted set after acceptance -- new opportunities may appear
                    attempted_opportunities.clear()
                    step_accepted = True

            # Alternative path: when the rule-based proposal was turned down, ask the LLM.
            if not step_accepted and self._llm_ready(llm_calls, current):
                llm_calls += 1
                outcome, current = self._llm_step(iteration, current, logger, proposals)
                llm_proposals += outcome != "no_proposal"
                llm_valid += outcome in ("accepted", "rejected")
                if outcome == "accepted":
                    accepted += 1
                    types_applied.append("LLM")
                    attempted_opportunities.clear()
                elif outcome == "rejected":
                    rejected += 1
                elif outcome == "invalid":
                    invalid += 1

            cost_history.append(self.cost_evaluator.evaluate(current).weighted_total)
        else:
            if self.max_iterations > 0:
                hit_cap = True
                logger.log_info(iteration, f"Stopped: reached max_iterations={self.max_iterations}")

        # Final verification
        final_match, final_reason = self._final_output_check(program, current)

        orig_cost = self.cost_evaluator.evaluate(program)
        fin_cost = self.cost_evaluator.evaluate(current)

        return OptimizationResult(
            program_name=program_name,
            original_tac=program,
            optimized_tac=current,
            original_cost=orig_cost,
            final_cost=fin_cost,
            cost_reduction_pct=self.cost_evaluator.reduction_percentage(orig_cost, fin_cost),
            iterations=iteration,
            accepted_count=accepted,
            rejected_count=rejected,
            invalid_count=invalid,
            optimization_types_applied=types_applied,
            log=logger,
            output_match=final_match,
            llm_proposals=llm_proposals,
            llm_valid=llm_valid,
            proposals=proposals,
            cost_history=cost_history,
            final_check_reason=final_reason,
            hit_iteration_cap=hit_cap,
        )

    # ------------------------------------------------------------------ #
    def _llm_ready(self, llm_calls: int, current: TACProgram | None = None) -> bool:
        if self.llm_optimizer is None or not self.llm_optimizer.available:
            return False
        if llm_calls >= self.max_llm_calls:
            return False
        return current is None or not self.is_provably_minimal(current)

    @staticmethod
    def is_provably_minimal(program: TACProgram) -> bool:
        """True if the program is nothing but ``print <constant>`` lines.

        Every print must stay (it is observable output) and nothing else is
        left, so no optimizer can lower the cost -- asking the LLM would only
        waste an API call.
        """
        return all(ins.op == TACOp.PRINT and is_literal(ins.arg1) for ins in program.instructions)

    def _llm_step(self, iteration: int, current: TACProgram, logger: DecisionLogger,
                  proposals: list[dict]) -> tuple[str, TACProgram]:
        """One LLM proposal through the same verify/evaluate gates.

        Returns (outcome, new_current) where outcome is one of
        "accepted", "rejected", "invalid", "no_proposal".
        """
        candidate, reasoning = self.llm_optimizer.propose(current)
        logger.log_llm_proposal(iteration, reasoning, candidate, tac_before=current)
        if candidate is None:
            return "no_proposal", current
        record = {"iteration": iteration, "source": "llm", "type": "LLM",
                  "outcome": None, "cost_before": None, "cost_after": None}
        proposals.append(record)
        ver_result = self.verifier.verify(current, candidate)
        logger.log_verification(iteration, ver_result)
        if not ver_result.passed:
            record["outcome"] = "invalid"
            logger.log_reject(iteration, f"Verification failed: {ver_result.reason}")
            return "invalid", current
        old_cost = self.cost_evaluator.evaluate(current)
        new_cost = self.cost_evaluator.evaluate(candidate)
        logger.log_cost(iteration, old_cost, new_cost)
        record["cost_before"] = old_cost.weighted_total
        record["cost_after"] = new_cost.weighted_total
        if not self.cost_evaluator.is_improvement(old_cost, new_cost):
            record["outcome"] = "rejected"
            logger.log_reject(iteration, "No cost improvement")
            return "rejected", current
        record["outcome"] = "accepted"
        logger.log_accept(iteration, f"Cost reduced: {old_cost.weighted_total} → {new_cost.weighted_total}")
        return "accepted", candidate

    def _final_output_check(self, original: TACProgram, optimized: TACProgram) -> tuple[bool, str]:
        """End-to-end check of the final program against the untouched original."""
        result = self.verifier.verify(original, optimized)
        return result.passed, result.reason
