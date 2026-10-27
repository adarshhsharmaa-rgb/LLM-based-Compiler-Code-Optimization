"""The result charts with the three LLM runs next to each other.

``charts.py`` draws one chart for one run. Here every kind of chart is drawn once for several
runs, one panel per run, so the runs can be compared at a glance: the proposal flow, the
outcomes per optimization type, the cost over iterations, the accepted types, steps against
improvement, the category heatmap and the rules-only baseline against rules + LLM.

``layout="slide"`` puts the panels in a row for a 16:9 slide, ``layout="half"`` likewise but lower, so that
two charts fit on one slide. ``layout="page"`` is for an A4
page: panels that need the width (flow, outcomes, heatmap) go under each other, the others in a
row with one legend below.

    runs = [("Gemini", records), ("Groq", records), ("Ollama", records)]
    paths = draw_all(runs, baseline_records, "report_figures", "gen", layout="page")
"""
from __future__ import annotations

import os
from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from .charts import (BLUE_RAMP, CATEGORY_COLORS, DIM_POINT, DPI, INK, INK_2, LINE_CATEGORIES,  # noqa: E402
                     SHORT_TYPE_LABELS, STATUS, SURFACE, TYPE_COLORS, _representative, _style)
from .report import CATEGORIES, OPT_TYPES, TYPE_LABELS, aggregate_metrics  # noqa: E402
from .suggestions import MODEL_COLORS  # noqa: E402

TYPES = list(OPT_TYPES) + ["LLM"]
OUTCOMES = [("accepted", "Accepted"), ("rejected", "Correct, no cost gain"), ("invalid", "Wrong, blocked")]
CATEGORY_NAMES = {"arithmetic": "Arithmetic", "nested": "Nested", "repeated_expr": "Repeated expr.",
                  "dead_code": "Dead code", "loops": "Loops", "conditionals": "Conditionals", "mixed": "Mixed"}
BASELINE_COLOR = "#9a988f"


def _proposals(records):
    return [p for r in records for p in r["proposals"]]


def _figure(count: int, layout: str, stacked: bool, row_height: float = 2.0):
    """Figure and one axis per run: a row for slides, a row or a column for a page."""
    _style()
    small = layout == "page"
    size = 7 if small else 9.5          # set before the axes exist, so tick labels follow it
    plt.rcParams.update({"font.size": size, "xtick.labelsize": size, "ytick.labelsize": size,
                         "axes.labelsize": size})
    if layout in ("slide", "half"):         # "half": two charts stacked on one slide
        fig, axes = plt.subplots(1, count, figsize=(13.3, 4.5 if layout == "slide" else 3.1), squeeze=False)
    elif stacked:
        fig, axes = plt.subplots(count, 1, figsize=(6.6, row_height * count + 0.3), squeeze=False)
    else:
        fig, axes = plt.subplots(1, count, figsize=(6.9, 2.7), squeeze=False)
    return fig, list(axes.flat), small


def _title(ax, name: str, detail: str, small: bool) -> None:
    ax.set_title(name, loc="left", fontsize=8.5 if small else 12, color=MODEL_COLORS.get(name, INK),
                 fontweight="semibold", pad=(13 if small else 20) if detail else 5)
    if detail:
        ax.text(0, 1.02, detail, transform=ax.transAxes, fontsize=6.5 if small else 9, color=INK_2, va="bottom")


def _save(fig, path: str, legend=None, small: bool = False) -> str:
    if legend:
        handles, labels = legend
        fig.legend(handles, labels, loc="lower center", ncols=min(len(labels), 7), frameon=False,
                   fontsize=7 if small else 9.5, bbox_to_anchor=(0.5, -0.01))
        fig.tight_layout(rect=(0, 0.09 if small else 0.08, 1, 1))
    else:
        fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fig.savefig(path, dpi=DPI * (1.4 if small else 1.0), bbox_inches="tight")
    plt.close(fig)
    plt.rcParams.update({"font.size": 10, "xtick.labelsize": "medium", "ytick.labelsize": "medium",
                         "axes.labelsize": "medium"})
    return path


