"""Structured decision log for the optimisation agent loop."""
from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import asdict, dataclass


@dataclass
class DecisionEntry:
    iteration: int
    phase: str              # "analyze", "propose", "verify", "evaluate", "accept", "reject"
    opportunity_type: str | None
    description: str
    tac_before: str | None = None
    tac_after: str | None = None
    verification_result: str | None = None
    cost_before: float | None = None
    cost_after: float | None = None
    decision: str | None = None    # "ACCEPT" or "REJECT"
    reason: str | None = None
    source: str = "rule"           # "rule" or "llm"


_TAGS = {
    "analyze": "[ANALYZE]",
    "propose": "[PROPOSE]",
    "verify": "[VERIFY] ",
    "evaluate": "[COST]   ",
    "accept": "[ACCEPT] ",
    "reject": "[REJECT] ",
    "info": "[INFO]   ",
}


class DecisionLogger:
    def __init__(self, program_name: str = ""):
        self.program_name = program_name
        self.entries: list[DecisionEntry] = []
        self._current_type: str | None = None
        self._current_source: str = "rule"

    # ------------------------------------------------------------------ #
    def log_analysis(self, iteration, opportunities) -> None:
        if not opportunities:
            desc = "No more opportunities found."
        else:
            counts = Counter(o.type.value for o in opportunities)
            prio = {o.type.value: o.priority for o in opportunities}
            ordered = sorted(counts, key=lambda t: -prio[t])
            parts = [f"{t}{'x' + str(counts[t]) if counts[t] > 1 else ''} (priority={prio[t]})"
                     for t in ordered]
            desc = f"Found {len(opportunities)} opportunit{'y' if len(opportunities) == 1 else 'ies'}: " \
                   + ", ".join(parts)
        self.entries.append(DecisionEntry(iteration, "analyze", None, desc))

    def log_proposal(self, iteration, opportunity, candidate_tac, tac_before=None) -> None:
        self._current_type = opportunity.type.value
        self._current_source = "rule"
        before = opportunity.details.get("before", "")
        after = opportunity.details.get("after", "")
        desc = (f"Applying {opportunity.type.value} at instruction {opportunity.location}: "
                f"{before} → {after}")
        self.entries.append(DecisionEntry(
            iteration, "propose", opportunity.type.value, desc,
            tac_before=tac_before.to_string() if tac_before is not None else None,
            tac_after=candidate_tac.to_string() if candidate_tac is not None else None))

    def log_llm_proposal(self, iteration, reasoning, candidate_tac, tac_before=None) -> None:
        self._current_type = "LLM"
        self._current_source = "llm"
        desc = f"LLM proposal: {reasoning}" if candidate_tac is not None else f"LLM produced no usable TAC: {reasoning}"
        self.entries.append(DecisionEntry(
            iteration, "propose", "LLM", desc,
            tac_before=tac_before.to_string() if tac_before is not None else None,
            tac_after=candidate_tac.to_string() if candidate_tac is not None else None,
            source="llm"))

    def log_verification(self, iteration, result) -> None:
        status = "PASS" if result.passed else "FAIL"
        desc = f"{status} ({result.reason})"
        self.entries.append(DecisionEntry(
            iteration, "verify", self._current_type, desc,
            verification_result=status, reason=result.reason, source=self._current_source))

    def log_cost(self, iteration, old_cost, new_cost) -> None:
        old_v, new_v = old_cost.weighted_total, new_cost.weighted_total
        pct = (old_v - new_v) / old_v * 100 if old_v else 0.0
        desc = f"Before: {old_v:.1f}, After: {new_v:.1f} (reduction: {pct:.1f}%)"
        self.entries.append(DecisionEntry(
            iteration, "evaluate", self._current_type, desc,
            cost_before=old_v, cost_after=new_v, source=self._current_source))

    def log_accept(self, iteration, reason) -> None:
        self.entries.append(DecisionEntry(
            iteration, "accept", self._current_type, "✓ Change accepted",
            decision="ACCEPT", reason=reason, source=self._current_source))

    def log_reject(self, iteration, reason) -> None:
        self.entries.append(DecisionEntry(
            iteration, "reject", self._current_type, f"✗ Change rejected: {reason}",
            decision="REJECT", reason=reason, source=self._current_source))

    def log_info(self, iteration, message) -> None:
        self.entries.append(DecisionEntry(iteration, "info", None, message))

    # ------------------------------------------------------------------ #
    def format_log(self) -> str:
        """Human-readable multi-line decision log."""
        lines: list[str] = []
        if self.program_name:
            lines.append(f"=== Program: {self.program_name} ===")
        current_iter = None
        for e in self.entries:
            if e.iteration != current_iter:
                current_iter = e.iteration
                lines.append(f"--- Iteration {e.iteration} ---")
            tag = _TAGS.get(e.phase, f"[{e.phase.upper()}]")
            if e.source == "llm" and e.phase == "propose":
                tag = "[LLM]    "
            lines.append(f"  {tag} {e.description}")
        return "\n".join(lines)

    def to_json(self) -> list[dict]:
        """Machine-readable JSON log."""
        return [asdict(e) for e in self.entries]

    def save(self, filepath: str) -> None:
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump({"program": self.program_name, "entries": self.to_json()}, fh, indent=2)
