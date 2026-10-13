"""Terminal front end: optimize a real C program step by step.

    py demo.py                                   # menu: pick a program, then who proposes and the cost model
    py demo.py demo_programs/3_loop.c            # pauses between stages (press Enter)
    py demo.py demo_programs/3_loop.c --compare  # the same program under the rules and every LLM that is ready
    py demo.py my_program.c --cost-model time    # judge changes by measured execution time, not the static count
    py demo.py dataset/real_programs/loops/loops_001.c   # a real Codeforces program (strict C mode)
    py demo.py my_program.c --fast               # no pauses
    py demo.py my_program.c --step               # also pause after every agent decision
    py demo.py my_program.c --inputs n=10,k=3    # values for scanf() variables
    py demo.py my_program.c --use-llm            # add the LLM proposer (Gemini, or Ollama when offline)
    py demo.py my_program.c --offline            # add the local Ollama model as the LLM proposer
    py demo.py my_program.c --optimizer llm      # route to the LLM first, the rules second
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
import random
import re
import sys
import textwrap
import time
from collections import Counter

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agents.cost_evaluator import CostEvaluator  # noqa: E402
from src.agents.smt_verifier import z3_available  # noqa: E402
from src.agents.optimization_specialist import MODE_SUMMARIES, MODES  # noqa: E402
from src.agents.optimizer_llm import KEY_FILES, PROVIDERS, load_key_files, ollama_running  # noqa: E402
from src.agents.orchestrator import Orchestrator  # noqa: E402
from src.frontend.c_frontend import CFrontendError, compile_c  # noqa: E402
from src.tac.interpreter import ExecutionTimeout, TACInterpreter, TACRuntimeError  # noqa: E402

WIDTH = 78
SAMPLES_DIR = os.path.join(PROJECT_ROOT, "demo_programs")
REAL_DIR = os.path.join(PROJECT_ROOT, "dataset", "real_programs")
PROOF_LABELS = {"identical": "the optimized program is identical to the original",
                "both": "proved for all inputs by the symbolic polynomial check",
                "smt": "proved for all inputs by the Z3 SMT solver"}
TYPE_LABELS = {
    "CONSTANT_FOLD": "Constant folding",
    "ALGEBRAIC_SIMPLIFY": "Algebraic simplification",
    "DEAD_CODE": "Dead code elimination",
    "CSE": "Common subexpression (CSE)",
    "STRENGTH_REDUCTION": "Strength reduction",
    "COPY_PROPAGATION": "Copy propagation",
    "LLM": "LLM proposal",
}
LLM_NAMES = {"gemini": "Gemini", "groq": "Groq", "ollama": "Ollama"}


def llm_label(result) -> str:
    """Name of the LLM proposer for this run, e.g. ``LLM (Ollama)``."""
    name = LLM_NAMES.get(result.llm_provider)
    return f"LLM ({name})" if name else "LLM"


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


def real_files() -> list[str]:
    """The real-program dataset; short programs only, so that one fits on the screen."""
    return [path for path in sorted(glob.glob(os.path.join(REAL_DIR, "*", "*.c")))
            if os.path.getsize(path) < 900]


def is_real_program(name: str) -> bool:
    """Real programs print text and leave early, so they are compiled in the front end's strict mode."""
    return bool(glob.glob(os.path.join(REAL_DIR, "*", os.path.basename(name))))


def llm_choices() -> list[tuple[str, str, bool, str]]:
    """(name, provider, ready, note) for every LLM the demo can use."""
    choices = []
    for provider, variable in (("groq", "GROQ_API_KEY"), ("gemini", "GEMINI_API_KEY")):
        ready = bool(os.environ.get(variable)) or os.path.exists(os.path.join(PROJECT_ROOT, KEY_FILES[variable]))
        choices.append((LLM_NAMES[provider], provider, ready,
                        "cloud, key found" if ready else f"cloud, no key: save one in {KEY_FILES[variable]}"))
    ready = ollama_running()
    choices.append(("Ollama", "ollama", ready,
                    "local model, no internet needed" if ready else "local model: Ollama is not running"))
    return choices


def with_llm(args, provider: str | None):
    """A copy of the command-line options with the LLM set to ``provider`` (None = rules only)."""
    chosen = argparse.Namespace(**vars(args))
    if provider:
        chosen.llm_provider, chosen.offline = provider, provider == "ollama"
    return chosen


