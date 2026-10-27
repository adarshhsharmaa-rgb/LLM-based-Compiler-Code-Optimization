import pytest

from src.agents.code_analyzer import CodeAnalyzer, OpportunityType as OT
from src.agents.optimizer_llm import parse_llm_tac
from src.agents.optimizer_rule import RuleBasedOptimizer
from src.tac.interpreter import TACInterpreter
from src.tac.program import TACProgram


def apply_first(text, otype, **match):
    prog = TACProgram.from_string(text)
    opps = [o for o in CodeAnalyzer().analyze(prog) if o.type == otype
            and all(o.details.get(k) == v for k, v in match.items())]
    assert opps, f"no {otype} opportunity found"
    new = RuleBasedOptimizer().propose(prog, opps[0])
    return prog, new


def same_output(a, b, inputs=None):
    interp = TACInterpreter()
    return interp.execute(a, inputs) == interp.execute(b, inputs)


def test_constant_fold():
    orig, new = apply_first("t0 = 3 + 5\nprint t0", OT.CONSTANT_FOLD)
    assert new.to_string() == "t0 = 8\nprint t0"
    assert orig.to_string() == "t0 = 3 + 5\nprint t0"  # original never mutated


def test_constant_fold_unary_and_division():
    _, new = apply_first("t0 = -7 / 2\nprint t0", OT.CONSTANT_FOLD)
    assert new.to_string() == "t0 = -3\nprint t0"


def test_constant_fold_of_comparison_forwards_constant():
    # Folding "t0 = 10 > 5" to "t0 = 1" alone would raise the cost (a copy costs more than a
    # comparison), so the folded constant is forwarded into its uses and the copy dropped.
    orig, new = apply_first("t0 = 10 > 5\nifFalse t0 goto L0\nprint 1\nL0:", OT.CONSTANT_FOLD)
    assert new.to_string() == "ifFalse 1 goto L0\nprint 1\nL0:"
    from src.agents.cost_evaluator import CostEvaluator
    ev = CostEvaluator()
    assert ev.is_improvement(ev.evaluate(orig), ev.evaluate(new))


def test_constant_fold_of_unary_forwards_constant():
    orig, new = apply_first("t0 = - 5\nt1 = x * t0\nprint t1", OT.CONSTANT_FOLD)
    assert new.to_string() == "t1 = x * -5\nprint t1"
    assert same_output(orig, new, {"x": 3})


@pytest.mark.parametrize("text,expected", [
    ("t0 = x + 0\nprint t0", "t0 = x\nprint t0"),
    ("t0 = 1 * x\nprint t0", "t0 = x\nprint t0"),
    ("t0 = x * 0\nprint t0", "t0 = 0\nprint t0"),
    ("t0 = x / 1\nprint t0", "t0 = x\nprint t0"),
    ("t0 = x - x\nprint t0", "t0 = 0\nprint t0"),
])
def test_algebraic_simplify(text, expected):
    orig, new = apply_first(text, OT.ALGEBRAIC_SIMPLIFY)
    assert new.to_string() == expected
    for x in (-5, 0, 9):
        assert same_output(orig, new, {"x": x})


def test_dead_code_elimination_removes_instruction():
    orig, new = apply_first("x = 10\ny = 20\nprint x", OT.DEAD_CODE)
    assert new.to_string() == "x = 10\nprint x"
    assert len(orig) == 3 and same_output(orig, new)


def test_cse_replaces_with_copy():
    orig, new = apply_first("t0 = a + b\nt1 = a + b\nt2 = t0 * t1\nprint t2", OT.CSE)
    assert new.to_string() == "t0 = a + b\nt1 = t0\nt2 = t0 * t1\nprint t2"
    assert same_output(orig, new, {"a": 3, "b": 4})


def test_strength_reduction_double():
    orig, new = apply_first("t0 = x * 2\nprint t0", OT.STRENGTH_REDUCTION)
    assert new.to_string() == "t0 = x + x\nprint t0"
    assert same_output(orig, new, {"x": -13})


def test_strength_reduction_shift():
    orig, new = apply_first("t0 = 16 * x\nprint t0", OT.STRENGTH_REDUCTION)
    assert new.to_string() == "t0 = x << 4\nprint t0"
    for x in (-7, 0, 5):
        assert same_output(orig, new, {"x": x})


def test_copy_propagation_and_removal_of_dead_copy():
    orig, new = apply_first("t0 = 5\nt1 = t0 + 1\nprint t1", OT.COPY_PROPAGATION, var="t0")
    assert new.to_string() == "t1 = 5 + 1\nprint t1"
    assert same_output(orig, new)


def test_copy_propagation_keeps_copy_still_needed():
    text = "x = y\nt0 = x + 1\nifFalse c goto L0\ny = 2\nL0:\nprint x\nprint t0"
    orig, new = apply_first(text, OT.COPY_PROPAGATION, var="x")
    assert new[0].to_string() == "x = y"          # still read by "print x" after the branch
    assert new[1].to_string() == "t0 = y + 1"
    for c in (0, 1):
        assert same_output(orig, new, {"y": 4, "c": c})