# ---------------------------------------------------------------------- 1. proposal flow
def proposal_flow(runs, path: str, layout: str = "slide") -> str:
    """Sankey diagrams: where each run's proposals went, from source through verification to the decision."""
    import plotly.graph_objects as go

    page = layout == "page"
    fig = go.Figure()
    count = len(runs)
    annotations = []
    for i, (name, records) in enumerate(runs):
        m = aggregate_metrics(records)
        props = _proposals(records)
        rule_n = sum(1 for p in props if p["source"] == "rule")
        llm_n = len(props) - rule_n
        labels = [f"Proposals {m['total_proposals']:,}", f"Correct {m['passed_verification']:,}",
                  f"Wrong {m['invalid_failed_verification']:,}", f"Accepted {m['accepted']:,}",
                  f"No gain {m['rejected_no_cost_gain']:,}", f"Rules {rule_n:,}", f"LLM {llm_n:,}"]
        colors = ["#2a78d6", "#256abf", STATUS["invalid"], STATUS["accepted"], STATUS["rejected"],
                  "#2a78d6", MODEL_COLORS.get(name, "#4a3aa7")]
        links = [(5, 0, rule_n, "rgba(42,120,214,0.20)"), (6, 0, llm_n, "rgba(74,58,167,0.35)"),
                 (0, 1, m["passed_verification"], "rgba(42,120,214,0.30)"),
                 (0, 2, m["invalid_failed_verification"], "rgba(208,59,59,0.45)"),
                 (1, 3, m["accepted"], "rgba(12,163,12,0.30)"),
                 (1, 4, m["rejected_no_cost_gain"], "rgba(236,131,90,0.40)")]
        links = [link for link in links if link[2] > 0]
        if page:
            top = 1 - i / count
            domain = dict(x=[0, 1], y=[top - 1 / count + 0.06, top - 0.06])
            annotations.append(dict(text=f"<b>{name}</b>", x=0, y=top - 0.01, xref="paper", yref="paper",
                                    showarrow=False, xanchor="left", yanchor="top",
                                    font=dict(size=17, color=MODEL_COLORS.get(name, INK))))
        else:
            left = i / count
            domain = dict(x=[left + 0.015, left + 1 / count - 0.015], y=[0, 0.9])
            annotations.append(dict(text=f"<b>{name}</b>", x=left + 0.015, y=1.0, xref="paper", yref="paper",
                                    showarrow=False, xanchor="left", yanchor="top",
                                    font=dict(size=18, color=MODEL_COLORS.get(name, INK))))
        # fixed columns: sources, all proposals, the verifier's verdict, the cost gate's decision
        node_x = [0.3, 0.62, 0.62, 0.999, 0.999, 0.001, 0.001] if page else [0.22, 0.46, 0.46, 0.999, 0.999, 0.001, 0.001]
        node_y = [0.5, 0.52, 0.02, 0.5, 0.98, 0.47, 0.98]
        fig.add_trace(go.Sankey(
            domain=domain, arrangement="fixed",
            node=dict(label=labels, color=colors, pad=16, thickness=14, line=dict(color=SURFACE, width=1),
                      x=node_x, y=node_y),
            link=dict(source=[s for s, _, _, _ in links], target=[t for _, t, _, _ in links],
                      value=[v for _, _, v, _ in links], color=[c for _, _, _, c in links]),
            textfont=dict(color=INK, size=13 if page else 12, family="Segoe UI, sans-serif")))
    fig.update_layout(paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, annotations=annotations,
                      font=dict(family="Segoe UI, sans-serif", color=INK_2),
                      width=1100 if page else 1500, height=270 * count if page else (520 if layout == "slide" else 360),
                      margin=dict(l=10, r=10, t=12, b=10))
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fig.write_image(path, scale=2)
    return path


