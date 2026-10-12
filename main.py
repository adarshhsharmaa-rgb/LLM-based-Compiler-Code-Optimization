"""Automated LLM/Agent-Guided Compiler Code Optimization - entry point."""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agents.optimization_specialist import MODE_SUMMARIES, MODES  # noqa: E402
from src.agents.optimizer_llm import DEFAULT_MODELS, PROVIDERS, load_key_files  # noqa: E402
from src.agents.orchestrator import Orchestrator  # noqa: E402
from src.frontend import LexerError, ParseError, compile_source  # noqa: E402
from src.frontend.c_frontend import CFrontendError, compile_c  # noqa: E402
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
REAL_DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset", "real_programs")
DATASETS = {
    # name: (folder, file pattern, what to do when it is empty)
    "generated": (DATASET_DIR, "*.src", "Run with --generate-dataset first."),
    "real": (REAL_DATASET_DIR, "*.c", "Build it with dataset/real_dataset.py (collect, then select)."),
}


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


def ensure_output_dirs(out_dir: str) -> None:
    for sub in ("logs", "metrics", "plots"):
        os.makedirs(os.path.join(out_dir, sub), exist_ok=True)


def process_file(path: str, orchestrator: Orchestrator, out_dir: str, echo: bool = True) -> dict | None:
    name = os.path.basename(path)
    with open(path, encoding="utf-8") as fh:
        source = fh.read()
    try:
        if name.endswith(".c"):
            tac, _ = compile_c(source, strict=True)     # a C program: strict mode keeps its printed text
        else:
            tac = compile_source(source)
    except (LexerError, ParseError, CFrontendError) as exc:
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


def _load_cache(path: str) -> dict[str, dict]:
    """Results a previous, interrupted run already saved (a half-written last line is ignored)."""
    done: dict[str, dict] = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                done[record["program_name"]] = record
    return done


