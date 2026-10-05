"""Metrics aggregation and CSV/JSON export.

Results are first converted to plain-dict *records* (``result_to_record``) so
they can be saved to ``output/metrics/results.json`` and later reloaded by
``--visualize`` without re-running the optimizer.
"""
from __future__ import annotations

import csv
import json
import os
import re
import statistics
from collections import Counter

CATEGORIES = ["arithmetic", "nested", "repeated_expr", "dead_code", "loops", "conditionals", "mixed"]
OPT_TYPES = ["CONSTANT_FOLD", "ALGEBRAIC_SIMPLIFY", "DEAD_CODE", "CSE",
             "STRENGTH_REDUCTION", "COPY_PROPAGATION"]
TYPE_LABELS = {
    "CONSTANT_FOLD": "Constant Fold",
    "ALGEBRAIC_SIMPLIFY": "Algebraic Simplify",
    "DEAD_CODE": "Dead Code",
    "CSE": "CSE",
    "STRENGTH_REDUCTION": "Strength Reduction",
    "COPY_PROPAGATION": "Copy Propagation",
    "LLM": "LLM Proposal",
}

PER_PROGRAM_COLUMNS = ["program_name", "category", "original_cost", "final_cost", "reduction_pct",
                       "iterations", "accepted", "rejected", "invalid", "output_match"]


def infer_category(name: str, path: str | None = None) -> str:
    if path:
        parent = os.path.basename(os.path.dirname(os.path.abspath(path)))
        if parent in CATEGORIES:
            return parent
    stem = re.sub(r"_\d+(\.src)?$", "", os.path.basename(name))
    return stem if stem in CATEGORIES else "uncategorized"


def result_to_record(result, category: str) -> dict:
    return {
        "program_name": result.program_name,
        "category": category,
        "original_cost": result.original_cost.weighted_total,
        "final_cost": result.final_cost.weighted_total,
        "reduction_pct": round(result.cost_reduction_pct, 4),
        "iterations": result.iterations,
        "accepted": result.accepted_count,
        "rejected": result.rejected_count,
        "invalid": result.invalid_count,
        "output_match": result.output_match,
        "original_instructions": len(result.original_tac),
        "final_instructions": len(result.optimized_tac),
        "types_applied": list(result.optimization_types_applied),
        "proposals": list(result.proposals),
        "cost_history": list(result.cost_history),
        "llm_proposals": result.llm_proposals,
        "llm_valid": result.llm_valid,
        "hit_iteration_cap": result.hit_iteration_cap,
        "original_cost_breakdown": result.original_cost.to_dict(),
        "final_cost_breakdown": result.final_cost.to_dict(),
    }


def _pct(num: float, den: float) -> float | None:
    return round(num / den * 100, 2) if den else None


def aggregate_metrics(records: list[dict], llm_used: bool | None = None) -> dict:
    proposals = [p for r in records for p in r["proposals"]]
    outcomes = Counter(p["outcome"] for p in proposals)
    total = len(proposals)
    verified = outcomes["accepted"] + outcomes["rejected"]
    reductions = [r["reduction_pct"] for r in records]
    iterations = [r["iterations"] for r in records]
    llm_total = sum(r["llm_proposals"] for r in records)
    llm_valid = sum(r["llm_valid"] for r in records)
    if llm_used is None:
        llm_used = llm_total > 0
    false_positives = sum(1 for r in records if not r["output_match"])

    buckets = Counter()
    for it in iterations:
        lo = (it - 1) // 10 * 10 + 1
        buckets[f"{lo}-{lo + 9}"] += 1
    distribution = dict(sorted(buckets.items(), key=lambda kv: int(kv[0].split("-")[0])))

    per_category = {}
    for cat in sorted({r["category"] for r in records},
                      key=lambda c: CATEGORIES.index(c) if c in CATEGORIES else 99):
        rs = [r for r in records if r["category"] == cat]
        per_category[cat] = {
            "programs": len(rs),
            "avg_reduction_pct": round(statistics.mean(r["reduction_pct"] for r in rs), 2),
            "avg_iterations": round(statistics.mean(r["iterations"] for r in rs), 2),
            "accepted": sum(r["accepted"] for r in rs),
        }

    by_type = {}
    for t in OPT_TYPES + (["LLM"] if llm_total else []):
        c = Counter(p["outcome"] for p in proposals if p["type"] == t)
        by_type[t] = {"accepted": c["accepted"], "rejected": c["rejected"], "invalid": c["invalid"]}

    n = len(records)
    return {
        "total_programs": n,
        "total_proposals": total,
        "passed_verification": verified,
        "accepted": outcomes["accepted"],
        "rejected_no_cost_gain": outcomes["rejected"],
        "invalid_failed_verification": outcomes["invalid"],
        "verification_pass_rate_pct": _pct(verified, total),
        "acceptance_rate_pct": _pct(outcomes["accepted"], verified),
        "avg_cost_reduction_pct": round(statistics.mean(reductions), 2) if reductions else 0.0,
        "median_cost_reduction_pct": round(statistics.median(reductions), 2) if reductions else 0.0,
        "min_cost_reduction_pct": round(min(reductions), 2) if reductions else 0.0,
        "max_cost_reduction_pct": round(max(reductions), 2) if reductions else 0.0,
        "programs_with_reduction_over_30pct": sum(1 for x in reductions if x > 30),
        "steps_to_convergence_mean": round(statistics.mean(iterations), 2) if iterations else 0.0,
        "steps_to_convergence_median": statistics.median(iterations) if iterations else 0,
        "steps_to_convergence_min": min(iterations) if iterations else 0,
        "steps_to_convergence_max": max(iterations) if iterations else 0,
        "steps_to_convergence_stdev": round(statistics.pstdev(iterations), 2) if iterations else 0.0,
        "steps_distribution": distribution,
        "programs_hitting_iteration_cap": sum(1 for r in records if r.get("hit_iteration_cap")),
        "llm_used": llm_used,
        "llm_proposals": llm_total,
        "llm_valid": llm_valid,
        "llm_validity_rate_pct": _pct(llm_valid, llm_total) if llm_used else None,
        "false_positive_count": false_positives,
        "false_positive_rate_pct": _pct(false_positives, n) if n else 0.0,
        "per_category": per_category,
        "by_optimization_type": by_type,
    }