# ---------------------------------------------------------------------- 2. outcomes per type
def outcomes_by_type(runs, path: str, layout: str = "slide") -> str:
    """Accepted, correct-but-no-gain and wrong proposals for every optimization type (log scale)."""
    fig, axes, small = _figure(len(runs), layout, stacked=True, row_height=1.75)
    top = 1
    for ax, (name, records) in zip(axes, runs):
        counts = {t: Counter() for t in TYPES}
        for p in _proposals(records):
            counts.setdefault(p["type"], Counter())[p["outcome"]] += 1
        x = np.arange(len(TYPES))
        width = 0.27
        for k, (outcome, _) in enumerate(OUTCOMES):
            values = [counts[t][outcome] for t in TYPES]
            top = max(top, max(values))
            bars = ax.bar(x + (k - 1) * width, [v or np.nan for v in values], width, color=STATUS[outcome],
                          edgecolor=SURFACE, linewidth=0.8)
            for bar, v in zip(bars, values):
                if v:
                    ax.annotate(f"{v:,}", (bar.get_x() + bar.get_width() / 2, v), xytext=(0, 2),
                                textcoords="offset points", ha="center", va="bottom", rotation=90,
                                fontsize=5.5 if small else 7.5, color=INK_2)
        ax.set_yscale("log")
        ax.set_xticks(x, [SHORT_TYPE_LABELS[t].replace("\n", " ") if small else SHORT_TYPE_LABELS[t] for t in TYPES],
                      fontsize=6.5 if small else 8.5)
        ax.grid(axis="x", visible=False)
        llm = counts["LLM"]
        _title(ax, name, f"LLM: {llm['accepted']} accepted, {llm['rejected']} no gain, {llm['invalid']} wrong", small)
    for ax in axes:
        ax.set_ylim(0.8, top * 12)
    axes[0].set_ylabel("Proposals (log scale)")
    if small:
        for ax in axes:
            ax.set_ylabel("Proposals (log)")
    handles = [Patch(color=STATUS[o]) for o, _ in OUTCOMES]
    return _save(fig, path, (handles, [label for _, label in OUTCOMES]), small)


# ---------------------------------------------------------------------- 3. cost over iterations
def cost_over_iterations(runs, path: str, layout: str = "slide") -> str:
    """The weighted cost after every step, for one typical program of five categories."""
    fig, axes, small = _figure(len(runs), layout, stacked=False)
    for ax, (name, records) in zip(axes, runs):
        longest = 0
        for category in LINE_CATEGORIES:
            record = _representative(records, category)
            if record is None:
                continue
            history = record["cost_history"]
            longest = max(longest, len(history))
            ax.plot(range(len(history)), history, color=CATEGORY_COLORS[category], linewidth=1.4 if small else 2)
        ax.set_xlim(0, longest)
        ax.set_ylim(bottom=0)
        ax.set_xlabel("Iteration")
        _title(ax, name, "", small)
    axes[0].set_ylabel("Weighted cost")
    handles = [plt.Line2D([], [], color=CATEGORY_COLORS[c], linewidth=2) for c in LINE_CATEGORIES]
    return _save(fig, path, (handles, [CATEGORY_NAMES[c] for c in LINE_CATEGORIES]), small)


# ---------------------------------------------------------------------- 4. accepted types
def accepted_types(runs, path: str, layout: str = "slide") -> str:
    """Donut charts: the share of every optimization type among the accepted changes."""
    fig, axes, small = _figure(len(runs), layout, stacked=False)
    present = set()
    for ax, (name, records) in zip(axes, runs):
        counts = Counter(p["type"] for p in _proposals(records) if p["outcome"] == "accepted")
        items = [(t, counts[t]) for t in TYPES if counts[t]]
        present.update(t for t, _ in items)
        total = sum(v for _, v in items) or 1
        ax.grid(False)
        wedges, _ = ax.pie([v for _, v in items], colors=[TYPE_COLORS[t] for t, _ in items], startangle=90,
                           counterclock=False, wedgeprops=dict(edgecolor=SURFACE, linewidth=1.2, width=0.42))
        for wedge, (_, v) in zip(wedges, items):
            if v / total >= 0.07:
                angle = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
                ax.text(0.79 * np.cos(angle), 0.79 * np.sin(angle), f"{v / total:.0%}", ha="center", va="center",
                        fontsize=6.5 if small else 9, color="#ffffff", fontweight="semibold")
        ax.text(0, 0.05, f"{total:,}", ha="center", va="center", fontsize=10 if small else 15, color=INK,
                fontweight="semibold")
        ax.text(0, -0.17, "accepted", ha="center", va="center", fontsize=6.5 if small else 9, color=INK_2)
        llm_share = counts["LLM"] / total
        ax.set_title(name, loc="center", fontsize=9.5 if small else 12, color=MODEL_COLORS.get(name, INK),
                     fontweight="semibold")
        ax.text(0.5, -0.04, f"LLM: {counts['LLM']:,} ({llm_share:.1%})", transform=ax.transAxes, ha="center",
                fontsize=7 if small else 9.5, color=INK_2)
        ax.set_aspect("equal")
    kinds = [t for t in TYPES if t in present]
    handles = [Patch(color=TYPE_COLORS[t]) for t in kinds]
    return _save(fig, path, (handles, [TYPE_LABELS.get(t, "LLM proposal") for t in kinds]), small)


