"""Tests for the Optimization Specialist: routing between the rules and the LLM."""
import pytest

from src.agents.code_analyzer import CodeAnalyzer
from src.agents.optimization_specialist import MODES, OptimizationSpecialist, Route
from src.agents.orchestrator import Orchestrator
from src.tac.program import TACProgram


def P(text):
    return TACProgram.from_string(text)


def found(prog):
    return CodeAnalyzer().analyze(prog)


class _FakeLLM:
    """Stands in for an LLM backend: returns a fixed sequence of proposals."""

    def __init__(self, proposals=(), available=True):
        self.proposals = list(proposals)
        self.available = available
        self.unavailable_reason = "" if available else "server down"
        self.calls = 0

    def propose(self, program):
        self.calls += 1
        if not self.proposals:
            return None, "nothing more"
        text, reason = self.proposals.pop(0)
        return (P(text) if text else None), reason


FOLDABLE = "t0 = 3 + 5\nprint t0"


# ------------------------------------------------------------------ routing
def test_rule_mode_never_routes_to_the_llm():
    spec = OptimizationSpecialist("rule", _FakeLLM())
    prog = P(FOLDABLE)
    assert spec.route(prog, found(prog)).route is Route.RULE
    assert spec.route(prog, found(prog), tried=[Route.RULE]).route is None
    assert spec.route(prog, []).route is None
    assert not spec.llm_attached


def test_hybrid_mode_routes_to_the_rules_first_and_the_llm_second():
    spec = OptimizationSpecialist("hybrid", _FakeLLM())
    prog = P(FOLDABLE)
    first = spec.route(prog, found(prog))
    assert first.route is Route.RULE
    assert first.reason == "highest-priority opportunity is CONSTANT_FOLD (priority 100)"
    second = spec.route(prog, found(prog), tried=[Route.RULE])
    assert second.route is Route.LLM and second.reason == "the rule-based proposal was turned down"
    exhausted = spec.route(prog, [])
    assert exhausted.route is Route.LLM and exhausted.reason == "the rules have nothing left to try"
    assert spec.route(prog, [], tried=[Route.LLM]).route is None


def test_llm_mode_routes_to_the_llm_first_and_the_rules_second():
    spec = OptimizationSpecialist("llm", _FakeLLM())
    prog = P(FOLDABLE)
    first = spec.route(prog, found(prog))
    assert first.route is Route.LLM and first.reason == "LLM-first mode"
    second = spec.route(prog, found(prog), tried=[Route.LLM])
    assert second.route is Route.RULE and second.reason == "the LLM proposal was turned down"
    assert spec.route(prog, found(prog), tried=[Route.LLM, Route.RULE]).route is None


def test_llm_that_cannot_be_used_is_routed_around():
    prog = P(FOLDABLE)
    down = OptimizationSpecialist("llm", _FakeLLM(available=False))
    decision = down.route(prog, found(prog))
    assert decision.route is Route.RULE and "unavailable (server down)" in decision.reason
    spent = OptimizationSpecialist("llm", _FakeLLM(), max_llm_calls=2)
    assert spent.route(prog, found(prog), llm_calls=1).route is Route.LLM
    decision = spent.route(prog, found(prog), llm_calls=2)
    assert decision.route is Route.RULE and "call budget used up (2 per program)" in decision.reason
    nothing = spent.route(prog, [], llm_calls=2)
    assert nothing.route is None and nothing.llm_note == "call budget used up (2 per program)"


def test_llm_is_not_asked_about_a_provably_minimal_program():
    for mode in ("llm", "hybrid"):
        decision = OptimizationSpecialist(mode, _FakeLLM()).route(P("print 1\nprint -4"), [])
        assert decision.route is None and "provably minimal" in decision.llm_note


@pytest.mark.parametrize("mode", MODES)
def test_without_an_llm_every_mode_is_rule_based(mode):
    spec = OptimizationSpecialist(mode)
    prog = P(FOLDABLE)
    assert not spec.llm_attached
    assert spec.route(prog, found(prog)).route is Route.RULE
    nothing = spec.route(prog, [])
    assert nothing.route is None and nothing.llm_note == ""


def test_unknown_mode_is_rejected():
    with pytest.raises(ValueError, match="unknown optimizer mode"):
        OptimizationSpecialist("fastest")
    with pytest.raises(ValueError):
        Orchestrator(optimizer_mode="fastest")


# ------------------------------------------------------------------ proposing
def test_rule_route_applies_the_highest_priority_opportunity():
    spec = OptimizationSpecialist("rule")
    prog = P("t0 = 3 + 5\nt1 = x * 1\ndead = 9\nprint t0\nprint t1")
    snapshot = prog.to_string()
    opps = found(prog)
    proposal = spec.propose(prog, spec.route(prog, opps), opps)
    assert (proposal.source, proposal.type) == ("rule", "CONSTANT_FOLD")
    assert proposal.opportunity is opps[0] and proposal.candidate != prog
    assert prog.to_string() == snapshot                 # the input program is never modified


def test_llm_route_returns_the_models_proposal():
    llm = _FakeLLM([("print 8", "evaluated the constant expression")])
    spec = OptimizationSpecialist("llm", llm)
    prog = P(FOLDABLE)
    proposal = spec.propose(prog, spec.route(prog, found(prog)), found(prog))
    assert (proposal.source, proposal.type) == ("llm", "LLM")
    assert proposal.candidate.to_string() == "print 8" and proposal.opportunity is None
    assert proposal.reasoning == "evaluated the constant expression" and llm.calls == 1


