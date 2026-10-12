"""Tests for LLM self-repair: a rejected answer goes back to the model with the reason."""
from src.agents.optimization_specialist import OptimizationSpecialist, Proposal
from src.agents.optimizer_llm import BaseLLMOptimizer, tac_parse_error
from src.agents.orchestrator import Orchestrator
from src.tac.program import TACProgram
from src.visualization.report import aggregate_metrics, format_metrics_table, result_to_record


def P(text):
    return TACProgram.from_string(text)


PROG = "t0 = x * 2\nprint t0"            # the only rule proposal (x + x) is cost-neutral, so the LLM is asked
RIGHT = ("t0 = x << 1\nprint t0", "multiply by 2 is a shift", "")
WRONG = ("print 2", "x is probably 1", "")


class _RepairableLLM:
    """A scripted LLM that also supports repair. Replies are (tac text, reasoning, failure)."""

    provider, available, unavailable_reason = "fake", True, ""

    def __init__(self, proposals, repairs=()):
        self.proposals, self.repairs = list(proposals), list(repairs)
        self.repair_requests = []
        self.last_failure = self.last_tac = ""

    def _reply(self, queue):
        if not queue:
            self.last_failure, self.last_tac = "error", ""
            return None, "nothing more"
        text, reasoning, self.last_failure = queue.pop(0)
        self.last_tac = text
        return (None if self.last_failure else P(text)), reasoning

    def propose(self, program):
        return self._reply(self.proposals)

    def repair(self, program, rejected, problem):
        self.repair_requests.append((rejected, problem))
        return self._reply(self.repairs)


def run(llm, max_repairs=1, max_llm_calls=1, prog=PROG):
    orch = Orchestrator(max_llm_calls=max_llm_calls, max_repairs=max_repairs)
    orch.llm_optimizer = llm
    return orch.optimize(P(prog))


# ------------------------------------------------------------------ the agent loop
def test_wrong_answer_is_repaired_with_the_verifiers_counterexample():
    llm = _RepairableLLM([WRONG], [RIGHT])
    result = run(llm)
    assert result.optimized_tac.to_string() == "t0 = x << 1\nprint t0" and result.output_match
    rejected, problem = llm.repair_requests[0]
    assert rejected == "print 2"
    assert "output mismatch on inputs" in problem and "candidate printed [2]" in problem
    assert (result.llm_repairs, result.llm_repairs_accepted) == (1, 1)
    assert result.llm_calls == 2                              # the proposal and its repair
    assert (result.llm_proposals, result.llm_valid, result.invalid_count) == (2, 1, 1)
    llm_records = [p for p in result.proposals if p["source"] == "llm"]
    assert [(p["outcome"], p.get("repair", False)) for p in llm_records] == [("invalid", False), ("accepted", True)]


def test_repair_is_written_to_the_decision_log():
    result = run(_RepairableLLM([WRONG], [RIGHT]))
    log = result.log.format_log()
    assert "[REPAIR]  Feedback sent to the LLM: It changes what the program does: output mismatch" in log
    assert "[LLM]     LLM repair: multiply by 2 is a shift" in log
    assert "LLM repairs:   1 (1 accepted)" in result.format_report()
    phases = [e.phase for e in result.log.entries]
    assert phases.index("repair") < len(phases) - 1 and phases[phases.index("repair") + 1] == "propose"


def test_unparseable_answer_is_repaired_with_the_syntax_error():
    llm = _RepairableLLM([("t0 = x + x + 0\nprint t0", "two operators at once", "unparseable")], [RIGHT])
    result = run(llm)
    rejected, problem = llm.repair_requests[0]
    assert rejected.startswith("t0 = x + x + 0") and "It is not valid TAC" in problem
    assert "at most one operator" in problem
    assert result.optimized_tac.to_string() == "t0 = x << 1\nprint t0"
    assert (result.llm_repairs, result.llm_repairs_accepted, result.invalid_count) == (1, 1, 0)


def test_a_repair_that_is_also_wrong_is_rejected_too():
    llm = _RepairableLLM([WRONG], [("print 3", "then it must be 3", "")])
    result = run(llm)
    assert result.optimized_tac == P(PROG) and result.output_match      # nothing wrong was ever accepted
    assert (result.llm_repairs, result.llm_repairs_accepted, result.invalid_count) == (1, 0, 2)
    assert len(llm.repair_requests) == 1                                 # max_repairs is 1


def test_second_repair_gets_feedback_on_the_latest_answer():
    llm = _RepairableLLM([WRONG], [("print 3", "then it must be 3", ""), RIGHT])
    result = run(llm, max_repairs=2)
    assert [r[0] for r in llm.repair_requests] == ["print 2", "print 3"]
    assert "candidate printed [3]" in llm.repair_requests[1][1]
    assert (result.llm_repairs, result.llm_repairs_accepted) == (2, 1)