# ---------------------------------------------------------------------- 5. steps against improvement
def steps_vs_improvement(runs, path: str, layout: str = "slide") -> str:
    """Every program: how many steps the agent took and how much cheaper the program became."""
    fig, axes, small = _figure(len(runs), layout, stacked=False)
    rng = np.random.default_rng(0)
    low = 100.0
    for ax, (name, records) in zip(axes, runs):
        xs = np.array([r["iterations"] for r in records], dtype=float)
        ys = np.array([r["reduction_pct"] for r in records], dtype=float)
        low = min(low, float(ys.min()))
        colors = [CATEGORY_COLORS.get(r["category"], DIM_POINT) for r in records]
        ax.scatter(xs + rng.uniform(-0.3, 0.3, len(xs)), ys, s=5 if small else 12, c=colors, alpha=0.7, linewidths=0)
        detail = ""
        if len(set(xs)) > 1:
            slope, intercept = np.polyfit(xs, ys, 1)
            grid = np.linspace(xs.min(), xs.max(), 100)
            line = slope * grid + intercept
            keep = line <= 100
            ax.plot(grid[keep], line[keep], color=INK, linewidth=1.2)
            detail = f"trend {slope:+.2f} points per step"
        ax.set_xlabel("Steps (iterations)")
        _title(ax, name, detail, small)
    for ax in axes:
        ax.set_ylim(max(0.0, low - 5), 102)
    axes[0].set_ylabel("Cost reduction (%)")
    handles = [plt.Line2D([], [], marker="o", linestyle="", color=CATEGORY_COLORS[c]) for c in CATEGORIES]
    return _save(fig, path, (handles, [CATEGORY_NAMES[c] for c in CATEGORIES]), small)


# ---------------------------------------------------------------------- 6. category heatmap
def category_heatmap(runs, path: str, layout: str = "slide") -> str:
    """Accepted changes per program category and optimization type, on one colour scale for all runs."""
    fig, axes, small = _figure(len(runs), layout, stacked=True, row_height=1.95)
    grids = []
    for _, records in runs:
        grid = np.zeros((len(CATEGORIES), len(TYPES)), dtype=int)
        for r in records:
            for p in r["proposals"]:
                if p["outcome"] == "accepted" and p["type"] in TYPES and r["category"] in CATEGORIES:
                    grid[CATEGORIES.index(r["category"]), TYPES.index(p["type"])] += 1
        grids.append(grid)
    vmax = max(int(g.max()) for g in grids) or 1
    cmap = LinearSegmentedColormap.from_list("blue_ramp", BLUE_RAMP)
    for i, (ax, (name, _), grid) in enumerate(zip(axes, runs, grids)):
        first = i == 0 or small
        sns.heatmap(grid, ax=ax, cmap=cmap, vmin=0, vmax=vmax, annot=True, fmt=",d", cbar=False,
                    linewidths=1, linecolor=SURFACE, annot_kws={"fontsize": 6 if small else 8},
                    xticklabels=[SHORT_TYPE_LABELS[t].replace("\n", " ") if small else SHORT_TYPE_LABELS[t]
                                 for t in TYPES],
                    yticklabels=[CATEGORY_NAMES[c] for c in CATEGORIES] if first else False)
        ax.tick_params(axis="both", length=0, labelsize=6.5 if small else 8.5)
        plt.setp(ax.get_yticklabels(), rotation=0)
        plt.setp(ax.get_xticklabels(), rotation=0)
        _title(ax, name, f"LLM changes accepted: {int(grid[:, -1].sum()):,}", small)
    return _save(fig, path, None, small)


