"""Tests for the result charts with several LLM runs side by side (src/visualization/model_charts.py)."""
import json
import os
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from src.visualization import model_charts as mc  # noqa: E402


def records(folder, count=60):
    path = os.path.join(ROOT, folder, "metrics", "results.json")
    if not os.path.exists(path):
        pytest.skip(f"{folder} has no results")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)[:count]


@pytest.fixture(scope="module")
def runs():
    return [("Gemini", records("output")), ("Groq", records("output_groq")), ("Ollama", records("output_ollama"))]


@pytest.fixture(scope="module")
def baseline():
    return records("output_rule_only", 500)


@pytest.mark.parametrize("layout", ["page", "slide"])
def test_every_chart_is_drawn_for_all_runs(runs, baseline, tmp_path, layout):
    paths = mc.draw_all(runs, baseline, str(tmp_path), "t", layout)
    assert sorted(paths) == sorted(key for key, _, _ in mc.CHARTS)
    for path in paths.values():
        assert os.path.getsize(path) > 10_000


def test_the_descriptions_quote_the_data(runs, baseline):
    text = mc.describe(runs, baseline)
    assert sorted(text) == sorted(key for key, _, _ in mc.CHARTS)
    for long, short in text.values():
        assert long and short and len(short) < len(long)
    wrong = sum(1 for _, rs in runs[:1] for r in rs for p in r["proposals"] if p["outcome"] == "invalid")
    assert f"{wrong} for Gemini" in text["flow"][1]
    assert "Gemini" in text["rules_vs_llm"][0] and "%" in text["rules_vs_llm"][0]
