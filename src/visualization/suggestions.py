"""Suggestions per optimization type and per model: how many were correct and how many were wrong.

A suggestion is *correct* when it passed verification (it was then accepted, or turned down
only because it did not make the program cheaper) and *wrong* when the verifier rejected it.
The counts come from the ``proposals`` list of every result record, so they can be drawn for
any finished run. The two charts keep the correct and the wrong suggestions apart: one chart
each, per program category and per LLM.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .charts import DPI, INK, INK_2, _style  # noqa: E402
from .report import CATEGORIES, OPT_TYPES  # noqa: E402

TYPES = list(OPT_TYPES) + ["LLM"]
MODEL_COLORS = {"Gemini": "#2a78d6", "Groq": "#eda100", "Ollama": "#1baf7a"}
CATEGORY_LABELS = {"arithmetic": "Arithmetic", "nested": "Nested", "repeated_expr": "Repeated\nexpr.",
                   "dead_code": "Dead\ncode", "loops": "Loops", "conditionals": "Conditionals", "mixed": "Mixed"}


def _empty() -> dict[str, int]:
    return {"suggested": 0, "correct": 0, "accepted": 0, "no_gain": 0, "wrong": 0}


def _add(counts: dict[str, int], outcome: str) -> None:
    counts["suggested"] += 1
    if outcome == "invalid":
        counts["wrong"] += 1
        return
    counts["correct"] += 1
    counts["accepted" if outcome == "accepted" else "no_gain"] += 1


def by_type(records: list[dict]) -> dict[str, dict[str, int]]:
    """Counts for every optimization type (the six rules and ``LLM``)."""
    counts = {kind: _empty() for kind in TYPES}
    for record in records:
        for proposal in record["proposals"]:
            _add(counts.setdefault(proposal["type"], _empty()), proposal["outcome"])
    return counts


def llm_by_category(records: list[dict]) -> dict[str, dict[str, int]]:
    """Counts of the LLM's suggestions for every program category."""
    counts = {category: _empty() for category in CATEGORIES}
    for record in records:
        for proposal in record["proposals"]:
            if proposal["source"] == "llm":
                _add(counts.setdefault(record["category"], _empty()), proposal["outcome"])
    return counts


def category_chart(panels: list[tuple[str, dict[str, list[dict]]]], field: str, path: str, title: str,
                   stacked: bool = False, size: tuple[float, float] | None = None) -> str:
    """Grouped bars: program categories along the axis, one bar per LLM.

    ``panels`` is [(panel title, {model name: records})], one panel per dataset; ``field`` is
    ``"correct"`` or ``"wrong"``. ``stacked`` puts the panels under each other (for a page)
    instead of side by side (for a slide).
    """
    _style()
    rows, cols = (len(panels), 1) if stacked else (1, len(panels))
    figsize = size or ((7.2, 3.3 * rows) if stacked else (6.4 * cols, 3.9))
    fig, axes = plt.subplots(rows, cols, figsize=figsize, squeeze=False)
    top = 1
    for ax, (panel, runs) in zip(axes.flat, panels):
        x = np.arange(len(CATEGORIES))
        width = 0.8 / max(len(runs), 1)
        for i, (model, records) in enumerate(runs.items()):
            counts = llm_by_category(records)
            values = [counts[category][field] for category in CATEGORIES]
            bars = ax.bar(x + (i - (len(runs) - 1) / 2) * width, values, width * 0.92,
                          color=MODEL_COLORS.get(model), label=f"{model} ({sum(values)})")
            ax.bar_label(bars, fontsize=7.5, color=INK_2, padding=1.5)
            top = max(top, max(values))
        ax.set_xticks(x, [CATEGORY_LABELS.get(category, category) for category in CATEGORIES], fontsize=8.5)
        ax.set_title(panel, fontsize=11, color=INK, loc="left", pad=8)
        ax.set_ylabel("LLM suggestions", fontsize=9)
        ax.legend(fontsize=8.5, frameon=False, title="Model (total)", title_fontsize=8.5)
    for ax in axes.flat:
        ax.set_ylim(0, top * 1.14)
    fig.suptitle(title, fontsize=12.5, fontweight="bold", color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return path