# ---------------------------------------------------------------------- 7. rules alone against rules + LLM
def rules_vs_llm(runs, baseline, path: str, layout: str = "slide") -> str:
    """Average cost reduction per category: the rules-only run against each run with an LLM."""
    fig, axes, small = _figure(len(runs), layout, stacked=False)
    base = {r["program_name"]: r["reduction_pct"] for r in baseline}
    y = np.arange(len(CATEGORIES))
    for i, (ax, (name, records)) in enumerate(zip(axes, runs)):
        before, after = [], []
        for category in CATEGORIES:
            chosen = [r for r in records if r["category"] == category and r["program_name"] in base]
            before.append(float(np.mean([base[r["program_name"]] for r in chosen])) if chosen else 0.0)
            after.append(float(np.mean([r["reduction_pct"] for r in chosen])) if chosen else 0.0)
        height = 0.38
        for offset, values, color in ((-height / 2, before, BASELINE_COLOR), (height / 2, after, MODEL_COLORS.get(name))):
            bars = ax.barh(y + offset, values, height, color=color, edgecolor=SURFACE, linewidth=0.6)
            for bar, v in zip(bars, values):
                ax.annotate(f"{v:.1f}", (v, bar.get_y() + bar.get_height() / 2), xytext=(2, 0),
                            textcoords="offset points", va="center", fontsize=5.5 if small else 8, color=INK_2)
        ax.set_yticks(y, [CATEGORY_NAMES[c] for c in CATEGORIES] if i == 0 else [""] * len(CATEGORIES))
        ax.invert_yaxis()
        ax.set_xlim(0, 112)
        ax.set_xlabel("Average cost reduction (%)")
        ax.grid(axis="y", visible=False)
        overall_before = float(np.mean([base[r["program_name"]] for r in records if r["program_name"] in base]))
        overall_after = float(np.mean([r["reduction_pct"] for r in records if r["program_name"] in base]))
        _title(ax, name, f"all programs: {overall_before:.1f}% → {overall_after:.1f}%", small)
    handles = [Patch(color=BASELINE_COLOR)] + [Patch(color=MODEL_COLORS.get(name)) for name, _ in runs]
    labels = ["Rules only"] + [f"Rules + {name}" for name, _ in runs]
    return _save(fig, path, (handles, labels), small)


CHARTS = [
    ("flow", "Proposal Flow", proposal_flow),
    ("outcomes", "Outcomes by Optimization Type", outcomes_by_type),
    ("accepted", "Accepted Optimizations by Type", accepted_types),
    ("cost", "Cost over Iterations", cost_over_iterations),
    ("steps", "Steps against Improvement", steps_vs_improvement),
    ("heatmap", "Where the Optimizations Were Applied", category_heatmap),
    ("rules_vs_llm", "Rules Only against Rules + LLM", None),
]


def draw_all(runs, baseline, out_dir: str, prefix: str, layout: str = "slide") -> dict[str, str]:
    """Every chart for these runs; returns {chart key: path}. Files are named ``<prefix>_<key>.png``."""
    paths = {}
    for key, _, draw in CHARTS:
        path = os.path.join(out_dir, f"{prefix}_{key}.png")
        paths[key] = rules_vs_llm(runs, baseline, path, layout) if draw is None else draw(runs, path, layout)
    return paths


# ---------------------------------------------------------------------- what the charts show, in words
FRIENDLY = {"CONSTANT_FOLD": "constant folding", "ALGEBRAIC_SIMPLIFY": "algebraic simplification",
            "DEAD_CODE": "dead code elimination", "CSE": "common subexpression elimination",
            "STRENGTH_REDUCTION": "strength reduction", "COPY_PROPAGATION": "copy propagation", "LLM": "the LLM"}
PLAIN_CATEGORY = {"arithmetic": "arithmetic", "nested": "nested-expression", "repeated_expr": "repeated-expression",
                  "dead_code": "dead-code", "loops": "loop", "conditionals": "conditional", "mixed": "mixed"}


def _names(items) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _capital(text: str) -> str:
    return text[0].upper() + text[1:]


