"""Automated LLM/Agent-Guided Compiler Code Optimization - entry point."""
from __future__ import annotations

import argparse
import glob
import importlib.util
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agents.optimizer_llm import DEFAULT_MODELS, PROVIDERS  # noqa: E402
from src.agents.orchestrator import Orchestrator  # noqa: E402
from src.frontend import LexerError, ParseError, compile_source  # noqa: E402
from src.visualization.report import (  # noqa: E402
    aggregate_metrics,
    format_metrics_table,
    infer_category,
    load_results,
    result_to_record,
    save_metrics,
    save_results,
)

DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset", "programs")


def _configure_console() -> None:
    # Decision logs contain ✓ ✗ →; make sure redirected output on Windows can encode them.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _load_generator():
    path = os.path.join(PROJECT_ROOT, "dataset", "generator.py")
    spec = importlib.util.spec_from_file_location("dataset_generator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _display(path: str) -> str:
    """Path relative to the project when possible (relpath fails across Windows drives)."""
    try:
        return os.path.relpath(path, PROJECT_ROOT)
    except ValueError:
        return path


def _load_key_file(env_var: str, filename: str) -> None:
    """Load an API key from a git-ignored file in the project root if the env var is unset."""
    if os.environ.get(env_var):
        return
    path = os.path.join(PROJECT_ROOT, filename)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            key = fh.read().strip()
        if key:
            os.environ[env_var] = key


def ensure_output_dirs(out_dir: str) -> None:
    for sub in ("logs", "metrics", "plots"):
        os.makedirs(os.path.join(out_dir, sub), exist_ok=True)


def process_file(path: str, orchestrator: Orchestrator, out_dir: str, echo: bool = True) -> dict | None:
    name = os.path.basename(path)
    with open(path, encoding="utf-8") as fh:
        source = fh.read()
    try:
        tac = compile_source(source)
    except (LexerError, ParseError) as exc:
        print(f"  ! {name}: {exc}")
        return None
    result = orchestrator.optimize(tac, name)
    report = result.format_report()
    stem = os.path.splitext(name)[0]
    logs_dir = os.path.join(out_dir, "logs")
    result.log.save(os.path.join(logs_dir, f"{stem}.json"))
    with open(os.path.join(logs_dir, f"{stem}.log"), "w", encoding="utf-8") as fh:
        fh.write(report + "\n")
    if echo:
        print(report)
        print()
    return result_to_record(result, infer_category(name, path))


def run_all(orchestrator: Orchestrator, out_dir: str, quiet: bool) -> list[dict]:
    files = sorted(glob.glob(os.path.join(DATASET_DIR, "*", "*.src")))
    if not files:
        print(f"No .src files found under {DATASET_DIR}. Run with --generate-dataset first.")
        return []
    records = []
    start = time.time()
    llm = orchestrator.llm_optimizer
    llm_was_available = llm is not None and llm.available
    for idx, path in enumerate(files, start=1):
        print(f"Processing [{idx}/{len(files)}]: {os.path.basename(path)}", flush=True)
        record = process_file(path, orchestrator, out_dir, echo=not quiet)
        if record is not None:
            records.append(record)
        if llm_was_available and not llm.available:
            print(f"  ! LLM switched off after {idx} programs: {llm.unavailable_reason}", flush=True)
            llm_was_available = False
    print(f"\nProcessed {len(records)} programs in {time.time() - start:.1f}s")
    return records


def report_metrics(records: list[dict], out_dir: str, llm_used: bool) -> None:
    metrics = aggregate_metrics(records, llm_used=llm_used)
    print("\n=== METRICS SUMMARY ===")
    print(format_metrics_table(metrics))
    save_results(records, out_dir)
    for path in save_metrics(metrics, records, out_dir):
        print(f"  saved {_display(path)}")


def main() -> int:
    _configure_console()
    parser = argparse.ArgumentParser(description="Automated Compiler Code Optimization Agent")
    parser.add_argument("--generate-dataset", action="store_true", help="Generate the 500-program dataset")
    parser.add_argument("--run-all", action="store_true", help="Run optimization on all dataset programs")
    parser.add_argument("--run-file", type=str, help="Run optimization on a single .src file")
    parser.add_argument("--use-llm", action="store_true", help="Enable LLM-based optimizer alongside rule-based")
    parser.add_argument("--output-dir", type=str, default="output", help="Output directory")
    parser.add_argument("--visualize", action="store_true", help="Generate all 6 visualization charts")
    parser.add_argument("--quiet", action="store_true",
                        help="With --run-all: print only progress, not every decision log (logs are still saved)")
    parser.add_argument("--max-iterations", type=int, default=50, help="Agent iteration cap per program")
    parser.add_argument("--llm-provider", choices=sorted(PROVIDERS), default="anthropic",
                        help="LLM backend for --use-llm: anthropic (Claude) or gemini (Google)")
    parser.add_argument("--llm-model", type=str, default=None,
                        help="Model ID for --use-llm (default: "
                             + ", ".join(f"{p}={m}" for p, m in DEFAULT_MODELS.items()) + ")")
    parser.add_argument("--max-llm-calls", type=int, default=5, help="LLM proposals allowed per program")
    parser.add_argument("--compare-with", type=str, default=None,
                        help="With --visualize: another output dir (e.g. a rule-only run) to compare against")
    args = parser.parse_args()

    if not any([args.generate_dataset, args.run_all, args.run_file, args.visualize]):
        parser.print_help()
        return 1

    out_dir = args.output_dir if os.path.isabs(args.output_dir) else os.path.join(PROJECT_ROOT, args.output_dir)
    ensure_output_dirs(out_dir)

    if args.generate_dataset:
        generator = _load_generator()
        counts = generator.generate_dataset(DATASET_DIR)
        for cat, n in counts.items():
            print(f"  {cat:<14} {n:>4} programs")
        print(f"Generated {sum(counts.values())} programs in {_display(DATASET_DIR)}")

    if args.run_all or args.run_file:
        if args.use_llm and args.llm_provider == "gemini" and not os.environ.get("GOOGLE_API_KEY"):
            _load_key_file("GEMINI_API_KEY", ".gemini_key")
        orchestrator = Orchestrator(use_llm=args.use_llm, max_iterations=args.max_iterations,
                                    llm_model=args.llm_model, max_llm_calls=args.max_llm_calls,
                                    llm_provider=args.llm_provider)
        if args.use_llm and orchestrator.llm_optimizer and not orchestrator.llm_optimizer.available:
            print(f"Warning: LLM optimizer unavailable ({orchestrator.llm_optimizer.unavailable_reason}); "
                  "continuing with rule-based optimization only.")

        if args.run_file:
            if not os.path.exists(args.run_file):
                print(f"File not found: {args.run_file}")
                return 1
            record = process_file(args.run_file, orchestrator, out_dir, echo=True)
            if record is None:
                return 1
            print(f"Decision log saved to {_display(os.path.join(out_dir, 'logs'))}")

        if args.run_all:
            records = run_all(orchestrator, out_dir, args.quiet)
            if records:
                report_metrics(records, out_dir, llm_used=args.use_llm)
            llm = orchestrator.llm_optimizer
            if args.use_llm and llm is not None and not llm.available:
                print(f"Note: LLM optimizer was disabled during the run ({llm.unavailable_reason}).")

    if args.visualize:
        from src.visualization.charts import generate_all_charts

        try:
            records = load_results(out_dir)
        except FileNotFoundError as exc:
            print(exc)
            return 1
        print("\n=== METRICS SUMMARY ===")
        print(format_metrics_table(aggregate_metrics(records)))
        print("\nGenerating charts...")
        for path in generate_all_charts(records, out_dir):
            print(f"  saved {_display(path)}")
        if args.compare_with:
            from src.visualization.charts import comparison_chart
            from src.visualization.report import compare_runs, format_comparison, save_comparison

            base_dir = args.compare_with
            if not os.path.isabs(base_dir):
                base_dir = os.path.join(PROJECT_ROOT, base_dir)
            try:
                baseline = load_results(base_dir)
            except FileNotFoundError as exc:
                print(exc)
                return 1
            cmp = compare_runs(baseline, records)
            print(f"\n=== COMPARISON: {_display(base_dir)} (baseline) vs {_display(out_dir)} ===")
            print(format_comparison(cmp))
            for path in save_comparison(cmp, out_dir) + [comparison_chart(cmp, out_dir)]:
                if path:
                    print(f"  saved {_display(path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