def choose_setup(args) -> tuple[argparse.Namespace, str, bool] | None:
    """Ask who proposes and what counts as cheaper. Returns (options, routing mode, compare all)."""
    choices = llm_choices()
    print()
    print(c("  Who proposes the optimizations?", "bold"))
    print(f"    {c('1', 'cyan', 'bold')}  rules only")
    for i, (name, _, ready, note) in enumerate(choices, start=2):
        print(f"    {c(str(i), 'cyan', 'bold')}  rules + {name:<7} " + c(f"({note})", "grey" if ready else "yellow"))
    last = len(choices) + 2
    print(f"    {c(str(last), 'cyan', 'bold')}  compare: the rules and every LLM that is ready, side by side")
    try:
        answer = input(c("  > [1] ", "cyan")).strip() or "1"
        number = int(answer) if answer.isdigit() and 1 <= int(answer) <= last else 1
        timed = input(c("  Cost model: Enter = static count, t = measured execution time > ", "cyan")).strip().lower()
    except EOFError:
        return None
    chosen = with_llm(args, None if number in (1, last) else choices[number - 2][1])
    chosen.cost_model = "time" if timed.startswith("t") else args.cost_model
    return chosen, "rule" if number in (1, last) else "hybrid", number == last


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
    real = real_files()
    if real:
        print(f"    {c('r', 'cyan', 'bold')}  a real program, picked at random from the {len(real)} Codeforces submissions")
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
        if choice.lower() == "r" and real:
            path = random.choice(real)
        elif choice.isdigit() and 1 <= int(choice) <= len(samples):
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
        for prefix in ("LLM proposal: ", "LLM repair: ", "LLM produced no usable TAC: "):
            text = text.replace(prefix, "")
        return text
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
        if e.phase in ("analyze", "route") and verbose:
            flush()
            print(c(f"       {'route to ' if e.phase == 'route' else ''}{e.description}", "grey"))
        elif e.phase == "repair":
            flush()
            print(c("         self-repair: the LLM is told what was wrong and asked again", "magenta"))
            print(c(f"         {clip(e.reason or '', 66)}", "grey"))
        elif e.phase == "propose":
            flush()
            kind = llm_label(result) if e.source == "llm" else e.opportunity_type
            if e.description.startswith("LLM repair: "):
                kind += " repair"
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
            (llm_label(result), count_outcomes(llm), "magenta"),
            ("Total", count_outcomes(result.proposals), "bold")]

    print("  " + c(f"{'Source':<16}{'Suggested':>10}{'Correct':>10}{'Accepted':>10}"
                   f"{'No gain':>9}{'Wrong':>9}", "bold"))
    print("  " + c("-" * 64, "grey"))
    for label, n, colour in rows:
        if label == "Total":
            print("  " + c("-" * 64, "grey"))
        line = (f"{label:<16}{n['suggested']:>10}{n['verified']:>10}{n['accepted']:>10}"
                f"{n['no_gain']:>9}{n['invalid']:>9}")
        print("  " + c(line, colour))
    print()
    print(c("  Suggested = proposals made   Correct = passed the correctness check", "grey"))
    print(c("  No gain   = correct but not cheaper   Wrong = failed the correctness check, so it was blocked", "grey"))

    if llm_enabled:
        unusable = result.llm_calls - len(llm)
        text = f"  LLM requests sent: {result.llm_calls}"
        if result.llm_calls:
            text += f"  ({len(llm)} usable suggestion{'s' if len(llm) != 1 else ''}"
            text += f", {unusable} unusable repl{'ies' if unusable != 1 else 'y'})" if unusable else ")"
        print(c(text, "magenta"))
        if result.llm_repairs:
            print(c(f"  Self-repair: {result.llm_repairs} second tr{'ies' if result.llm_repairs != 1 else 'y'} "
                    f"after a rejected answer, {result.llm_repairs_accepted} accepted", "magenta"))
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
        print("  " + c(f"{'By optimization type':<30}{'Suggested':>10}{'Correct':>9}{'Accepted':>10}"
                       f"{'No gain':>9}{'Wrong':>7}", "bold"))
        print("  " + c("-" * 75, "grey"))
        for key in TYPE_LABELS:
            if key in by_type:
                n = by_type[key]
                print(f"  {TYPE_LABELS[key]:<30}{sum(n.values()):>10}{n['accepted'] + n['rejected']:>9}"
                      f"{n['accepted']:>10}{n['rejected']:>9}{n['invalid']:>7}")

    # the wrong suggestions on their own, each with what the verifier found
    wrong = [e for e in result.log.entries if e.phase == "reject" and "Verification failed" in (e.reason or "")]
    if wrong:
        print()
        print("  " + c(f"Wrong suggestions, blocked by the verifier: {len(wrong)}", "red", "bold"))
        for e in wrong[:5]:
            who = llm_label(result) if e.source == "llm" else "rule"
            found = (e.reason or "").replace("Verification failed: ", "")
            print(c(f"    [{e.iteration:>2}] {who}: {clip(found, 58)}", "grey"))
        if len(wrong) > 5:
            print(c(f"    ... and {len(wrong) - 5} more (all in the decision log)", "grey"))
    elif result.proposals:
        print()
        print(c("  Wrong suggestions: none in this run.", "grey"))