def test_copy_coalescing():
    orig, new = apply_first("t7 = sum + 5\nsum = t7\nprint sum", OT.COPY_PROPAGATION, mode="coalesce")
    assert new.to_string() == "sum = sum + 5\nprint sum"
    assert same_output(orig, new, {"sum": 3})


def test_stale_opportunity_returns_unchanged_copy():
    prog = TACProgram.from_string("t0 = 3 + 5\nprint t0")
    opp = CodeAnalyzer().analyze(prog)[0]
    changed = TACProgram.from_string("t0 = x + 5\nprint t0")
    out = RuleBasedOptimizer().propose(changed, opp)
    assert out == changed and out is not changed


def test_propose_never_mutates_input():
    prog = TACProgram.from_string("t0 = 2 * 3\nx = t0\ny = 9\nt1 = x * 1\nprint t1")
    snapshot = prog.to_string()
    for opp in CodeAnalyzer().analyze(prog):
        RuleBasedOptimizer().propose(prog, opp)
    assert prog.to_string() == snapshot


def test_all_proposals_preserve_semantics_on_real_program():
    from src.frontend import compile_source
    prog = compile_source("int a = 3 + 4; int b = a * 1; int c = a + b; int d = a + b; "
                          "int dead = c * 8; for (int i = 0; i < 3; i = i + 1) { a = a + 2 * 1; } "
                          "print(c + d + a);")
    for opp in CodeAnalyzer().analyze(prog):
        assert same_output(prog, RuleBasedOptimizer().propose(prog, opp)), opp.description


# ---------------------------------------------------------------- LLM parsing
def test_llm_tac_parser_handles_listing_noise():
    text = "```\n 0 | t0 = 8\n 1 |     print t0\n```"
    prog = parse_llm_tac(text)
    assert prog is not None and prog.to_string() == "t0 = 8\nprint t0"


def test_llm_tac_parser_rejects_garbage():
    assert parse_llm_tac("this is not TAC at all") is None
    assert parse_llm_tac("goto L9") is None   # undefined label
    assert parse_llm_tac("") is None


def test_llm_tac_parser_compact_syntax():
    prog = parse_llm_tac("t1=a+b\nt2 = t1<<2\nprint t2")
    assert prog.to_string() == "t1 = a + b\nt2 = t1 << 2\nprint t2"


# ---------------------------------------------------------------- Gemini provider
class _FakeGeminiModels:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0

    def generate_content(self, model, contents, config=None):
        from types import SimpleNamespace
        self.calls += 1
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return SimpleNamespace(text=reply, candidates=[])


def _gemini_with(replies):
    from types import SimpleNamespace
    from src.agents.optimizer_llm import GeminiOptimizer
    opt = GeminiOptimizer(min_interval=0, retry_wait=0)
    from google.genai import errors
    opt._errors = errors
    opt._client = SimpleNamespace(models=_FakeGeminiModels(replies))
    opt.available = True
    return opt


def test_gemini_proposal_is_parsed():
    opt = _gemini_with(["<reasoning>fold 3 + 5</reasoning>\n<tac>\nt0 = 8\nprint t0\n</tac>"])
    cand, reason = opt.propose(TACProgram.from_string("t0 = 3 + 5\nprint t0"))
    assert cand.to_string() == "t0 = 8\nprint t0" and reason == "fold 3 + 5"


def test_gemini_rate_limit_retries_then_disables():
    from google.genai import errors
    err = errors.ClientError(429, {"error": {"code": 429, "message": "quota", "status": "RESOURCE_EXHAUSTED"}})
    opt = _gemini_with([err, err, err])    # first try + 2 retries
    cand, reason = opt.propose(TACProgram.from_string("t0 = 3 + 5\nprint t0"))
    assert cand is None and not opt.available and "quota" in reason
    assert opt._client.models.calls == 3


def test_gemini_transient_error_skips_without_disabling():
    from google.genai import errors
    err = errors.ServerError(503, {"error": {"code": 503, "message": "busy", "status": "UNAVAILABLE"}})
    opt = _gemini_with([err] * 4)          # first try + 3 retries, all overloaded
    cand, reason = opt.propose(TACProgram.from_string("t0 = 3 + 5\nprint t0"))
    assert cand is None and opt.available and "503" in reason
    assert opt._client.models.calls == 4


def test_gemini_overload_recovers_on_retry():
    from google.genai import errors
    err = errors.ServerError(503, {"error": {"code": 503, "message": "busy", "status": "UNAVAILABLE"}})
    opt = _gemini_with([err, "<reasoning>fold</reasoning><tac>t0 = 8\nprint t0</tac>"])
    cand, _ = opt.propose(TACProgram.from_string("t0 = 3 + 5\nprint t0"))
    assert cand.to_string() == "t0 = 8\nprint t0"


def test_gemini_without_key_is_unavailable(monkeypatch):
    from src.agents.optimizer_llm import GeminiOptimizer
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    opt = GeminiOptimizer()
    assert not opt.available and "GEMINI_API_KEY" in opt.unavailable_reason
    assert opt.propose(TACProgram.from_string("print 1"))[0] is None