def _fmt(value) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def format_metrics_table(m: dict) -> str:
    rows = [
        ("Programs processed", _fmt(m["total_programs"])),
        ("Total proposals", _fmt(m["total_proposals"])),
        ("  passed verification", _fmt(m["passed_verification"])),
        ("  accepted", _fmt(m["accepted"])),
        ("  rejected (no cost gain)", _fmt(m["rejected_no_cost_gain"])),
        ("  invalid (failed verification)", _fmt(m["invalid_failed_verification"])),
        ("Verification pass rate", _fmt(m["verification_pass_rate_pct"]) + " %"),
        ("Acceptance rate (of verified)", _fmt(m["acceptance_rate_pct"]) + " %"),
        ("Average cost reduction", _fmt(m["avg_cost_reduction_pct"]) + " %"),
        ("Median cost reduction", _fmt(m["median_cost_reduction_pct"]) + " %"),
        ("Programs with >30% reduction", f"{m['programs_with_reduction_over_30pct']} / {m['total_programs']}"),
        ("Steps to convergence (mean)", _fmt(m["steps_to_convergence_mean"])),
        ("Steps to convergence (median)", _fmt(m["steps_to_convergence_median"])),
        ("Steps to convergence (min/max)", f"{m['steps_to_convergence_min']} / {m['steps_to_convergence_max']}"),
        ("Programs stopped by iteration cap", _fmt(m["programs_hitting_iteration_cap"])),
        ("LLM validity rate", (_fmt(m["llm_validity_rate_pct"]) + " %") if m["llm_used"] else "n/a (LLM not used)"),
        ("False positives (output mismatch)", f"{m['false_positive_count']}  ({_fmt(m['false_positive_rate_pct'])} %)"),
    ]
    width = max(len(r[0]) for r in rows) + 2
    vwidth = max(len(r[1]) for r in rows)
    bar = "+" + "-" * (width + 1) + "+" + "-" * (vwidth + 2) + "+"
    out = [bar, f"| {'Metric':<{width}}| {'Value':>{vwidth}} |", bar]
    out += [f"| {k:<{width}}| {v:>{vwidth}} |" for k, v in rows]
    out.append(bar)

    out.append("")
    out.append(f"  {'Category':<15}{'Programs':>9}{'Avg red.%':>11}{'Avg iters':>11}")
    for cat, c in m["per_category"].items():
        out.append(f"  {cat:<15}{c['programs']:>9}{c['avg_reduction_pct']:>11.2f}{c['avg_iterations']:>11.2f}")
    out.append("")
    out.append(f"  {'Optimization type':<20}{'Accepted':>10}{'Rejected':>10}{'Invalid':>9}")
    for t, c in m["by_optimization_type"].items():
        out.append(f"  {TYPE_LABELS.get(t, t):<20}{c['accepted']:>10}{c['rejected']:>10}{c['invalid']:>9}")
    status = "PASS ✓ (zero false positives)" if m["false_positive_count"] == 0 else "FAIL ✗"
    out.append("")
    out.append(f"  False-positive guarantee: {status}")
    return "\n".join(out)