# ---------------------------------------------------------------------- #
def run_program(program, inputs: dict[str, int]) -> str:
    try:
        return "prints " + str(TACInterpreter().execute(program, inputs, max_steps=200_000))
    except ExecutionTimeout as exc:
        return f"prints {exc.outputs} and is still running after 200,000 steps"
    except TACRuntimeError as exc:
        return f"prints {exc.outputs} then stops with an error: {exc}"


def make_orchestrator(mode: str, args) -> tuple[Orchestrator, bool, str]:
    """Returns (orchestrator, llm_enabled, note about the LLM when it is not enabled).

    ``mode`` is the Optimization Specialist's routing policy: "rule", "llm" or "hybrid".
    """
    if mode == "rule":
        return (Orchestrator(max_iterations=args.max_iterations, cost_model=args.cost_model), False,
                "not used (add --use-llm, or --offline for a local Ollama model)")
    if not args.offline:
        load_key_files(PROJECT_ROOT)      # .gemini_key / .groq_key
    orchestrator = Orchestrator(optimizer_mode=mode, max_iterations=args.max_iterations, cost_model=args.cost_model,
                                llm_provider=args.llm_provider, llm_model=args.llm_model,
                                offline=args.offline, max_llm_calls=3)
    llm = orchestrator.llm_optimizer
    if llm is None or not llm.available:
        reason = clip(llm.unavailable_reason if llm else "not configured", 100)
        orchestrator.llm_optimizer = None
        return orchestrator, False, f"unavailable ({reason})"
    return orchestrator, True, ""


def compare(source: str, name: str, args) -> int:
    """Optimize one program under the rules and under every LLM that is ready, and show the runs side by side."""
    strict = args.strict or is_real_program(name)
    stage(1, f"The C program  ({name})")
    for line in numbered(source.rstrip().splitlines(), start=1):
        print(line)
    try:
        tac, _ = compile_c(source, strict=strict)
    except CFrontendError as exc:
        print(c(f"\n  {exc}", "red", "bold"))
        return 1
    cost0 = CostEvaluator().evaluate(tac)
    stage(2, "Comparison: the same program under every proposer")
    print(f"  {len(tac)} TAC instructions, weighted cost {cost0.weighted_total:.1f}, cost model: {args.cost_model}")
    print()
    rows, status = [], 0
    for label, provider, ready in [("Rules only", None, True)] + [(f"Rules + {n}", p, r) for n, p, r, _ in llm_choices()]:
        if not ready:
            rows.append((label, None, "not ready"))
            continue
        orchestrator, enabled, note = make_orchestrator("hybrid" if provider else "rule", with_llm(args, provider))
        if provider and not enabled:
            rows.append((label, None, clip(note, 50)))
            continue
        print(c(f"  running: {label} ...", "grey"), flush=True)
        started = time.time()
        result = orchestrator.optimize(compile_c(source, strict=strict)[0], name)
        if result.stopped_reason:
            rows.append((label, None, clip(result.stopped_reason, 50)))
            status = 1
            continue
        rows.append((label, result, f"{time.time() - started:.1f}s"))
        status = status or (0 if result.output_match else 1)
    print()
    print("  " + c(f"{'Proposer':<16}{'Cost':>14}{'Less':>8}{'Time less':>11}{'LLM correct':>13}"
                   f"{'LLM wrong':>11}  {'Equivalence':<12}{'Took':>7}", "bold"))
    print("  " + c("-" * 94, "grey"))
    for label, result, note in rows:
        if result is None:
            print("  " + c(f"{label:<16}{note}", "grey"))
            continue
        llm = count_outcomes([p for p in result.proposals if p["source"] == "llm"])
        used = label != "Rules only"
        cost = f"{result.original_cost.weighted_total:.1f} → {result.final_cost.weighted_total:.1f}"
        check = "FAILED" if not result.output_match else "proved" if result.proved else "tested"
        line = (f"{label:<16}{cost:>14}{result.cost_reduction_pct:>7.1f}%{result.time_reduction_pct:>10.1f}%"
                f"{llm['verified'] if used else '-':>13}{llm['invalid'] if used else '-':>11}  {check:<12}{note:>7}")
        print("  " + c(line, "green" if result.output_match else "red"))
    print()
    print(c("  Less = static cost removed   Time less = execution time removed", "grey"))
    print(c("  LLM correct = LLM suggestions that passed verification   LLM wrong = blocked by the verifier", "grey"))
    print(c("  Equivalence: proved = for every input (symbolic check or Z3), tested = on the verifier's inputs", "grey"))
    return status


