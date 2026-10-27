"""Tests for the counts and charts of correct and wrong suggestions (src/visualization/suggestions.py)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.visualization import suggestions as sg  # noqa: E402


def proposal(source, kind, outcome):
    return {"source": source, "type": kind, "outcome": outcome}


RECORDS = [
    {"category": "loops", "proposals": [proposal("rule", "DEAD_CODE", "accepted"),
                                        proposal("rule", "STRENGTH_REDUCTION", "rejected"),
                                        proposal("llm", "LLM", "invalid"),
                                        proposal("llm", "LLM", "accepted")]},
    {"category": "mixed", "proposals": [proposal("rule", "DEAD_CODE", "accepted"),
                                        proposal("llm", "LLM", "rejected")]},
]


def test_a_suggestion_is_correct_when_it_passed_verification():
    counts = sg.by_type(RECORDS)
    assert counts["DEAD_CODE"] == {"suggested": 2, "correct": 2, "accepted": 2, "no_gain": 0, "wrong": 0}
    assert counts["STRENGTH_REDUCTION"]["correct"] == 1 and counts["STRENGTH_REDUCTION"]["no_gain"] == 1
    assert counts["LLM"] == {"suggested": 3, "correct": 2, "accepted": 1, "no_gain": 1, "wrong": 1}
    assert counts["CSE"]["suggested"] == 0             # a type nobody suggested is still listed


def test_llm_counts_per_category_leave_the_rules_out():
    counts = sg.llm_by_category(RECORDS)
    assert (counts["loops"]["correct"], counts["loops"]["wrong"]) == (1, 1)
    assert (counts["mixed"]["correct"], counts["mixed"]["wrong"]) == (1, 0)
    assert counts["arithmetic"]["suggested"] == 0


def test_the_wrong_suggestions_get_a_chart_of_their_own(tmp_path):
    panels = [("One dataset", {"Gemini": RECORDS, "Ollama": RECORDS})]
    for field in ("correct", "wrong"):
        path = sg.category_chart(panels, field, str(tmp_path / f"{field}.png"), field, stacked=True)
        assert os.path.getsize(path) > 5000