def test_repair_can_be_switched_off():
    llm = _RepairableLLM([WRONG], [RIGHT])
    result = run(llm, max_repairs=0)
    assert llm.repair_requests == [] and result.llm_repairs == 0
    assert result.optimized_tac == P(PROG) and "[REPAIR]" not in result.log.format_log()


def test_unchanged_answers_and_api_errors_are_not_repaired():
    for failure in ("unchanged", "error"):
        llm = _RepairableLLM([(PROG, "nothing to do", failure)], [RIGHT])
        result = run(llm)
        assert llm.repair_requests == [] and result.llm_repairs == 0, failure


def test_repairs_do_not_use_up_the_call_budget():
    # one fresh proposal allowed per program; its repair is extra, and a later program state
    # gets no second fresh proposal
    llm = _RepairableLLM([WRONG, RIGHT], [("print 3", "still guessing", "")])
    result = run(llm, max_llm_calls=1)
    assert result.llm_calls == 2 and len(llm.proposals) == 1


def test_llm_without_a_repair_method_still_works():
    class Plain:
        available, unavailable_reason = True, ""

        def propose(self, program):
            return P("print 2"), "wrong"

    result = run(Plain())
    assert result.llm_repairs == 0 and result.invalid_count == 1 and result.output_match


# ------------------------------------------------------------------ the specialist
def test_specialist_only_repairs_what_can_be_explained():
    llm = _RepairableLLM([])
    spec = OptimizationSpecialist("hybrid", llm, max_repairs=1)
    invalid = Proposal("llm", "LLM", P("print 2"), "wrong", failure="invalid", problem="...", rejected_tac="print 2")
    assert spec.can_repair(invalid, 0) and not spec.can_repair(invalid, 1)
    assert not spec.can_repair(Proposal("llm", "LLM", None, "same", failure="unchanged"), 0)
    assert not spec.can_repair(Proposal("rule", "DEAD_CODE", P("print 1"), "", failure="invalid"), 0)
    llm.available = False
    assert not spec.can_repair(invalid, 0)
    assert not OptimizationSpecialist("rule", _RepairableLLM([]), max_repairs=1).can_repair(invalid, 0)


# ------------------------------------------------------------------ the prompt
class _Recording(BaseLLMOptimizer):
    provider = "recording"

    def __init__(self, replies):
        super().__init__("test-model")
        self.replies, self.prompts = list(replies), []

    def _complete(self, prompt):
        self.prompts.append(prompt)
        return self.replies.pop(0)


def test_repair_prompt_shows_the_rejected_answer_and_the_reason():
    opt = _Recording(["<reasoning>shift</reasoning><tac>t0 = x << 1\nprint t0</tac>"])
    cand, reason = opt.repair(P(PROG), "print 2", "It changes what the program does: output mismatch on inputs {'x': 5}.")
    assert cand.to_string() == "t0 = x << 1\nprint t0" and reason == "shift"
    prompt = opt.prompts[0]
    assert "Original TAC:\nt0 = x * 2\nprint t0" in prompt
    assert "Your rejected answer:\nprint 2" in prompt
    assert "Why it was rejected:\nIt changes what the program does: output mismatch on inputs {'x': 5}." in prompt
    assert "TAC syntax (one instruction per line" in prompt and "<tac>" in prompt     # same rules as a first try


def test_optimizer_remembers_why_a_reply_was_unusable():
    opt = _Recording(["<reasoning>r</reasoning><tac>t0 = x + x + 0\nprint t0</tac>",
                      "<reasoning>r</reasoning><tac>t0 = x * 2\nprint t0</tac>", "no tags at all",
                      "<reasoning>r</reasoning><tac>t0 = x << 1\nprint t0</tac>"])
    prog = P(PROG)
    assert opt.propose(prog)[0] is None and opt.last_failure == "unparseable" and "x + x + 0" in opt.last_tac
    assert opt.propose(prog)[0] is None and opt.last_failure == "unchanged"
    assert opt.propose(prog)[0] is None and opt.last_failure == "no_tac"
    assert opt.propose(prog)[0] is not None and opt.last_failure == ""


def test_tac_parse_error_explains_the_problem():
    assert tac_parse_error("t0 = 8\nprint t0") == ""
    assert tac_parse_error("") == "the <tac> block is empty"
    assert tac_parse_error("t0 = x + x + 0") != ""


# ------------------------------------------------------------------ metrics
def test_metrics_report_repairs():
    result = run(_RepairableLLM([WRONG], [RIGHT]))
    record = result_to_record(result, "mixed")
    assert (record["llm_calls"], record["llm_repairs"], record["llm_repairs_accepted"]) == (2, 1, 1)
    metrics = aggregate_metrics([record])
    assert (metrics["llm_repairs"], metrics["llm_repairs_accepted"]) == (1, 1)
    assert "1 / 1" in format_metrics_table(metrics)
    old_record = {k: v for k, v in record.items() if not k.startswith("llm_repairs")}   # results saved before
    assert aggregate_metrics([old_record])["llm_repairs"] == 0