def run_demo(source: str, name: str, args, pacer: Pacer, mode: str) -> int:
    # ------------------------------------------------------------ stage 1
    strict = args.strict or is_real_program(name)
    stage(1, f"The C program  ({name})")
    for line in numbered(source.rstrip().splitlines(), start=1):
        print(line)
    if strict:
        print(c("  strict C mode: printed text and early returns are kept, so every output is checked", "cyan"))

    try:
        tac, cprog = compile_c(source, strict=strict)
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
    print("  weighted cost = " + c(f"{cost0.weighted_total:.1f}", "bold", "yellow")
          + f"    execution time = {cost0.exec_time:.1f} cycles (average over the profile inputs)")
    if input_names:
        shown = ", ".join(c_names.get(n, n) for n in input_names)
        print(c(f"  inputs (scanf): {shown} - the verifier will test many different values", "cyan"))
    pacer.pause("Enter to start the agent loop")

    # ------------------------------------------------------------ stage 3
    stage(3, "Agent loop: Analyze → Propose → Verify → Evaluate → Accept/Reject")
    orchestrator, llm_enabled, llm_note = make_orchestrator(mode, args)
    if mode != "rule" and not llm_enabled:
        print(c(f"  LLM {llm_note}; continuing with rules only.", "yellow"))
    elif llm_enabled:
        llm = orchestrator.llm_optimizer
        why = f" - {llm.selected_because}" if llm.selected_because else ""
        print(c(f"  Routing: {mode} ({MODE_SUMMARIES[mode]}).", "magenta"))
        print(c(f"  LLM: {llm.label}{why}", "magenta"))
        print(c("  (waiting for the LLM can take a few seconds, longer for a local model)", "grey"))
    started = time.time()
    result = orchestrator.optimize(tac, name)
    elapsed = time.time() - started
    hidden = replay(result, pacer, args.verbose)
    print()
    if getattr(orchestrator.llm_optimizer, "cpu_fallback", False):
        print(c("  note: Ollama's GPU runner crashed, so the model ran on the CPU (slower).", "yellow"))
        print(c("  Updating the NVIDIA driver usually fixes this.", "yellow"))
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
    print(f"  execution time: {result.original_cost.exec_time:.1f} → {result.final_cost.exec_time:.1f} cycles "
          f"({result.time_reduction_pct:.1f}% less)")
    proof = PROOF_LABELS.get(result.final_check_method, "proved for all inputs") if result.proved else \
        "tested on the verifier's inputs"
    if result.output_match:
        print("  equivalence: " + (c(proof, "green") if result.proved else proof))
        if not result.proved and not z3_available():
            print(c("    (pip install z3-solver to have programs without loops proved by the SMT solver)", "grey"))
    verdict = c("PASS", "green", "bold") if result.output_match else c("FAIL", "red", "bold")
    print(f"  verifier, final check against the original: {verdict}")
    print(c(f"    {clip(result.final_check_reason, 70)}", "grey"))

    counts = count_outcomes(result.proposals)
    print()
    print(c("  " + "-" * (WIDTH - 2), "blue"))
    print(c("  SUMMARY", "bold", "blue") + c(f"   {name}, cost model: {args.cost_model}", "grey"))
    print(f"    weighted cost    {cost0.weighted_total:.1f} → {f.weighted_total:.1f}"
          + c(f"   {result.cost_reduction_pct:.1f}% less", "green", "bold"))
    print(f"    execution time   {result.original_cost.exec_time:.1f} → {result.final_cost.exec_time:.1f} cycles"
          + c(f"   {result.time_reduction_pct:.1f}% less", "green", "bold"))
    print(f"    suggestions      {counts['suggested']} made: {counts['verified']} correct "
          f"({counts['accepted']} accepted), " + c(f"{counts['invalid']} wrong and blocked",
                                                   "red" if counts["invalid"] else "grey"))
    print(f"    equivalence      {proof if result.output_match else 'FAILED'}")
    print(c("  " + "-" * (WIDTH - 2), "blue"))

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
    ap.add_argument("--optimizer", choices=MODES, default=None,
                    help="how each step is routed: " + "; ".join(f"{m} = {MODE_SUMMARIES[m]}" for m in MODES)
                         + " (default: rule, or hybrid with --use-llm / --offline)")
    ap.add_argument("--use-llm", action="store_true", help="add the LLM proposer (same as --optimizer hybrid)")
    ap.add_argument("--offline", action="store_true",
                    help="offline mode: the LLM is a local Ollama model, no internet or API key needed")
    ap.add_argument("--llm-provider", default="auto", choices=["auto", *sorted(PROVIDERS)],
                    help="auto = gemini or groq when online and a key is set, otherwise ollama")
    ap.add_argument("--llm-model", default=None, help="model ID for the LLM")
    ap.add_argument("--max-iterations", type=int, default=200, help="agent iteration cap (default 200)")
    ap.add_argument("--cost-model", choices=["static", "time"], default="static",
                    help="what counts as cheaper: static cost (default), or measured execution time first")
    ap.add_argument("--compare", action="store_true",
                    help="run the program under the rules and under every LLM that is ready, and compare the runs")
    ap.add_argument("--strict", action="store_true",
                    help="strict C mode: keep printed text and early returns (always on for the real-program dataset)")
    ap.add_argument("--delay", type=float, default=0.12, help="seconds between decisions")
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args()

    Style.enabled = not args.no_color and sys.stdout.isatty()
    if Style.enabled and os.name == "nt":
        os.system("")   # switches the Windows console to ANSI colour mode
    pacer = Pacer(args.fast, args.step, args.delay)
    mode = args.optimizer or ("hybrid" if args.use_llm or args.offline else "rule")
    banner()

    if args.file:
        try:
            with open(args.file, encoding="utf-8") as fh:
                source = fh.read()
        except OSError as exc:
            print(c(f"  Cannot read '{args.file}': {exc.strerror or exc}", "red"))
            return 1
        if args.compare:
            return compare(source, os.path.basename(args.file), args)
        return run_demo(source, os.path.basename(args.file), args, pacer, mode)

    if not sys.stdin.isatty():            # piped input: treat it as a pasted program
        return run_demo(sys.stdin.read(), "pasted_program.c", args, pacer, mode)

    # The menu asks who proposes, unless the command line already said so.
    ask_setup = mode == "rule" and args.optimizer is None and not args.compare
    status = 0
    while True:
        chosen = choose_program()
        if chosen is None:
            return status
        source, name = chosen
        run_args, run_mode, side_by_side_runs = args, mode, args.compare
        if ask_setup:
            setup = choose_setup(args)
            if setup is None:
                return status
            run_args, run_mode, side_by_side_runs = setup
        if side_by_side_runs:
            status = compare(source, name, run_args)
        else:
            status = run_demo(source, name, run_args, pacer, run_mode)
        if not ask_yes_no("Run another program?", default=True):
            return status


if __name__ == "__main__":
    sys.exit(main())
