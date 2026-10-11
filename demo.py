"""Terminal front end: optimize a real C program step by step.

    py demo.py                                   # menu: pick a sample, paste code or give a path
    py demo.py demo_programs/3_loop.c            # pauses between stages (press Enter)
    py demo.py my_program.c --fast               # no pauses
    py demo.py my_program.c --step               # also pause after every agent decision
    py demo.py my_program.c --inputs n=10,k=3    # values for scanf() variables
    py demo.py my_program.c --use-llm            # add the Gemini proposer (needs .gemini_key)
    py demo.py my_program.c --verbose            # show every decision, including repeats

The program goes through the same pipeline as the 500-program experiment:
C source -> AST -> Three-Address Code -> agent loop -> verified, cheaper TAC.
After the loop it reports how many suggestions came from the rules and from
the LLM, and what happened to each.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
import textwrap
import time
from collections import Counter

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agents.cost_evaluator import CostEvaluator  # noqa: E402
from src.agents.orchestrator import Orchestrator  # noqa: E402
from src.frontend.c_frontend import CFrontendError, compile_c  # noqa: E402
from src.tac.interpreter import ExecutionTimeout, TACInterpreter, TACRuntimeError  # noqa: E402

WIDTH = 78
SAMPLES_DIR = os.path.join(PROJECT_ROOT, "demo_programs")
TYPE_LABELS = {
    "CONSTANT_FOLD": "Constant folding",
    "ALGEBRAIC_SIMPLIFY": "Algebraic simplification",
    "DEAD_CODE": "Dead code elimination",
    "CSE": "Common subexpression (CSE)",
    "STRENGTH_REDUCTION": "Strength reduction",
    "COPY_PROPAGATION": "Copy propagation",
    "LLM": "LLM proposal",
}


class Style:
    enabled = True
    CODES = {"bold": "1", "dim": "2", "red": "31", "green": "32", "yellow": "33",
             "blue": "34", "magenta": "35", "cyan": "36", "grey": "90"}

    @classmethod
    def c(cls, text: str, *names: str) -> str:
        if not cls.enabled or not names:
            return text
        return "\033[" + ";".join(cls.CODES[n] for n in names) + "m" + text + "\033[0m"


c = Style.c


class Pacer:
    def __init__(self, fast: bool, step: bool, delay: float):
        self.interactive = not fast and sys.stdin.isatty()
        self.step = step and self.interactive
        self.delay = 0.0 if fast else delay

    def pause(self, prompt: str = "Press Enter to continue") -> None:
        if self.interactive:
            try:
                input(c(f"\n  > {prompt} ", "grey"))
            except EOFError:
                self.interactive = False

    def tick(self) -> None:
        if self.step:
            self.pause("Enter for the next decision")
        elif self.delay:
            time.sleep(self.delay)


# ---------------------------------------------------------------------- #
# small display helpers
# ---------------------------------------------------------------------- #
def banner() -> None:
    print()
    print(c("=" * WIDTH, "blue"))
    print(c("  Automated LLM/Agent-Guided Compiler Code Optimization", "bold"))
    print(c("  Analyze -> Propose -> Verify -> Evaluate -> Accept/Reject", "grey"))
    print(c("=" * WIDTH, "blue"))


def stage(number: int, title: str) -> None:
    print()
    print(c("=" * WIDTH, "blue"))
    print(c(f"  STAGE {number}  ", "bold", "blue") + c(title, "bold"))
    print(c("=" * WIDTH, "blue"))


def numbered(lines: list[str], indent: str = "  ", start: int = 0) -> list[str]:
    """TAC is numbered from 0 (instruction index); source lines from 1 (as error messages count)."""
    w = len(str(max(len(lines) - 1 + start, 0)))
    return [f"{indent}{c(str(i).rjust(w), 'grey')} {c('|', 'grey')} {line}"
            for i, line in enumerate(lines, start=start)]


def tac_lines(program) -> list[str]:
    return [ins.to_string() if ins.to_string().endswith(":") else "  " + ins.to_string()
            for ins in program.instructions]


def clip(text: str, width: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


def side_by_side(left: list[str], right: list[str], left_title: str, right_title: str) -> None:
    col = max(max((len(s) for s in left), default=0), len(left_title)) + 4
    print("  " + c(left_title.ljust(col), "bold") + c(right_title, "bold", "green"))
    for i in range(max(len(left), len(right))):
        l_text = left[i] if i < len(left) else ""
        r_text = right[i] if i < len(right) else ""
        print("  " + c(l_text.ljust(col), "dim") + c(r_text, "green"))


# ---------------------------------------------------------------------- #
# choosing a program
# ---------------------------------------------------------------------- #
def sample_files() -> list[str]:
    return sorted(glob.glob(os.path.join(SAMPLES_DIR, "*.c")))


def first_comment(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            m = re.search(r"/\*(.*?)\*/", fh.read(), re.DOTALL)
        return clip(m.group(1), 52) if m else ""
    except OSError:
        return ""


def read_pasted() -> str:
    print(c("  Paste your C program, then type END on its own line:", "bold"))
    lines = []
    for line in sys.stdin:
        if line.strip() == "END":
            break
        lines.append(line)
    return "".join(lines)


def choose_program() -> tuple[str, str] | None:
    """Interactive menu. Returns (source, name) or None to quit."""
    samples = sample_files()
    print()
    print(c("  Choose a program to optimize:", "bold"))
    for i, path in enumerate(samples, start=1):
        print(f"    {c(str(i), 'cyan', 'bold')}  {os.path.basename(path):<18} {c(first_comment(path), 'grey')}")
    print(f"    {c('p', 'cyan', 'bold')}  paste my own C program")
    print(f"    {c('q', 'cyan', 'bold')}  quit")
    print(c("    ...or type the path of a .c file", "grey"))
    while True:
        try:
            choice = input(c("  > ", "cyan")).strip().strip('"')
        except EOFError:
            return None
        if choice.lower() in ("q", "quit", "exit"):
            return None
        if choice.lower() == "p":
            return read_pasted(), "pasted_program.c"
        if choice.isdigit() and 1 <= int(choice) <= len(samples):
            path = samples[int(choice) - 1]
        elif choice:
            path = choice
        else:
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                return fh.read(), os.path.basename(path)
        except OSError as exc:
            print(c(f"  cannot read '{path}': {exc.strerror or exc}", "red"))


def ask_yes_no(question: str, default: bool = False) -> bool:
    hint = "[Y/n]" if default else "[y/N]"
    try:
        answer = input(c(f"  {question} {hint} ", "cyan")).strip().lower()
    except EOFError:
        return default
    return default if not answer else answer.startswith("y")


def parse_inputs(text: str | None) -> dict[str, int]:
    values: dict[str, int] = {}
    for part in (text or "").split(","):
        if "=" in part:
            name, value = part.split("=", 1)
            try:
                values[name.strip()] = int(value.strip())
            except ValueError:
                print(c(f"  ignoring --inputs value '{part.strip()}' (not an integer)", "yellow"))
    return values


def choose_inputs(input_names: list[str], c_names: dict[str, str], given: dict[str, int],
                  pacer: Pacer) -> dict[str, int]:
    """One integer per program input: from --inputs, typed by the user, or a default."""
    chosen: dict[str, int] = {}
    for name in input_names:
        label = c_names.get(name, name)
        if label in given or name in given:
            chosen[name] = given.get(label, given.get(name))
            continue
        value = 7
        if pacer.interactive:
            try:
                raw = input(c(f"  value for {label} (scanf) [7]: ", "cyan")).strip()
                value = int(raw) if raw else 7
            except (EOFError, ValueError):
                value = 7
        chosen[name] = value
    return chosen


# ---------------------------------------------------------------------- #
# the agent loop, replayed from its decision log
# ---------------------------------------------------------------------- #
def describe(entry) -> str:
    text = entry.description
    if entry.source == "llm":
        return text.replace("LLM proposal: ", "").replace("LLM produced no usable TAC: ", "")
    return text.split(": ", 1)[1] if ": " in text else text


def replay(result, pacer: Pacer, verbose: bool) -> int:
    """Print the agent's decisions one by one. Returns how many repeat rejections were hidden.

    After every accepted change the agent re-checks suggestions it rejected earlier
    (the program changed, so the answer might differ). Those re-tries are counted in
    the summary but only printed once here, unless --verbose is given.
    """
    current: dict | None = None
    rejected_before: set[tuple[str, str]] = set()
    hidden = 0

    def flush() -> None:
        nonlocal current, hidden
        if current is None:
            return
        rec, current = current, None
        key = (rec["kind"], rec["what"].split(" → ")[0])
        if rec["outcome"] in ("nogain", "invalid") and rec["source"] == "rule":
            if key in rejected_before and not verbose:
                hidden += 1
                return
            rejected_before.add(key)
        head = c(f"  [{rec['it']:>2}] ", "grey") + c(f"{rec['kind']:<19}",
                                                    "magenta" if rec["source"] == "llm" else "cyan")
        if rec["outcome"] == "accept":
            tail = (c("verified ", "green") + f"cost {rec['before']:.1f} → "
                    + c(f"{rec['after']:.1f}", "bold") + c("  ACCEPTED", "green", "bold"))
        elif rec["outcome"] == "invalid":
            tail = c("verification FAILED  REJECTED (invalid)", "red", "bold")
        elif rec["outcome"] == "nogain":
            tail = (c("verified ", "green") + f"cost {rec['before']:.1f} → {rec['after']:.1f}"
                    + c("  REJECTED (no gain)", "yellow"))
        elif rec["outcome"] == "unverifiable":
            tail = c("could not be verified (program runs too long)", "red")
        else:
            tail = c("no usable suggestion in the reply", "grey")
        if rec["source"] == "llm":       # the LLM's explanation is a sentence: give it its own lines
            print(head.rstrip())
            for line in textwrap.wrap(" ".join(rec["what"].split()), 66)[:3]:
                print(" " * 9 + c(line, "dim"))
        else:
            print(head + clip(rec["what"], 52))
        print(" " * 9 + tail)
        if rec["outcome"] == "invalid" and rec.get("reason"):
            print(" " * 9 + c(clip(rec["reason"], 66), "grey"))
        pacer.tick()

    for e in result.log.entries:
        if e.phase == "analyze" and verbose:
            flush()
            print(c(f"       {e.description}", "grey"))
        elif e.phase == "propose":
            flush()
            kind = "LLM (Gemini)" if e.source == "llm" else e.opportunity_type
            current = {"it": e.iteration, "kind": kind, "source": e.source, "what": describe(e),
                       "outcome": None, "before": 0.0, "after": 0.0, "reason": None}
        elif current is not None and e.phase == "verify":
            current["reason"] = e.reason
        elif current is not None and e.phase == "evaluate":
            current["before"], current["after"] = e.cost_before, e.cost_after
        elif current is not None and e.phase == "accept":
            current["outcome"] = "accept"
        elif current is not None and e.phase == "reject":
            reason = e.reason or ""
            current["outcome"] = ("unverifiable" if reason.startswith("Could not be verified")
                                  else "invalid" if "Verification failed" in reason else "nogain")
        elif e.phase == "info":
            flush()
            if not (result.stopped_reason and e.description.startswith("Stopped:")):
                print(c(f"       {e.description}", "grey"))   # the stop reason is printed by the caller
    flush()
    return hidden


# ---------------------------------------------------------------------- #
# suggestion summary
# ---------------------------------------------------------------------- #
def count_outcomes(proposals: list[dict]) -> dict[str, int]:
    outcomes = Counter(p["outcome"] for p in proposals)
    accepted, no_gain, invalid = outcomes["accepted"], outcomes["rejected"], outcomes["invalid"]
    return {"suggested": len(proposals), "verified": accepted + no_gain,
            "accepted": accepted, "no_gain": no_gain, "invalid": invalid}


def suggestion_summary(result, llm_enabled: bool, llm_note: str, hidden: int) -> None:
    """How many suggestions came from the rules and from the LLM, and what happened to each."""
    rules = [p for p in result.proposals if p["source"] == "rule"]
    llm = [p for p in result.proposals if p["source"] == "llm"]
    rows = [("Rule-based", count_outcomes(rules), "cyan"),
            ("LLM (Gemini)", count_outcomes(llm), "magenta"),
            ("Total", count_outcomes(result.proposals), "bold")]

    print("  " + c(f"{'Source':<16}{'Suggested':>10}{'Verified':>10}{'Accepted':>10}"
                   f"{'No gain':>9}{'Invalid':>9}", "bold"))
    print("  " + c("-" * 64, "grey"))
    for label, n, colour in rows:
        if label == "Total":
            print("  " + c("-" * 64, "grey"))
        line = (f"{label:<16}{n['suggested']:>10}{n['verified']:>10}{n['accepted']:>10}"
                f"{n['no_gain']:>9}{n['invalid']:>9}")
        print("  " + c(line, colour))
    print()
    print(c("  Suggested = proposals made   Verified = passed the correctness check", "grey"))
    print(c("  No gain   = correct but not cheaper   Invalid = failed the correctness check", "grey"))

    if llm_enabled:
        unusable = result.llm_calls - len(llm)
        text = f"  LLM requests sent: {result.llm_calls}"
        if result.llm_calls:
            text += f"  ({len(llm)} usable suggestion{'s' if len(llm) != 1 else ''}"
            text += f", {unusable} unusable repl{'ies' if unusable != 1 else 'y'})" if unusable else ")"
        print(c(text, "magenta"))
        if not result.llm_calls:
            print(c("  The LLM was not needed: the rules left nothing more to improve.", "grey"))
    else:
        print(c(f"  LLM: {llm_note}", "grey"))
    if hidden:
        print(c(f"  'No gain' includes {hidden} re-tr{'ies' if hidden != 1 else 'y'} of suggestions already "
                "rejected once (hidden above).", "grey"))

    by_type: dict[str, Counter] = {}
    for p in result.proposals:
        by_type.setdefault(p["type"], Counter())[p["outcome"]] += 1
    if by_type:
        print()
        print("  " + c(f"{'By optimization type':<30}{'Suggested':>10}{'Accepted':>10}"
                       f"{'No gain':>9}{'Invalid':>9}", "bold"))
        print("  " + c("-" * 68, "grey"))
        for key in TYPE_LABELS:
            if key in by_type:
                n = by_type[key]
                print(f"  {TYPE_LABELS[key]:<30}{sum(n.values()):>10}{n['accepted']:>10}"
                      f"{n['rejected']:>9}{n['invalid']:>9}")


# ---------------------------------------------------------------------- #
def run_program(program, inputs: dict[str, int]) -> str:
    try:
        return "prints " + str(TACInterpreter().execute(program, inputs, max_steps=200_000))
    except ExecutionTimeout as exc:
        return f"prints {exc.outputs} and is still running after 200,000 steps"
    except TACRuntimeError as exc:
        return f"prints {exc.outputs} then stops with an error: {exc}"


def make_orchestrator(use_llm: bool, provider: str, max_iterations: int) -> tuple[Orchestrator, bool, str]:
    """Returns (orchestrator, llm_enabled, note about the LLM when it is not enabled)."""
    if not use_llm:
        return Orchestrator(max_iterations=max_iterations), False, "not used (add --use-llm to include Gemini)"
    if provider == "gemini" and not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
        key_path = os.path.join(PROJECT_ROOT, ".gemini_key")
        if os.path.exists(key_path):
            with open(key_path, encoding="utf-8") as fh:
                os.environ["GEMINI_API_KEY"] = fh.read().strip()
    orchestrator = Orchestrator(use_llm=True, max_iterations=max_iterations,
                                llm_provider=provider, max_llm_calls=3)
    llm = orchestrator.llm_optimizer
    if llm is None or not llm.available:
        reason = clip(llm.unavailable_reason if llm else "not configured", 48)
        orchestrator.llm_optimizer = None
        return orchestrator, False, f"unavailable ({reason})"
    return orchestrator, True, ""


def run_demo(source: str, name: str, args, pacer: Pacer, use_llm: bool) -> int:
    # ------------------------------------------------------------ stage 1
    stage(1, f"The C program  ({name})")
    for line in numbered(source.rstrip().splitlines(), start=1):
        print(line)

    try:
        tac, cprog = compile_c(source)
    except CFrontendError as exc:
        print()
        print(c(f"  {exc}", "red", "bold"))
        print(c("  Supported: int variables, if / else if / else, while, for, += ++,", "grey"))
        print(c("  printf(\"%d\") and scanf(\"%d\"). Not supported: arrays, pointers, other functions.", "grey"))
        return 1
    for note in cprog.notes:
        print(c(f"  note: {note}", "yellow"))
    c_names = {inp: var for inp, var in cprog.inputs}
    input_names = sorted(tac.get_input_variables())
    if len(tac) == 0:
        print(c("\n  The program has no statements to optimize.", "red"))
        return 1
    pacer.pause("Enter to translate it to Three-Address Code")

    # ------------------------------------------------------------ stage 2
    evaluator = CostEvaluator()
    cost0 = evaluator.evaluate(tac)
    stage(2, "Frontend: C → AST → Three-Address Code")
    for line in numbered(tac_lines(tac)):
        print(line)
    print()
    print(f"  {c(str(cost0.instruction_count), 'bold')} instructions, {cost0.arithmetic_ops} arithmetic, "
          f"{cost0.temp_vars} temporaries, {cost0.memory_ops} copies, {cost0.branch_ops} branches")
    print("  weighted cost = " + c(f"{cost0.weighted_total:.1f}", "bold", "yellow"))
    if input_names:
        shown = ", ".join(c_names.get(n, n) for n in input_names)
        print(c(f"  inputs (scanf): {shown} - the verifier will test many different values", "cyan"))
    pacer.pause("Enter to start the agent loop")

    # ------------------------------------------------------------ stage 3
    stage(3, "Agent loop: Analyze → Propose → Verify → Evaluate → Accept/Reject")
    orchestrator, llm_enabled, llm_note = make_orchestrator(use_llm, args.llm_provider, args.max_iterations)
    if use_llm and not llm_enabled:
        print(c(f"  LLM {llm_note}; continuing with rules only.", "yellow"))
    elif llm_enabled:
        print(c("  Rules + Gemini: the LLM is asked when a rule is rejected or the rules run out.", "magenta"))
        print(c("  (waiting for the LLM can take a few seconds)", "grey"))
    started = time.time()
    result = orchestrator.optimize(tac, name)
    elapsed = time.time() - started
    hidden = replay(result, pacer, args.verbose)
    print()
    if result.stopped_reason:
        print(c(f"  Stopped: {result.stopped_reason}.", "red", "bold"))
        print(c("  The agent only accepts changes it can check by running the program, so it made none.", "grey"))
        print(c("  Use smaller loop bounds (the limit is 100,000 executed instructions) and try again.", "grey"))
        return 1
    print(c(f"  finished in {result.iterations} iterations ({elapsed:.1f}s)", "bold"))
    if result.hit_iteration_cap:
        print(c(f"  note: stopped at the iteration limit ({args.max_iterations}); more may be possible", "yellow"))
    pacer.pause("Enter to see how many suggestions were made")

    # ------------------------------------------------------------ stage 4
    stage(4, "Suggestions made by the agent")
    suggestion_summary(result, llm_enabled, llm_note, hidden)
    pacer.pause("Enter to see the optimized program")

    # ------------------------------------------------------------ stage 5
    stage(5, "Result: original vs. optimized TAC")
    side_by_side(tac_lines(result.original_tac), tac_lines(result.optimized_tac),
                 f"Original ({len(result.original_tac)} instructions)",
                 f"Optimized ({len(result.optimized_tac)} instructions)")
    print()
    f = result.final_cost
    print(f"  cost {c(f'{cost0.weighted_total:.1f}', 'yellow')} → {c(f'{f.weighted_total:.1f}', 'green', 'bold')}"
          f"   reduction {c(f'{result.cost_reduction_pct:.1f}%', 'green', 'bold')}")
    pacer.pause("Enter to check that the output is unchanged")

    # ------------------------------------------------------------ stage 6
    stage(6, "Proof: the optimized program behaves the same")
    inputs = choose_inputs(input_names, c_names, parse_inputs(args.inputs), pacer)
    if inputs:
        print("  running with " + ", ".join(f"{c_names.get(k, k)} = {v}" for k, v in inputs.items()))
    before, after = run_program(result.original_tac, inputs), run_program(result.optimized_tac, inputs)
    print(f"  original : {before}")
    print(f"  optimized: {after}")
    same = before == after
    print("  " + (c("identical output", "green", "bold") if same else c("OUTPUT DIFFERS", "red", "bold")))
    verdict = c("PASS", "green", "bold") if result.output_match else c("FAIL", "red", "bold")
    print(f"  verifier, final check against the original: {verdict}")
    print(c(f"    {clip(result.final_check_reason, 70)}", "grey"))

    out_dir = os.path.join(PROJECT_ROOT, "output", "demo")
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(name)[0]
    with open(os.path.join(out_dir, f"{stem}.log"), "w", encoding="utf-8") as fh:
        fh.write("=== C source ===\n" + source.rstrip() + "\n\n" + result.format_report() + "\n")
    result.log.save(os.path.join(out_dir, f"{stem}.json"))
    print(c(f"\n  full decision log saved to output/demo/{stem}.log", "grey"))
    return 0 if same and result.output_match else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Terminal front end: optimize a C program with the agent loop")
    ap.add_argument("file", nargs="?", help="C source file (omit for the menu)")
    ap.add_argument("--fast", action="store_true", help="no pauses or delays")
    ap.add_argument("--step", action="store_true", help="pause after every agent decision")
    ap.add_argument("--verbose", action="store_true",
                    help="show every decision, including repeats and what the analyzer found")
    ap.add_argument("--inputs", help="values for scanf variables, e.g. n=10,k=3")
    ap.add_argument("--use-llm", action="store_true", help="add the LLM proposer")
    ap.add_argument("--llm-provider", default="gemini", choices=["gemini", "anthropic"])
    ap.add_argument("--max-iterations", type=int, default=200, help="agent iteration cap (default 200)")
    ap.add_argument("--delay", type=float, default=0.12, help="seconds between decisions")
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args()

    Style.enabled = not args.no_color and sys.stdout.isatty()
    if Style.enabled and os.name == "nt":
        os.system("")   # switches the Windows console to ANSI colour mode
    pacer = Pacer(args.fast, args.step, args.delay)
    banner()

    if args.file:
        try:
            with open(args.file, encoding="utf-8") as fh:
                source = fh.read()
        except OSError as exc:
            print(c(f"  Cannot read '{args.file}': {exc.strerror or exc}", "red"))
            return 1
        return run_demo(source, os.path.basename(args.file), args, pacer, args.use_llm)

    if not sys.stdin.isatty():            # piped input: treat it as a pasted program
        return run_demo(sys.stdin.read(), "pasted_program.c", args, pacer, args.use_llm)

    status = 0
    while True:
        chosen = choose_program()
        if chosen is None:
            return status
        source, name = chosen
        use_llm = args.use_llm
        if not use_llm and os.path.exists(os.path.join(PROJECT_ROOT, ".gemini_key")):
            use_llm = ask_yes_no("Also use the Gemini LLM proposer?", default=False)
        status = run_demo(source, name, args, pacer, use_llm)
        if not ask_yes_no("Run another program?", default=True):
            return status


if __name__ == "__main__":
    sys.exit(main())