def describe(runs, baseline, accepted_note: str = "") -> dict[str, tuple[str, str]]:
    """For every chart key: (a paragraph for the report, a short line for a slide), worked out from the data.

    The text is plain: percentages are written with "%" and negative numbers with "-".
    """
    import statistics

    from .suggestions import by_type, llm_by_category

    models = [name for name, _ in runs]
    metrics = {name: aggregate_metrics(r) for name, r in runs}
    types = {name: by_type(r) for name, r in runs}
    base = {r["program_name"]: r["reduction_pct"] for r in baseline}
    out = {}

    # 1. flow
    wrong = [f"{metrics[k]['invalid_failed_verification']:,} of {k}'s {metrics[k]['total_proposals']:,}" for k in models]
    wrong[0] += " proposals"
    out["flow"] = (
        "The diagrams follow every proposal of a run from where it came from, the rules or the LLM, through the "
        "verifier to the cost check. A wrong proposal ends at the verifier and never reaches the program. The wrong "
        "ones are " + _names(wrong) + "; everything that gets to the right-hand side was checked first.",
        "Wrong proposals stop at the verifier: "
        + _names(f"{metrics[k]['invalid_failed_verification']:,} for {k}" for k in models)
        + ". Nothing reaches the program without being checked.")

    # 2. outcomes
    rule_kinds = [t for t in TYPES if t != "LLM" and min(types[k][t]["suggested"] for k in models) >= 50]
    spread = max((max(types[k][t]["suggested"] for k in models) / min(types[k][t]["suggested"] for k in models)
                  for t in rule_kinds), default=1.0)
    alike = ("look almost the same in the three runs, because the rules do not change between them" if spread <= 1.15
             else "are similar in the three runs but not identical, because an accepted LLM change alters what the "
                  "rules find next")
    worse = [k for k in models if types[k]["LLM"]["wrong"] > types[k]["LLM"]["accepted"]]
    llm_counts = _names(f"{k} had {types[k]['LLM']['accepted']} accepted and {types[k]['LLM']['wrong']} wrong"
                        for k in models)
    out["outcomes"] = (
        f"The bars of the six rules {alike}. The difference is in the last group, the LLM's own proposals: "
        + llm_counts + "." + (f" For {_names(worse)} the wrong answers outnumber the accepted ones." if worse else "")
        + " The scale is logarithmic; on a normal scale every bar next to copy propagation would be too small to read.",
        ("The rule bars hardly change between runs. " if spread <= 1.15 else "The rule bars are similar between runs. ")
        + "The LLM group is where they differ: "
        + _names(f"{k} {types[k]['LLM']['accepted']} accepted / {types[k]['LLM']['wrong']} wrong" for k in models) + ".")

    # 3. accepted types
    accepted = {k: {t: types[k][t]["accepted"] for t in TYPES} for k in models}
    totals = {k: sum(accepted[k].values()) or 1 for k in models}
    ranked = sorted((t for t in TYPES if t != "LLM"), key=lambda t: -sum(accepted[k][t] for k in models))
    shares = [100 * accepted[k][ranked[0]] / totals[k] for k in models]
    llm_share = _names(f"{100 * accepted[k]['LLM'] / totals[k]:.1f}% for {k}" for k in models)
    top = _capital(FRIENDLY[ranked[0]])
    out["accepted"] = (
        f"{top} makes up between {min(shares):.0f}% and {max(shares):.0f}% of the accepted changes in every run, "
        f"followed by {FRIENDLY[ranked[1]]} and {FRIENDLY[ranked[2]]}. The LLM's slice is small: {llm_share}. "
        + accepted_note,
        f"{top} is {min(shares):.0f}-{max(shares):.0f}% of the accepted changes in every run. "
        f"The LLM's slice: {llm_share}.")

    # 4. cost over iterations
    steep = []
    for k, records in runs:
        for category in LINE_CATEGORIES:
            record = _representative(records, category)
            if record is None:
                continue
            history = record["cost_history"]
            kinds = {p["iteration"]: p["type"] for p in record["proposals"] if p["outcome"] == "accepted"}
            if k not in steep and any(history[i - 1] - history[i] >= 0.2 * history[0] and kinds.get(i) == "LLM"
                                      for i in range(1, len(history))):
                steep.append(k)
    out["cost"] = (
        "Each line is one program of a category, the one whose reduction is closest to the middle of that category. "
        "The cost falls a little with almost every step, because most steps remove a single copy or temporary. "
        + (f"The steep drops in the {_names(steep)} panels are LLM changes that replaced a larger piece of code in "
           "one step." if steep else
           "No single step removes much at once here; the LLM changes in these programs are small ones."),
        "Most steps remove one copy or one temporary. "
        + (f"The steep drops ({_names(steep)}) are LLM steps that replace a larger piece of code at once."
           if steep else "No single step removes much at once."))

    # 5. steps against improvement
    slopes = []
    for _, records in runs:
        xs = [r["iterations"] for r in records]
        ys = [r["reduction_pct"] for r in records]
        slopes.append(statistics.linear_regression(xs, ys).slope if len(set(xs)) > 1 else 0.0)
    slope_text = _names(f"{s:+.2f}" for s in slopes)
    if all(abs(s) < 0.1 for s in slopes):
        out["steps"] = (
            f"The fitted line is almost flat ({slope_text} percentage points per step for {_names(models)}). On these "
            "programs the number of steps says little about how much a program shrinks: a long program needs many "
            "steps, but it also keeps more of its work. The colours of the categories are mixed together for the "
            "same reason.",
            f"Almost flat ({slope_text} points per step): the number of steps says little about the gain here.")
    else:
        out["steps"] = (
            ("Programs that take more steps tend to end up cheaper, because a long run usually means there was more "
             "redundant code to remove. " if all(s > 0 for s in slopes) else "")
            + f"The fitted line changes by {slope_text} percentage points per step for {_names(models)}. The programs "
            "of one category stay close together, so how much a program shrinks depends more on its category than "
            "on the model.",
            f"More steps, cheaper result: the fitted line changes by {slope_text} points per step. Each category "
            "stays in its own band.")

    # 6. heatmap
    column = {t: sum(accepted[k][t] for k in models) for t in TYPES}
    darkest = _capital(FRIENDLY[max((t for t in TYPES if t != "LLM"), key=lambda t: column[t])])
    per_category = [llm_by_category(records) for _, records in runs]
    llm_cells = {c: sum(counts[c]["accepted"] for counts in per_category) for c in CATEGORIES}
    busiest = _names(PLAIN_CATEGORY[c] for c in sorted(llm_cells, key=lambda c: -llm_cells[c])[:3])
    out["heatmap"] = (
        f"{darkest} is the darkest column in every run, and the rule columns look much the same in all three "
        f"panels. The column that differs is the last one: the accepted LLM changes fall mostly in {busiest} programs.",
        f"{darkest} dominates every run. The accepted LLM changes (last column) sit mostly in {busiest} programs.")

    # 7. rules only against rules + LLM
    lines, biggest, before = [], {}, 0.0
    for k, records in runs:
        chosen = [r for r in records if r["program_name"] in base]
        before = statistics.mean(base[r["program_name"]] for r in chosen)
        lines.append(f"{statistics.mean(r['reduction_pct'] for r in chosen):.1f}% with {k}")
        gains = {}
        for category in CATEGORIES:
            in_category = [r for r in chosen if r["category"] == category]
            if in_category:
                gains[category] = statistics.mean(r["reduction_pct"] - base[r["program_name"]] for r in in_category)
        biggest[k] = max(gains, key=gains.get)
    if len(set(biggest.values())) == 1:
        where = f"the {PLAIN_CATEGORY[next(iter(biggest.values()))]} category for all three"
    else:
        where = _names(f"the {PLAIN_CATEGORY[c]} category for {_names(k for k, v in biggest.items() if v == c)}"
                       for c in dict.fromkeys(biggest.values()))
    out["rules_vs_llm"] = (
        f"The grey bars are the rules alone ({before:.1f}% on average); the coloured bars add one LLM: "
        + _names(lines) + f". The biggest gain is in {where}.",
        f"Rules alone {before:.1f}%; " + _names(lines) + f". Biggest gain: {where}.")
    return out