def run_all(orchestrator: Orchestrator, out_dir: str, quiet: bool, dataset: str = "generated",
            every: int = 1, resume: bool = False, require_llm: bool = False) -> list[dict]:
    """Optimize the whole dataset. Every finished program is appended to a cache file at
    once, so a run that is interrupted (hours in, with an LLM) can be continued with
    ``--resume`` instead of starting again. The cache is removed when the run completes.

    ``require_llm`` stops the run as soon as the LLM becomes unavailable (a daily quota is
    spent), instead of finishing the remaining programs with the rules alone."""
    folder, pattern, hint = DATASETS[dataset]
    files = sorted(glob.glob(os.path.join(folder, "*", pattern)))[::max(every, 1)]
    cache_path = os.path.join(out_dir, "metrics", "records_cache.jsonl")
    cached = _load_cache(cache_path) if resume else {}
    if resume and not cached:
        # A run that finished (for example on a sample made with --every) can be extended:
        # its saved results count as done.
        try:
            cached = {r["program_name"]: r for r in load_results(out_dir)}
        except FileNotFoundError:
            pass
    if cached:
        print(f"Resuming: {len(cached)} programs are already done in {_display(cache_path)}")
    if not files:
        print(f"No {pattern[1:]} files found under {folder}. {hint}")
        return []
    records = []
    start = time.time()
    llm = orchestrator.llm_optimizer
    llm_was_available = llm is not None and llm.available
    cache = open(cache_path, "w", encoding="utf-8")
    for record in cached.values():          # so the cache alone is enough if this run is interrupted too
        cache.write(json.dumps(record) + "\n")
    stopped = require_llm and not llm_was_available
    if stopped:
        reason = getattr(llm, "unavailable_reason", "") or "no LLM is attached"
        print(f"The LLM is not available ({reason}), so nothing was run (--require-llm).")
    for idx, path in enumerate(files if not stopped else [], start=1):
        name = os.path.basename(path)
        if name in cached:
            records.append(cached[name])
            continue
        print(f"Processing [{idx}/{len(files)}]: {name}", flush=True)
        record = process_file(path, orchestrator, out_dir, echo=not quiet)
        if require_llm and not llm.available:
            # The LLM gave out during this program, so its result is not an LLM result: drop it.
            print(f"  ! LLM unavailable: {llm.unavailable_reason}. Stopped before {name}; "
                  "continue later with --resume.", flush=True)
            stopped = True
            break
        if record is not None:
            records.append(record)
            cache.write(json.dumps(record) + "\n")
            cache.flush()
            os.fsync(cache.fileno())
        if llm_was_available and not llm.available:
            print(f"  ! LLM switched off after {idx} programs: {llm.unavailable_reason}", flush=True)
            llm_was_available = False
    cache.close()
    if stopped:
        seen = {r["program_name"] for r in records}
        records += [r for name, r in cached.items() if name not in seen]   # done earlier, further down the list
    else:
        os.remove(cache_path)       # the caller writes the complete results next
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
    parser.add_argument("--run-file", type=str, help="Run optimization on a single .src or .c file")
    parser.add_argument("--resume", action="store_true",
                        help="With --run-all: continue an interrupted run, skipping the programs whose "
                             "results are already in <output-dir>/metrics/records_cache.jsonl")
    parser.add_argument("--require-llm", action="store_true",
                        help="With --run-all and an LLM: stop when the LLM becomes unavailable (quota spent) "
                             "instead of finishing with the rules alone; continue later with --resume")
    parser.add_argument("--every", type=int, default=1, metavar="K",
                        help="With --run-all: optimize only every K-th program, a sample spread evenly over "
                             "the categories (for slow runs such as a local model on the CPU)")
    parser.add_argument("--dataset", choices=sorted(DATASETS), default="generated",
                        help="Which programs --run-all optimizes: the generated 500, or the 500 real "
                             "Codeforces submissions built by dataset/real_dataset.py")
    parser.add_argument("--optimizer", choices=MODES, default=None,
                        help="How the Optimization Specialist routes each step: "
                             + "; ".join(f"{m} = {MODE_SUMMARIES[m]}" for m in MODES)
                             + " (default: rule, or hybrid with --use-llm / --offline)")
    parser.add_argument("--use-llm", action="store_true",
                        help="Enable LLM-based optimizer alongside rule-based (same as --optimizer hybrid)")
    parser.add_argument("--offline", action="store_true",
                        help="Offline mode: the LLM is a local Ollama model, no internet or API key needed")
    parser.add_argument("--output-dir", type=str, default="output", help="Output directory")
    parser.add_argument("--visualize", action="store_true", help="Generate all 6 visualization charts")
    parser.add_argument("--quiet", action="store_true",
                        help="With --run-all: print only progress, not every decision log (logs are still saved)")
    parser.add_argument("--cost-model", choices=["static", "time"], default="static",
                        help="What counts as cheaper: static = weighted instruction counts (default); "
                             "time = measured execution time first, static cost second")
    parser.add_argument("--max-iterations", type=int, default=50, help="Agent iteration cap per program")
    parser.add_argument("--llm-provider", choices=["auto", *sorted(PROVIDERS)], default="auto",
                        help="LLM backend: gemini (Google), groq (Groq), ollama (local model), or "
                             "auto = gemini or groq when online and a key is set, otherwise ollama")
    parser.add_argument("--llm-model", type=str, default=None,
                        help="Model ID for the LLM (default: "
                             + ", ".join(f"{p}={m}" for p, m in DEFAULT_MODELS.items()) + ")")
    parser.add_argument("--max-llm-calls", type=int, default=5, help="LLM proposals allowed per program")
    parser.add_argument("--max-repairs", type=int, default=1,
                        help="Self-repair: second tries the LLM gets after a rejected answer, with the "
                             "verifier's counterexample as feedback (default 1, 0 turns it off)")
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
        mode = args.optimizer or ("hybrid" if args.use_llm or args.offline else "rule")
        use_llm = mode != "rule"
        if use_llm and not args.offline:
            load_key_files(PROJECT_ROOT)      # .gemini_key / .groq_key
        orchestrator = Orchestrator(optimizer_mode=mode, max_iterations=args.max_iterations, cost_model=args.cost_model,
                                    llm_model=args.llm_model, max_llm_calls=args.max_llm_calls,
                                    llm_provider=args.llm_provider, offline=args.offline,
                                    max_repairs=args.max_repairs)
        llm = orchestrator.llm_optimizer
        if llm is not None:
            why = f" - {llm.selected_because}" if llm.selected_because else ""
            print(f"Optimizer routing: {mode} ({MODE_SUMMARIES[mode]})")
            print(f"LLM backend: {llm.label}{why}")
            if not llm.available:
                print(f"Warning: LLM optimizer unavailable ({llm.unavailable_reason}); "
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
            records = run_all(orchestrator, out_dir, args.quiet, args.dataset, args.every, args.resume,
                              args.require_llm)
            if records:
                report_metrics(records, out_dir, llm_used=use_llm)
            if llm is not None and not llm.available:
                print(f"Note: LLM optimizer was disabled during the run ({llm.unavailable_reason}).")

        for previous, current, calls in getattr(llm, "model_switches", []):
            print(f"Note: Groq model {previous} became unusable after {calls} calls (daily quota spent "
                  f"or model not available); the run continued with {current}.")
        if getattr(llm, "cpu_fallback", False):
            print("Note: Ollama's GPU runner crashed, so the model ran on the CPU (slower). "
                  "Updating the NVIDIA driver usually fixes this.")

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