# ---------------------------------------------------------------------- #
def save_results(records: list[dict], out_dir: str) -> str:
    metrics_dir = os.path.join(out_dir, "metrics")
    os.makedirs(metrics_dir, exist_ok=True)
    path = os.path.join(metrics_dir, "results.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=1)
    return path


def load_results(out_dir: str) -> list[dict]:
    path = os.path.join(out_dir, "metrics", "results.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found - run with --run-all first")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _flatten(prefix: str, value, rows: list[tuple[str, str]]) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            _flatten(f"{prefix}.{k}" if prefix else k, v, rows)
    else:
        rows.append((prefix, "" if value is None else value))


def save_metrics(metrics: dict, records: list[dict], out_dir: str) -> list[str]:
    metrics_dir = os.path.join(out_dir, "metrics")
    os.makedirs(metrics_dir, exist_ok=True)
    json_path = os.path.join(metrics_dir, "metrics_summary.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)

    csv_path = os.path.join(metrics_dir, "metrics_summary.csv")
    rows: list[tuple[str, str]] = []
    _flatten("", metrics, rows)
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["metric", "value"])
        writer.writerows(rows)

    per_path = os.path.join(metrics_dir, "per_program_results.csv")
    with open(per_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=PER_PROGRAM_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow({**r, "reduction_pct": f"{r['reduction_pct']:.2f}"})
    return [json_path, csv_path, per_path]


# ---------------------------------------------------------------------- #
def compare_runs(baseline: list[dict], current: list[dict]) -> dict:
    """Per-program and per-category comparison of two runs over the same programs
    (e.g. rule-only vs rule + LLM)."""
    base = {r["program_name"]: r for r in baseline}
    pairs = [(base[r["program_name"]], r) for r in current if r["program_name"] in base]
    if not pairs:
        return {"programs_compared": 0, "per_category": {}}

    def summarize(items):
        return {
            "programs": len(items),
            "baseline_avg_reduction_pct": round(statistics.mean(b["reduction_pct"] for b, _ in items), 2),
            "current_avg_reduction_pct": round(statistics.mean(c["reduction_pct"] for _, c in items), 2),
            "baseline_avg_final_cost": round(statistics.mean(b["final_cost"] for b, _ in items), 2),
            "current_avg_final_cost": round(statistics.mean(c["final_cost"] for _, c in items), 2),
            "programs_improved": sum(1 for b, c in items if c["final_cost"] < b["final_cost"]),
            "programs_worse": sum(1 for b, c in items if c["final_cost"] > b["final_cost"]),
        }

    per_category = {}
    for cat in CATEGORIES:
        items = [(b, c) for b, c in pairs if c["category"] == cat]
        if items:
            per_category[cat] = summarize(items)
    overall = summarize(pairs)
    return {"programs_compared": len(pairs), "overall": overall, "per_category": per_category}


def format_comparison(cmp: dict, base_label: str = "rule-only", cur_label: str = "rule+LLM") -> str:
    if not cmp["programs_compared"]:
        return "  (no overlapping programs to compare)"
    head = (f"  {'Category':<15}{'Programs':>9}{base_label + ' %':>14}{cur_label + ' %':>14}"
            f"{'Improved':>10}{'Worse':>7}")
    out = [head, "  " + "-" * (len(head) - 2)]
    rows = list(cmp["per_category"].items()) + [("ALL", cmp["overall"])]
    for cat, c in rows:
        out.append(f"  {cat:<15}{c['programs']:>9}{c['baseline_avg_reduction_pct']:>14.2f}"
                   f"{c['current_avg_reduction_pct']:>14.2f}{c['programs_improved']:>10}{c['programs_worse']:>7}")
    return "\n".join(out)


def save_comparison(cmp: dict, out_dir: str) -> list[str]:
    metrics_dir = os.path.join(out_dir, "metrics")
    os.makedirs(metrics_dir, exist_ok=True)
    json_path = os.path.join(metrics_dir, "comparison.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(cmp, fh, indent=2)
    csv_path = os.path.join(metrics_dir, "comparison.csv")
    fields = ["category", "programs", "baseline_avg_reduction_pct", "current_avg_reduction_pct",
              "baseline_avg_final_cost", "current_avg_final_cost", "programs_improved", "programs_worse"]
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for cat, c in list(cmp.get("per_category", {}).items()) + [("ALL", cmp.get("overall", {}))]:
            if c:
                writer.writerow({"category": cat, **c})
    return [json_path, csv_path]