def test_route_labels_name_the_llm_backend():
    llm = _FakeLLM()
    llm.label = "ollama qwen2.5-coder:7b"
    spec = OptimizationSpecialist("hybrid", llm)
    assert spec.route_label(Route.RULE) == "Rule-based optimizer"
    assert spec.route_label(Route.LLM) == "LLM optimizer (ollama qwen2.5-coder:7b)"
    assert OptimizationSpecialist("hybrid", _FakeLLM()).route_label(Route.LLM) == "LLM optimizer"


# ------------------------------------------------------------------ in the agent loop
def _orchestrator(mode, llm, **kwargs):
    orch = Orchestrator(**kwargs)
    orch.specialist.mode = mode
    orch.llm_optimizer = llm
    return orch


def test_llm_first_mode_accepts_a_correct_llm_proposal():
    llm = _FakeLLM([("print 8", "evaluated everything")])
    result = _orchestrator("llm", llm).optimize(P("t0 = 3 + 5\nt1 = t0 * 1\nprint t1"))
    assert result.optimized_tac.to_string() == "print 8" and result.output_match
    assert result.optimization_types_applied == ["LLM"]           # one LLM step replaced several rule steps
    assert result.llm_calls == 1 and result.llm_valid == 1 and result.optimizer_mode == "llm"
    log = result.log.format_log()
    assert "[ROUTE]   LLM optimizer: LLM-first mode" in log
    assert "LLM not consulted: program is only constant prints" in log


def test_llm_first_mode_falls_back_to_the_rules_when_the_llm_is_wrong():
    prog = P("t0 = 3 + 5\nt1 = t0 * 1\nprint t1")
    rule_only = Orchestrator().optimize(prog)
    llm = _FakeLLM([("print 0", "wrong")] * 5)
    result = _orchestrator("llm", llm).optimize(prog)
    assert result.optimized_tac == rule_only.optimized_tac        # never worse than the rules alone
    assert result.output_match and result.llm_valid == 0
    assert result.invalid_count == result.llm_proposals >= 1
    assert "[ROUTE]   Rule-based optimizer: the LLM proposal was turned down" in result.log.format_log()
    assert {p["source"] for p in result.proposals} == {"rule", "llm"}


def test_llm_first_mode_respects_the_call_budget():
    llm = _FakeLLM([("print 0", "wrong")] * 9)
    result = _orchestrator("llm", llm, max_llm_calls=2).optimize(P("t0 = 3 + 5\nt1 = t0 * 1\nprint t1"))
    assert llm.calls == result.llm_calls == 2
    assert result.optimized_tac.to_string() == "print 8"
    assert "LLM not used, call budget used up (2 per program)" in result.log.format_log()


def test_unavailable_llm_in_llm_mode_leaves_a_rule_based_run():
    prog = P("t0 = 3 + 5\nt1 = t0 * 1\nprint t1")
    result = _orchestrator("llm", _FakeLLM(available=False)).optimize(prog)
    assert result.optimized_tac == Orchestrator().optimize(prog).optimized_tac
    assert result.llm_calls == 0 and {p["source"] for p in result.proposals} == {"rule"}
    assert "LLM not used, unavailable (server down)" in result.log.format_log()


def test_rule_mode_orchestrator_ignores_an_attached_llm():
    llm = _FakeLLM([("print 0", "wrong")])
    orch = Orchestrator(optimizer_mode="rule")
    orch.llm_optimizer = llm
    result = orch.optimize(P("t0 = x * 2\nprint t0"))
    assert llm.calls == 0 and result.optimizer_mode == "rule"
    assert "[ROUTE]" not in result.log.format_log()


def test_route_lines_appear_only_when_there_is_a_choice():
    prog = P("t0 = x * 2\nprint t0")
    assert "[ROUTE]" not in Orchestrator().optimize(prog).log.format_log()
    orch = Orchestrator()
    orch.llm_optimizer = _FakeLLM([("t0 = x << 1\nprint t0", "shift")])
    result = orch.optimize(prog)
    log = result.log.format_log()
    assert "[ROUTE]   Rule-based optimizer: highest-priority opportunity is STRENGTH_REDUCTION" in log
    assert "[ROUTE]   LLM optimizer: the rule-based proposal was turned down" in log
    routes = [e for e in result.log.entries if e.phase == "route"]
    assert [e.source for e in routes][:2] == ["rule", "llm"]


def test_result_records_the_routing_mode_and_llm_backend():
    plain = Orchestrator().optimize(P(FOLDABLE))
    assert (plain.optimizer_mode, plain.llm_provider, plain.llm_model) == ("rule", "", "")
    assert "Routing:" not in plain.format_report()
    llm = _FakeLLM()
    llm.provider, llm.model = "ollama", "qwen2.5-coder:7b"
    orch = Orchestrator()
    orch.llm_optimizer = llm
    result = orch.optimize(P(FOLDABLE))
    assert (result.optimizer_mode, result.llm_provider) == ("hybrid", "ollama")
    assert "Routing:       hybrid (LLM: ollama qwen2.5-coder:7b)" in result.format_report()


def test_unverifiable_llm_proposal_stops_the_run_and_is_not_counted_as_wrong():
    # The program never finishes, so nothing about it can be checked by running it.
    prog = P("L0:\ngoto L0")
    orch = Orchestrator()
    orch.llm_optimizer = _FakeLLM([("L1:\ngoto L1", "renamed the label")])
    result = orch.optimize(prog)
    assert "does not finish" in result.stopped_reason
    assert result.optimized_tac == prog and result.proposals == []
    assert result.llm_calls == 1 and result.llm_proposals == 0 and result.invalid_count == 0
