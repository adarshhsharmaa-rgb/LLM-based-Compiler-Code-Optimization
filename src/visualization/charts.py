"""The six result visualisations. Every function takes the list of result
records (see ``report.result_to_record``) plus an output directory, writes a
150-DPI PNG and returns its path.

Colour roles follow one fixed scheme across all charts:
  * categories keep the same categorical hue everywhere (fixed slot order);
  * proposal outcomes use status colours (accepted = good, rejected = serious,
    invalid = critical);
  * magnitudes (heatmap) use a single-hue blue ramp.
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

from .report import CATEGORIES, OPT_TYPES, TYPE_LABELS, aggregate_metrics  # noqa: E402

DPI = 150

# ---- chart chrome ----------------------------------------------------- #
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
DIM_POINT = "#d6d5ce"

# ---- categorical slots (fixed order, never cycled) --------------------- #
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
# The five categories used in the line chart take the first five slots so that
# chart only ever shows a validated adjacent run of hues.
CATEGORY_ORDER = ["arithmetic", "loops", "conditionals", "dead_code", "mixed", "nested", "repeated_expr"]
CATEGORY_COLORS = {cat: SLOTS[i] for i, cat in enumerate(CATEGORY_ORDER)}
TYPE_COLORS = {t: SLOTS[i] for i, t in enumerate(OPT_TYPES + ["LLM"])}

# ---- status colours (reserved for outcomes) ---------------------------- #
STATUS = {"accepted": "#0ca30c", "rejected": "#ec835a", "invalid": "#d03b3b"}
OUTCOME_LABELS = {"accepted": "Accepted", "rejected": "Rejected (no cost gain)",
                  "invalid": "Invalid (failed verification)"}

# ---- sequential blue ramp (100 -> 700) --------------------------------- #
BLUE_RAMP = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
             "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]


def _style() -> None:
    plt.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": ["Segoe UI", "DejaVu Sans", "sans-serif"],
        "font.size": 10,
        "text.color": INK,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.titlesize": 13,
        "axes.titleweight": "semibold",
        "axes.titlelocation": "left",
        "axes.edgecolor": BASELINE,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK_2,
        "ytick.labelcolor": INK_2,
        "legend.frameon": False,
        "legend.labelcolor": INK_2,
        "lines.linewidth": 2,
    })


def _save(fig, out_dir: str, name: str) -> str:
    plots_dir = os.path.join(out_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    path = os.path.join(plots_dir, name)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return path


def _proposals(records: list[dict]) -> list[dict]:
    return [p for r in records for p in r["proposals"]]


def _types_present(records: list[dict]) -> list[str]:
    llm = any(p["type"] == "LLM" for p in _proposals(records))
    return OPT_TYPES + (["LLM"] if llm else [])


# ====================================================================== #
# 1. Sankey (plotly)
# ====================================================================== #
def sankey_diagram(records: list[dict], out_dir: str) -> str:
    import plotly.graph_objects as go

    m = aggregate_metrics(records)
    total, verified = m["total_proposals"], m["passed_verification"]
    accepted, rejected, invalid = m["accepted"], m["rejected_no_cost_gain"], m["invalid_failed_verification"]
    props = _proposals(records)
    rule_n = sum(1 for p in props if p["source"] == "rule")
    llm_n = sum(1 for p in props if p["source"] == "llm")

    labels = [f"Total proposals<br>{total:,}", f"Passed verification<br>{verified:,}",
              f"Invalid<br>{invalid:,}", f"Accepted<br>{accepted:,}", f"Rejected (no cost gain)<br>{rejected:,}"]
    colors = ["#2a78d6", "#256abf", STATUS["invalid"], STATUS["accepted"], STATUS["rejected"]]
    source, target, value, link_colors = [0, 0, 1, 1], [1, 2, 3, 4], [verified, invalid, accepted, rejected], [
        "rgba(42,120,214,0.30)", "rgba(208,59,59,0.35)", "rgba(12,163,12,0.30)", "rgba(236,131,90,0.35)"]
    if llm_n:
        labels += [f"Rule-based<br>{rule_n:,}", f"LLM<br>{llm_n:,}"]
        colors += ["#2a78d6", "#4a3aa7"]
        source += [5, 6]
        target += [0, 0]
        value += [rule_n, llm_n]
        link_colors += ["rgba(42,120,214,0.20)", "rgba(74,58,167,0.30)"]
    keep = [i for i, v in enumerate(value) if v > 0]

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(label=labels, color=colors, pad=28, thickness=18,
                  line=dict(color=SURFACE, width=2)),
        link=dict(source=[source[i] for i in keep], target=[target[i] for i in keep],
                  value=[value[i] for i in keep], color=[link_colors[i] for i in keep]),
        textfont=dict(color=INK, size=13, family="Segoe UI, sans-serif"),
    ))
    notes = [f"Verification pass rate {m['verification_pass_rate_pct']}%  ·  "
             f"acceptance rate {m['acceptance_rate_pct']}% of verified"]
    if invalid == 0:
        notes.append("Invalid = 0: no proposal failed verification (the flow has zero width).")
    fig.update_layout(
        title=dict(text="Proposal flow: every proposal passes the verifier before the cost gate",
                   x=0.01, font=dict(size=17, color=INK)),
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(family="Segoe UI, sans-serif", color=INK_2),
        width=1200, height=620, margin=dict(l=30, r=30, t=70, b=70),
        annotations=[dict(text="<br>".join(notes), x=0.0, y=-0.1, xref="paper", yref="paper",
                          showarrow=False, align="left", font=dict(size=12, color=INK_2))],
    )
    plots_dir = os.path.join(out_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    path = os.path.join(plots_dir, "1_sankey_proposal_flow.png")
    fig.write_html(path.replace(".png", ".html"), include_plotlyjs="cdn")
    fig.write_image(path, scale=DPI / 96 * 1.0)
    return path


# ====================================================================== #
# 2. Grouped bar chart: outcome counts per optimisation type
# ====================================================================== #
def bar_chart_by_type(records: list[dict], out_dir: str) -> str:
    _style()
    types = _types_present(records)
    counts = {t: Counter() for t in types}
    for p in _proposals(records):
        if p["type"] in counts:
            counts[p["type"]][p["outcome"]] += 1
    outcomes = ["accepted", "rejected", "invalid"]
    x = np.arange(len(types))
    width = 0.27
    fig, ax = plt.subplots(figsize=(11, 5.6))
    top = max((counts[t][o] for t in types for o in outcomes), default=1) or 1
    for k, outcome in enumerate(outcomes):
        vals = [counts[t][outcome] for t in types]
        bars = ax.bar(x + (k - 1) * width, vals, width, color=STATUS[outcome],
                      edgecolor=SURFACE, linewidth=2, label=OUTCOME_LABELS[outcome])
        for bar, v in zip(bars, vals):
            ax.annotate(f"{v:,}", (bar.get_x() + bar.get_width() / 2, v),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                        fontsize=8.5, color=INK_2 if v else MUTED)
    ax.set_xticks(x, [TYPE_LABELS[t].replace(" ", chr(10)) for t in types])
    ax.set_ylabel("Number of proposals")
    ax.set_ylim(0, top * 1.12)
    ax.grid(axis="x", visible=False)
    ax.set_title("Proposal outcomes by optimization type")
    ax.legend(loc="upper left", ncols=3, bbox_to_anchor=(0, 1.0))
    return _save(fig, out_dir, "2_bar_outcomes_by_type.png")


# ====================================================================== #
# 3. Line chart: cost over iterations for 5 representative programs
# ====================================================================== #
LINE_CATEGORIES = ["arithmetic", "loops", "conditionals", "dead_code", "mixed"]


def _representative(records: list[dict], category: str) -> dict | None:
    rs = [r for r in records if r["category"] == category and len(r["cost_history"]) > 2]
    if not rs:
        return None
    median = float(np.median([r["reduction_pct"] for r in rs]))
    # closest to the category's median reduction; prefer longer trajectories on ties
    return min(rs, key=lambda r: (abs(r["reduction_pct"] - median), -len(r["cost_history"])))


def line_chart_cost_trajectory(records: list[dict], out_dir: str) -> str:
    _style()
    fig, ax = plt.subplots(figsize=(11, 5.8))
    picked = [(c, _representative(records, c)) for c in LINE_CATEGORIES]
    picked = [(c, r) for c, r in picked if r is not None]
    max_x, max_y = 0, 0.0
    ends = []
    for cat, r in picked:
        hist = r["cost_history"]
        xs = np.arange(len(hist))
        max_x = max(max_x, xs[-1])
        max_y = max(max_y, max(hist))
        name = r["program_name"].replace(".src", "")
        ax.plot(xs, hist, color=CATEGORY_COLORS[cat], linewidth=2, label=f"{name} ({cat})",
                solid_capstyle="round")
        ends.append([hist[-1], xs[-1], f"{name}  {hist[0]:.0f}→{hist[-1]:.1f}"])
    # dodge end labels vertically so none overlap
    min_gap = max_y * 0.045
    ends.sort(key=lambda e: e[0])
    label_y = []
    for y, _, _ in ends:
        label_y.append(max(y, label_y[-1] + min_gap) if label_y else y)
    for (y, x_end, text), ly in zip(ends, label_y):
        ax.annotate(text, (x_end, y), xytext=(x_end + 0.6, ly), textcoords="data", va="center",
                    fontsize=8.5, color=INK_2)
    ax.set_xlim(0, max_x * 1.22 + 1)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Agent iteration (0 = original program)")
    ax.set_ylabel("Weighted program cost")
    ax.set_title("Cost decreases as the agent accepts verified optimizations")
    ax.legend(loc="upper right", fontsize=9)
    return _save(fig, out_dir, "3_line_cost_over_iterations.png")


# ====================================================================== #
# 4. Pie chart: accepted optimisation types
# ====================================================================== #
def pie_chart_accepted_types(records: list[dict], out_dir: str) -> str:
    _style()
    counts = Counter(p["type"] for p in _proposals(records) if p["outcome"] == "accepted")
    items = sorted(((t, n) for t, n in counts.items() if n > 0), key=lambda kv: -kv[1])
    total = sum(n for _, n in items) or 1
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.grid(False)
    if not items:
        ax.text(0.5, 0.5, "No accepted optimizations", ha="center", va="center", color=INK_2)
        ax.axis("off")
        return _save(fig, out_dir, "4_pie_accepted_types.png")
    wedges, _ = ax.pie([n for _, n in items], colors=[TYPE_COLORS[t] for t, _ in items],
                       startangle=90, counterclock=False,
                       wedgeprops=dict(edgecolor=SURFACE, linewidth=2, width=0.42))
    for w, (_, n) in zip(wedges, items):
        share = n / total
        if share >= 0.05:
            angle = np.deg2rad((w.theta1 + w.theta2) / 2)
            ax.text(0.79 * np.cos(angle), 0.79 * np.sin(angle), f"{share:.0%}",
                    ha="center", va="center", fontsize=10, color="#ffffff", fontweight="semibold")
    ax.text(0, 0.06, f"{total:,}", ha="center", va="center", fontsize=20, color=INK, fontweight="semibold")
    ax.text(0, -0.12, "accepted", ha="center", va="center", fontsize=10, color=INK_2)
    ax.legend(wedges, [f"{TYPE_LABELS[t]}  —  {n:,} ({n / total:.1%})" for t, n in items],
              loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=10, handlelength=1.2)
    ax.set_aspect("equal")
    ax.set_title("Share of accepted optimizations by type")
    return _save(fig, out_dir, "4_pie_accepted_types.png")


# ====================================================================== #
# 5. Scatter: steps vs improvement, small multiples by category
# ====================================================================== #
def _trend(ax, xs, ys, color, style="-"):
    if len(set(xs)) < 2:
        return None
    slope, intercept = np.polyfit(xs, ys, 1)
    gx = np.linspace(min(xs), max(xs), 200)
    gy = slope * gx + intercept
    inside = gy <= 100          # a cost reduction cannot exceed 100%
    ax.plot(gx[inside], gy[inside], style, color=color, linewidth=2)
    return slope


def scatter_steps_vs_improvement(records: list[dict], out_dir: str) -> str:
    _style()
    cats = [c for c in CATEGORIES if any(r["category"] == c for r in records)]
    fig, axes = plt.subplots(2, 4, figsize=(15, 7.4), sharex=True, sharey=True)
    all_x = np.array([r["iterations"] for r in records], dtype=float)
    all_y = np.array([r["reduction_pct"] for r in records], dtype=float)
    rng = np.random.default_rng(0)
    jitter = rng.uniform(-0.25, 0.25, size=len(records))
    for ax, cat in zip(axes.flat, cats):
        mask = np.array([r["category"] == cat for r in records])
        ax.scatter(all_x[~mask] + jitter[~mask], all_y[~mask], s=10, color=DIM_POINT, linewidths=0)
        ax.scatter(all_x[mask] + jitter[mask], all_y[mask], s=34, color=CATEGORY_COLORS[cat],
                   edgecolors=SURFACE, linewidths=1.2, alpha=0.9)
        slope = _trend(ax, all_x[mask], all_y[mask], INK)
        ax.set_title(cat, fontsize=11, color=INK)
        if slope is not None:
            ax.text(0.98, 0.04, f"trend {slope:+.2f} pp/step", transform=ax.transAxes,
                    ha="right", fontsize=8.5, color=INK_2)
    overall = axes.flat[len(cats)] if len(cats) < 8 else None
    if overall is not None:
        overall.scatter(all_x + jitter, all_y, s=12, color=SLOTS[0], alpha=0.55, linewidths=0)
        slope = _trend(overall, all_x, all_y, INK)
        overall.set_title("all programs", fontsize=11, color=INK)
        if slope is not None:
            overall.text(0.98, 0.04, f"trend {slope:+.2f} pp/step", transform=overall.transAxes,
                         ha="right", fontsize=8.5, color=INK_2)
        for ax in axes.flat[len(cats) + 1:]:
            ax.axis("off")
    axes.flat[0].set_ylim(min(45.0, float(all_y.min()) - 3), 102)
    for ax in axes[1]:
        ax.set_xlabel("Agent steps (iterations)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Cost improvement (%)")
    fig.suptitle("Agent steps vs. cost improvement per program (black line = linear trend)",
                 x=0.01, ha="left", fontsize=14, fontweight="semibold", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return _save(fig, out_dir, "5_scatter_steps_vs_improvement.png")


# ====================================================================== #
# 6. Heatmap: category x optimisation type (accepted counts)
# ====================================================================== #
def heatmap_category_type(records: list[dict], out_dir: str) -> str:
    _style()
    types = _types_present(records)
    cats = [c for c in CATEGORIES if any(r["category"] == c for r in records)]
    grid = np.zeros((len(cats), len(types)), dtype=int)
    for r in records:
        if r["category"] not in cats:
            continue
        for p in r["proposals"]:
            if p["outcome"] == "accepted" and p["type"] in types:
                grid[cats.index(r["category"]), types.index(p["type"])] += 1
    cmap = LinearSegmentedColormap.from_list("blue_ramp", BLUE_RAMP)
    fig, ax = plt.subplots(figsize=(11, 5.8))
    sns.heatmap(grid, ax=ax, cmap=cmap, annot=True, fmt=",d", linewidths=2, linecolor=SURFACE,
                xticklabels=[TYPE_LABELS[t].replace(" ", "\n") for t in types], yticklabels=cats,
                cbar_kws={"label": "Times applied (accepted)", "shrink": 0.85},
                annot_kws={"fontsize": 10})
    ax.grid(False)
    ax.tick_params(axis="both", length=0)
    ax.set_xlabel("Optimization type")
    ax.set_ylabel("Program category")
    plt.setp(ax.get_yticklabels(), rotation=0)
    plt.setp(ax.get_xticklabels(), rotation=0)
    ax.set_title("Where each optimization was applied")
    return _save(fig, out_dir, "6_heatmap_category_vs_type.png")


def generate_all_charts(records: list[dict], out_dir: str) -> list[str]:
    return [
        sankey_diagram(records, out_dir),
        bar_chart_by_type(records, out_dir),
        line_chart_cost_trajectory(records, out_dir),
        pie_chart_accepted_types(records, out_dir),
        scatter_steps_vs_improvement(records, out_dir),
        heatmap_category_type(records, out_dir),
    ]


# ====================================================================== #
# 7. (optional) Comparison: baseline run vs current run per category
# ====================================================================== #
def comparison_chart(cmp: dict, out_dir: str, base_label: str = "Rule-based only",
                     cur_label: str = "Rule-based + LLM") -> str | None:
    if not cmp.get("programs_compared"):
        return None
    _style()
    cats = list(cmp["per_category"])
    base = [cmp["per_category"][c]["baseline_avg_reduction_pct"] for c in cats]
    cur = [cmp["per_category"][c]["current_avg_reduction_pct"] for c in cats]
    x = np.arange(len(cats))
    width = 0.38
    fig, ax = plt.subplots(figsize=(11, 5.6))
    for offset, vals, color, label in ((-width / 2, base, SLOTS[0], base_label),
                                       (width / 2, cur, SLOTS[1], cur_label)):
        bars = ax.bar(x + offset, vals, width, color=color, edgecolor=SURFACE, linewidth=2, label=label)
        for bar, v in zip(bars, vals):
            ax.annotate(f"{v:.1f}", (bar.get_x() + bar.get_width() / 2, v), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=8.5, color=INK_2)
    ax.set_xticks(x, cats)
    ax.set_ylim(0, 108)
    ax.set_ylabel("Average cost reduction (%)")
    ax.grid(axis="x", visible=False)
    o = cmp["overall"]
    ax.set_title(f"Average cost reduction by category: {o['baseline_avg_reduction_pct']:.1f}% \u2192 "
                 f"{o['current_avg_reduction_pct']:.1f}% overall")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncols=2)
    return _save(fig, out_dir, "7_comparison_rule_vs_llm.png")
