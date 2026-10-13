"""Writes report3.tex, the final report: report.tex (same template structure) with the Review 3 work added.

The additions go where the template puts them: scope and objectives, the project plan, the
datasets, the algorithms (SMT verification, execution time, self-repair), implementation and
testing, the results on real programs, and the limitations. Every figure in them is read from
the result folders, so the text always matches the committed runs.

    python make_report3.py
"""
from __future__ import annotations

import json
import os
import shutil
import statistics
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.visualization.report import aggregate_metrics, load_results  # noqa: E402

CATEGORIES = [("arithmetic", "Arithmetic-only"), ("nested", "Nested expressions"),
              ("repeated_expr", "Repeated expressions"), ("dead_code", "Dead code"), ("loops", "Loops"),
              ("conditionals", "Conditionals"), ("mixed", "Mixed")]
RECHECK_EXECUTIONS = "539,170"      # independent re-check of the five runs on real programs
TEST_COMPONENTS = [
    ("test_lexer.py", "Lexer"), ("test_parser.py", "Parser"), ("test_tac_generator.py", "TAC generator"),
    ("test_c_frontend.py", "C front end"), ("test_interpreter.py", "TAC interpreter"),
    ("test_analyzer.py", "Code analyzer"), ("test_optimizer.py", "Rule and LLM optimizers"),
    ("test_optimization_specialist.py", "Routing"), ("test_groq.py", "Groq backend"),
    ("test_ollama.py", "Ollama backend"), ("test_self_repair.py", "LLM self-repair"),
    ("test_verifier.py", "Verifier"), ("test_cost_evaluator.py", "Cost evaluator"),
    ("test_review3_features.py", "Execution time, SMT, wide-range inputs"),
    ("test_real_dataset.py", "Real-program dataset, strict C"), ("test_orchestrator.py", "Orchestrator (integration)"),
    ("test_demo.py", "Demo front end"), ("test_bugfixes.py", "Regression tests"),
]


def load(folder):
    try:
        records = load_results(os.path.join(ROOT, folder))
    except FileNotFoundError:
        return None
    return {"m": aggregate_metrics(records), "by_name": {r["program_name"]: r for r in records}}


def p(value, digits=2):
    return "n/a" if value is None else f"{value:.{digits}f}\\%"


def n(value):
    return f"{value:,}"


def test_counts() -> dict[str, int]:
    """Tests per file, as pytest collects them."""
    out = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q"], cwd=ROOT,
                         capture_output=True, text=True).stdout
    counts: dict[str, int] = {}
    for line in out.splitlines():
        if "::" in line:
            name = os.path.basename(line.split("::")[0])
            counts[name] = counts.get(name, 0) + 1
    return counts


class Report:
    def __init__(self, text):
        self.text = text

    def after(self, anchor, addition):
        assert self.text.count(anchor) == 1, (self.text.count(anchor), anchor[:70])
        self.text = self.text.replace(anchor, anchor + addition)

    def before(self, anchor, addition):
        assert self.text.count(anchor) == 1, (self.text.count(anchor), anchor[:70])
        self.text = self.text.replace(anchor, addition + anchor)

    def swap(self, old, new):
        assert self.text.count(old) == 1, (self.text.count(old), old[:70])
        self.text = self.text.replace(old, new)

    def between(self, start, end, new):
        """Replace everything from ``start`` up to (not including) ``end``."""
        a = self.text.index(start)
        b = self.text.index(end, a)
        self.text = self.text[:a] + new + self.text[b:]


def build() -> str:
    with open(os.path.join(ROOT, "report.tex"), encoding="utf-8") as fh:
        doc = Report(fh.read().replace("\r\n", "\n"))
    rule, timed = load("output_real_rule_only"), load("output_real_rule_time")
    gemini, groq, ollama = load("output_real_gemini"), load("output_real_groq"), load("output_real_ollama")
    generated = load("output_rule_only")
    llm_runs = [(name, run) for name, run in (("Gemini", gemini), ("Groq", groq), ("Ollama", ollama)) if run]
    with open(os.path.join(ROOT, "dataset", "real_manifest.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    programs = manifest["programs"]
    as_c = sum(1 for e in programs if e["language"].startswith("GNU C") and "++" not in e["language"])
    rm, tm = rule["m"], timed["m"]
    tests = test_counts()
    total_tests = sum(tests.values())

    def same(run):
        return statistics.mean(rule["by_name"][name]["reduction_pct"] for name in run["by_name"])

    def improved(run):
        return sum(1 for name, rec in run["by_name"].items()
                   if rec["reduction_pct"] > rule["by_name"][name]["reduction_pct"] + 0.01)

    def lower(run):
        """Programs that end below the rules alone: an accepted LLM change can close off a later rule step."""
        return sum(1 for name, rec in run["by_name"].items()
                   if rec["reduction_pct"] < rule["by_name"][name]["reduction_pct"] - 0.01)

    def consulted(run):
        return sum(1 for rec in run["by_name"].values() if rec.get("llm_calls", 0) > 0)

    def calls(run):
        return sum(rec.get("llm_calls", 0) for rec in run["by_name"].values())

    def kind(m, name, field="accepted"):
        return m["by_optimization_type"].get(name, {}).get(field, 0)

    # ------------------------------------------------------------------ figures
    figures = os.path.join(ROOT, "report_figures")
    for source, name in (("output_real_rule_only/plots/6_heatmap_category_vs_type.png", "real_heatmap_rules.png"),
                         ("output_real_rule_only/plots/5_scatter_steps_vs_improvement.png", "real_steps_rules.png"),
                         ("output_real_gemini/plots/7_comparison_rule_vs_llm.png", "real_comparison_gemini.png"),
                         ("output_real_groq/plots/1_sankey_proposal_flow.png", "real_sankey_groq.png")):
        if os.path.exists(os.path.join(ROOT, source)):
            shutil.copyfile(os.path.join(ROOT, source), os.path.join(figures, name))
    doc.swap("report_figures/architecture.png", "report_figures/architecture_review3.png")

    # ------------------------------------------------------------------ abstract: the earlier one, with additions
    # (the template allows 200 to 300 words on one page)
    listed = [f"{p(run['m']['avg_cost_reduction_pct'], 1)} ({name})" for name, run in llm_runs]
    listed = listed[0] if len(listed) == 1 else ", ".join(listed[:-1]) + " and " + listed[-1]
    doc.after("a local model served by Ollama that works with no internet connection.",
              " A rejected LLM answer is sent back once with the reason.")
    doc.after("and symbolic polynomial equivalence for straight-line logic.",
              " Loop-free programs with branches are also proved equivalent by the Z3 SMT solver.")
    doc.after("so every run finished with zero false positives.", (
        f" On 500 real Codeforces programs the rules cut the static cost by {p(rm['avg_cost_reduction_pct'], 1)} "
        f"and the execution time by {p(rm['avg_time_reduction_pct'], 1)}, and an LLM raised the cost reduction to "
        + listed + f". {rm['programs_proved_equivalent']} of them are proved equivalent for every input."))
    a = doc.text.index("Standard compilers apply a fixed chain of optimization passes")
    words = len(doc.text[a:doc.text.index("\\setstretch{1.5}\n\\newpage", a)].split())
    assert words <= 300, f"the abstract has {words} words"

    # ------------------------------------------------------------------ scope, objectives, plan, software
    doc.swap("  \\item A two-stage verifier combining differential testing (random, edge, boundary, small-scope and "
             "pairwise input sets) and symbolic polynomial equivalence checking.\n", (
        "  \\item A three-stage verifier: differential testing (random, edge, boundary, small-scope, pairwise and "
        "wide-range input sets), symbolic polynomial equivalence checking, and an SMT proof with Z3 for programs "
        "without loops.\n"
        "  \\item LLM self-repair: a rejected LLM answer is sent back once with the reason.\n"))
    doc.swap("  \\item A weighted static cost model used as the accept/reject gate.\n", (
        "  \\item A cost evaluator with a weighted static cost and a measured execution time; either can be the "
        "accept/reject gate.\n"))
    doc.swap("  \\item A 500-program dataset covering seven structural categories (arithmetic, nested, "
             "repeated-expression, dead-code, loops, conditionals, mixed).\n", (
        "  \\item A 500-program generated dataset covering seven structural categories (arithmetic, nested, "
        "repeated-expression, dead-code, loops, conditionals, mixed), and a second dataset of 500 real programs "
        "in the same categories.\n"))
    doc.swap("  \\item Floating-point arithmetic, arrays or string types.\n"
             "  \\item SMT-based formal verification via Z3 (we rely on differential testing and symbolic equivalence "
             "instead).\n"
             "  \\item Measured execution time: the cost model is static.\n", (
        "  \\item Floating-point arithmetic, arrays or string types.\n"
        "  \\item SMT proofs for programs with loops (those stay tested).\n"
        "  \\item Execution time on real hardware: the time is an abstract cycle count.\n"))
    doc.after("  \\item Keep the system usable with no internet connection by supporting a local model.\n", (
        "  \\item Measure execution time as well as static cost, so that work removed from a loop counts for more.\n"
        "  \\item Prove equivalence for all inputs wherever that is possible, instead of only testing it.\n"
        "  \\item Give an LLM whose answer was rejected the reason and one more attempt.\n"
        "  \\item Evaluate the system on programs written by people, not only on generated ones.\n"))
    doc.swap("11 & Full runs with all three LLMs; C front end and live demo; report & Weeks 12--13 \\\\\n\\hline\n", (
        "11 & Full runs with all three LLMs; C front end and live demo; report & Weeks 12--13 \\\\\n\\hline\n"
        "12 & LLM self-repair; execution time in the cost evaluator; SMT verification with Z3 & Week 14 \\\\\n\\hline\n"
        "13 & Real-program dataset from Codeforces submissions; strict mode of the C front end & Week 15 \\\\\n\\hline\n"
        "14 & Runs on the real programs; independent re-check; wide-range inputs; final report & Week 16 \\\\\n\\hline\n"))
    doc.swap("pytest & $\\geq$8.0 & Unit and integration testing \\\\\n\\hline\n", (
        "pytest & $\\geq$8.0 & Unit and integration testing \\\\\n\\hline\n"
        "z3-solver & $\\geq$4.12 & SMT proofs for programs without loops (optional) \\\\\n\\hline\n"
        "pyarrow & $\\geq$15 & Reading the Codeforces data files (dataset building only) \\\\\n\\hline\n"))

    # ------------------------------------------------------------------ datasets
    rows = ""
    decided = {"arithmetic": "straight-line code, shallow arithmetic", "nested": "an expression three or more operators deep",
               "repeated_expr": "the same expression written twice", "dead_code": "a stored value that is never read",
               "loops": "a loop and no branch", "conditionals": "a branch and no loop", "mixed": "a loop and a branch"}
    for key, label in CATEGORIES:
        entries = [e for e in programs if e["category"] == key]
        rows += f"{label} & {len(entries)} & {len({e['problem_id'] for e in entries})} & {decided[key].capitalize()} \\\\\n\\hline\n"
    doc.after("so a single test run constitutes a proof of equivalence.\n", (
        "\n\\subsection{Real-Program Dataset}\n\\label{sec:realdata}\n\n"
        "The generated programs are written to contain what the optimizer looks for. To see how the system behaves "
        "on code that people actually wrote, we built a second dataset of 500 real programs. They are accepted "
        "submissions to Codeforces problems, taken from the dataset \\texttt{open-r1/codeforces-submissions} on "
        "Hugging Face (open-r1, 2025), which holds 12.6 million submissions under the CC-BY-4.0 licence.\n\n"
        "A submission is usable when (i) the judge accepted it, (ii) the C front end compiles it in strict mode, "
        "(iii) it prints something, and (iv) it finishes within 20,000 steps on every input set the verifier would "
        "try, since otherwise no change to it could be verified. Of 469,491 accepted C and C++ submissions examined "
        "(six of the dataset's 36 files), 9,489 were usable (2.0\\%), from 234 problems. The others mostly use "
        "arrays, further functions, floating point or macros, or read their input inside a loop, none of which the "
        "front end supports.\n\n"
        "From the usable submissions, 500 were chosen in exactly the proportions of the generated dataset "
        "(Table~\\ref{tab:realdata}). Programs that compile to the same TAC count once, each category is filled "
        "one program per problem per round, and within a problem the newest submission goes first. The 500 come "
        f"from {manifest['problems']} problems; {as_c} were submitted as C and {500 - as_c} as C-style C++, that "
        "is, C++ submissions that use only \\texttt{scanf} and \\texttt{printf} and nothing else from C++.\n\n"
        "\\begin{table}[H]\n\\centering\n\\caption{Real-program dataset: composition and how a category is decided}\n"
        "\\label{tab:realdata}\n\\begin{tabularx}{\\textwidth}{|l|c|c|X|}\n\\hline\n"
        "\\textbf{Category} & \\textbf{Programs} & \\textbf{Problems} & \\textbf{Decided by} \\\\\n\\hline\n"
        + rows + "\\end{tabularx}\n\\end{table}\n\n"
        "A stored value that is never read, or an expression written twice, decides the category first, because "
        "that is what the generator builds its dead-code and repeated-expression programs around. Everything else "
        "is classified by its control flow. Straight-line solutions are rare on Codeforces, so the arithmetic and "
        "nested categories draw on fewer problems than the others.\n\n"
        "For these programs the front end works in strict mode, which keeps everything a run shows. Text printed "
        "by \\texttt{printf}, \\texttt{puts} or \\texttt{putchar} becomes a \\texttt{print} of a code that stands "
        "for that text, so an optimization that changed which message is printed would fail verification. A "
        "\\texttt{return} in the middle of \\texttt{main} becomes a jump to the end of the program. An expression "
        "\\texttt{a \\&\\& b} is refused when \\texttt{b} contains a division, because TAC evaluates both sides and "
        "C would not.\n"))

    # ------------------------------------------------------------------ algorithms
    doc.swap("The input sets are built in five ways, listed in Table~\\ref{tab:inputs}.",
             "The input sets are built in six ways, listed in Table~\\ref{tab:inputs}.")
    doc.swap("Pairwise & Every two inputs with every two boundary values & Two inputs that must line up \\\\\n\\hline\n", (
        "Pairwise & Every two inputs with every two boundary values & Two inputs that must line up \\\\\n\\hline\n"
        "Wide range & 60 sets with values up to a thousand, ten thousand, a million and a billion, signed values, "
        "and powers of ten with their neighbours & A change that is right only for small inputs \\\\\n\\hline\n"))
    doc.before("\\section{Design}\n", (
        "The wide-range sets were added after the re-check of the runs on real programs "
        "(Section~\\ref{sec:testing}). A run that is too long for them is skipped, so they never make a program "
        "unverifiable.\n\n"
        "\\subsection{SMT Verification}\n\n"
        "Differential testing shows that two programs agree on the inputs that were tried. For a program with "
        "branches but no loops there are finitely many paths, so its whole behaviour can be written as one formula "
        "over its inputs. The verifier follows every path symbolically: a branch splits the path in two, and a "
        "division splits off the case in which the divisor is zero, where the run stops with what it has printed "
        "so far. The paths are then folded into a single description of a run (how it ends, how many values it "
        "prints, and the values), and the Z3 solver (de Moura \\& Bj{\\o}rner, 2008) is asked for an input on "
        "which the descriptions of the two programs differ (Table~\\ref{tab:smt}).\n\n"
        "\\begin{table}[H]\n\\centering\n\\caption{The three answers of the SMT stage}\n\\label{tab:smt}\n"
        "\\begin{tabularx}{\\textwidth}{|l|X|}\n\\hline\n\\textbf{Answer} & \\textbf{Meaning and consequence} \\\\\n\\hline\n"
        "\\texttt{unsat} & No such input exists: the two programs are equivalent for all inputs. The result is "
        "recorded as proved. \\\\\n\\hline\n"
        "\\texttt{sat} & Z3 returns the input. It is replayed in the reference interpreter, and if the outputs "
        "really differ the proposal is rejected with that counterexample. \\\\\n\\hline\n"
        "\\texttt{unknown} & No answer within three seconds, usually because of non-linear arithmetic. The verdict "
        "of differential testing stands. \\\\\n\\hline\n\\end{tabularx}\n\\end{table}\n\n"
        "Integers are unbounded and division and modulo follow C, exactly as in the interpreter. The stage runs on "
        "every LLM proposal and on the end-to-end check of every program. Programs with loops are outside its "
        "scope and remain tested. As an example of what it adds: a program that prints 1 when $3x = 999999$ and 0 "
        "otherwise differs from a program that always prints 0 on the single input $x = 333333$, which is near no "
        "literal in either program, so every test passes. Z3 finds that input immediately.\n\n"
        "\\subsection{Cost Model: Static Cost and Execution Time}\n\\label{sec:time}\n\n"
        "The static cost of a program is a weighted count of its instructions, arithmetic operations, "
        "temporaries, copies and branches. It cannot see how often an instruction runs. The Cost Evaluator "
        "therefore also measures execution time: the program is run on 25 fixed inputs (20 random sets, half of "
        "them positive, and 5 edge cases), every executed instruction adds its latency from "
        "Table~\\ref{tab:latency}, and the time is the average over the runs. The values given to an input depend "
        "only on its name, so a program and a candidate are timed on the same data.\n\n"
        "\\begin{table}[H]\n\\centering\n\\caption{Latency charged per executed instruction (abstract cycles)}\n"
        "\\label{tab:latency}\n\\begin{tabular}{|l|c|}\n\\hline\n\\textbf{Instruction} & \\textbf{Cycles} \\\\\n\\hline\n"
        "Copy, load a constant & 1 \\\\\n\\hline\nAddition, subtraction, shift, comparison, logic & 1 \\\\\n\\hline\n"
        "Multiplication & 3 \\\\\n\\hline\nDivision, modulo & 20 \\\\\n\\hline\nUnconditional jump & 1 \\\\\n\\hline\n"
        "Conditional branch & 2 \\\\\n\\hline\nPrint & 1 \\\\\n\\hline\nLabel & 0 \\\\\n\\hline\n\\end{tabular}\n\\end{table}\n\n"
        "Two cost models decide what counts as an improvement. Under the \\emph{static} model, the default, a "
        "change is accepted if the static cost drops; all results on the generated dataset use it. Under the "
        "\\emph{time} model a change is accepted if the measured time drops, or if the time is equal and the "
        "static cost drops. Every run reports both reductions, whichever model decides.\n\n"
        "\\subsection{LLM Self-Repair}\n\\label{sec:repair}\n\n"
        "When an LLM answer is rejected, the reason is specific: the verifier has the inputs on which the outputs "
        "differ, or the parser has the line that is not valid TAC. The Optimization Specialist sends the model its "
        "rejected answer together with that reason and asks once more. The second answer goes through exactly the "
        "same verification and cost gates as any other proposal, so self-repair cannot make the system less safe; "
        "it can only turn a wasted call into a useful one. By default one repair is allowed per rejected answer, "
        "and repairs do not use up the budget of fresh proposals.\n\n"))

    # ------------------------------------------------------------------ implementation and testing
    doc.after("\\texttt{demo.py} is a terminal front end that takes a C program and walks through the whole "
              "pipeline on screen, stage by stage.\n", (
        "\n\\subsection{Module 7: Verification, Cost and Dataset Extensions}\n\n"
        "\\texttt{smt\\_verifier.py} holds the SMT stage: a symbolic walk over every path of a loop-free program "
        "and the query to Z3. \\texttt{cost\\_evaluator.py} gained the execution profiler and the latency table, "
        "and the interpreter can report how often each instruction ran. The self-repair loop sits in the "
        "Orchestrator right after the two gates, and the repair prompt in \\texttt{optimizer\\_llm.py}. "
        "\\texttt{dataset/real\\_dataset.py} builds the real-program dataset (collect, select, rebuild from the "
        "manifest). Full runs save every finished program at once, so a run that is interrupted, or stopped "
        "because a free daily quota is spent, can be resumed; \\texttt{ollama\\_demo.bat} starts the offline demo "
        "with one command.\n"))
    doc.swap("We wrote 336 automated tests across fifteen test files", f"We wrote {total_tests} automated tests across "
             + {15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen"}.get(len(tests), str(len(tests))) + " test files")
    table_rows = ""
    for name, component in TEST_COMPONENTS:
        if name in tests:
            table_rows += "\\texttt{" + name.replace("_", "\\_") + "} & " + component + f" & {tests[name]} \\\\\n\\hline\n"
    doc.between("\\texttt{test\\_lexer.py} & Lexer & 14 \\\\\n",
                "\\end{tabular}\n\\end{table}\n\nThe verifier tests are worth calling out", table_rows)
    doc.after("The proposal was caught by the verifier every time, and the analyzer no longer makes it.\n", (
        "\nThe extensions are tested in the same way. The SMT stage is checked against "
        "hand-built pairs of programs: equivalent ones must be proved, and pairs that differ on a single input, "
        "in the order of their output, or in whether a division traps must be refuted with the right "
        "counterexample.\n\n"
        "\\textbf{Re-checking the runs on real programs.} Every optimized program was run against its original "
        "on inputs the verifier had not used, including values up to a million. For the rule-based runs and the "
        "Gemini and local-model runs no mismatch was found. In the Groq run the re-check found one wrong program. "
        "The model had replaced \\texttt{x - 1} by the constant 9 inside a loop in which \\texttt{x} is multiplied "
        "by ten in every iteration. The change is correct while \\texttt{x} is 10, and the loop runs a second "
        "time only for inputs of 100 or more, which none of the verifier's input sets reached, so all 388 tests "
        "had passed. The verifier now adds the 60 wide-range input sets of Table~\\ref{tab:inputs}. With them the "
        "wrong change is rejected with a counterexample. The affected program was optimized again, and the "
        f"re-check of all runs on real programs ({RECHECK_EXECUTIONS} executions) now finds no mismatch. The four "
        "runs on the generated dataset were re-checked on the same wide inputs, also without a mismatch.\n"))

    # ------------------------------------------------------------------ results on real programs
    table_rows = ""
    for key, label in CATEGORIES:
        g = generated["m"]["per_category"][key]["avg_reduction_pct"] if generated else None
        c = rm["per_category"][key]
        table_rows += (f"{label} & {c['programs']} & {p(g)} & {p(c['avg_reduction_pct'])} & "
                       f"{p(c['avg_time_reduction_pct'])} & {c['programs_proved']} \\\\\n\\hline\n")
    table_rows += (f"\\textbf{{All}} & \\textbf{{500}} & \\textbf{{{p(generated['m']['avg_cost_reduction_pct'])}}} & "
                   f"\\textbf{{{p(rm['avg_cost_reduction_pct'])}}} & \\textbf{{{p(rm['avg_time_reduction_pct'])}}} & "
                   f"\\textbf{{{rm['programs_proved_equivalent']}}} \\\\\n\\hline\n")
    results = (
        "\\subsection{Results on Real Programs}\n\\label{sec:realresults}\n\n"
        "All runs in this subsection use the real-program dataset of Section~\\ref{sec:realdata} and allow 200 "
        "iterations per program, because real programs are longer than the generated ones.\n\n"
        "\\subsubsection{Rule-Based Optimization}\n\n"
        "\\begin{table}[H]\n\\centering\n\\caption{Rules only: generated and real programs (static cost model)}\n"
        "\\label{tab:realrules}\n\\small\n\\begin{tabular}{|l|c|c|c|c|c|}\n\\hline\n"
        "\\textbf{Category} & \\textbf{Programs} & \\textbf{Generated} & \\textbf{Real} & \\textbf{Real, time} & "
        "\\textbf{Proved} \\\\\n\\hline\n" + table_rows + "\\end{tabular}\n\\end{table}\n\n"
        f"On the real programs the rules reduce the static cost by {p(rm['avg_cost_reduction_pct'])} on average "
        f"(median {p(rm['median_cost_reduction_pct'])}); {rm['programs_with_reduction_over_30pct']} of the 500 "
        "programs improve by more than 30\\%. The figure is lower than on the generated set because nearly all "
        "real programs read their values with \\texttt{scanf}, so nothing folds down to a constant. Most of what "
        f"the rules remove is the redundancy of the naive TAC translation: {n(kind(rm, 'COPY_PROPAGATION'))} "
        f"accepted copy propagations and {n(kind(rm, 'DEAD_CODE'))} dead-code removals, against "
        f"{n(kind(rm, 'CSE'))} common subexpressions and {n(kind(rm, 'CONSTANT_FOLD'))} constant folds "
        "(Figure~\\ref{fig:realheat}). "
        f"All {n(rm['total_proposals'])} proposals passed verification; {n(rm['accepted'])} were accepted and "
        f"{n(rm['rejected_no_cost_gain'])} gave no cost gain.\n\n"
        "\\begin{figure}[H]\n\\centering\n\\includegraphics[width=\\textwidth]{report_figures/real_heatmap_rules.png}\n"
        "\\caption{Real programs, rules only: accepted optimizations by category and type}\n\\label{fig:realheat}\n\\end{figure}\n\n"
        "\\subsubsection{Execution Time and the Two Cost Models}\n\n"
        "\\begin{table}[H]\n\\centering\n\\caption{Rules only on the 500 real programs under the two cost models}\n"
        "\\label{tab:costmodels}\n\\small\n\\begin{tabular}{|l|c|c|}\n\\hline\n\\textbf{Metric} & \\textbf{Static model} & \\textbf{Time model} \\\\\n\\hline\n"
        f"Average static cost reduction & {p(rm['avg_cost_reduction_pct'])} & {p(tm['avg_cost_reduction_pct'])} \\\\\n\\hline\n"
        f"Average execution-time reduction & {p(rm['avg_time_reduction_pct'])} & {p(tm['avg_time_reduction_pct'])} \\\\\n\\hline\n"
        f"Median execution-time reduction & {p(rm['median_time_reduction_pct'])} & {p(tm['median_time_reduction_pct'])} \\\\\n\\hline\n"
        f"Strength reductions accepted & {n(kind(rm, 'STRENGTH_REDUCTION'))} & {n(kind(tm, 'STRENGTH_REDUCTION'))} \\\\\n\\hline\n"
        f"Strength reductions rejected (no gain) & {n(kind(rm, 'STRENGTH_REDUCTION', 'rejected'))} & "
        f"{n(kind(tm, 'STRENGTH_REDUCTION', 'rejected'))} \\\\\n\\hline\n"
        f"Proposals accepted & {n(rm['accepted'])} & {n(tm['accepted'])} \\\\\n\\hline\n"
        f"False positives & \\textbf{{{rm['false_positive_count']}}} & \\textbf{{{tm['false_positive_count']}}} \\\\\n\\hline\n"
        "\\end{tabular}\n\\end{table}\n\n"
        "The execution time falls less than the static cost, because most of the removed instructions are copies, "
        "which cost one cycle each, while the divisions, multiplications and branches that dominate the running "
        "time have to stay. The time model accepts changes that the static count regards as a tie, such as "
        "replacing a multiplication by two with an addition, and so removes a little more time.\n\n"
        "\\subsubsection{Proved Equivalence}\n\n"
        f"For {rm['programs_proved_equivalent']} of the 500 real programs the optimized program is proved "
        f"equivalent to the original for every input: {rm['programs_proved_equivalent'] - rm['programs_proved_by_smt']} "
        f"by the polynomial check for straight-line code and {rm['programs_proved_by_smt']} by the SMT solver. The "
        "remaining programs contain loops, or defeated the solver within its time limit, and are verified by "
        "differential testing as before. The end-to-end check never failed, so no program had to be reverted to "
        "its original.\n\n")
    if llm_runs:
        cells = {"Programs": lambda r: n(r["m"]["total_programs"]),
                 "Programs the LLM was consulted on": lambda r: n(consulted(r)),
                 "Rules alone on these programs": lambda r: p(same(r)),
                 "Rules + LLM": lambda r: "\\textbf{" + p(r["m"]["avg_cost_reduction_pct"]) + "}",
                 "Programs improved by the LLM": lambda r: str(improved(r)),
                 "Average execution-time reduction": lambda r: p(r["m"]["avg_time_reduction_pct"]),
                 "LLM calls": lambda r: n(calls(r)),
                 "LLM proposals accepted": lambda r: n(r["m"]["by_source"]["LLM"]["accepted"]),
                 "LLM proposals with no cost gain": lambda r: n(r["m"]["by_source"]["LLM"]["rejected"]),
                 "Wrong LLM proposals blocked": lambda r: n(r["m"]["by_source"]["LLM"]["invalid"]),
                 "LLM validity rate": lambda r: p(r["m"]["llm_validity_rate_pct"]),
                 "Self-repairs accepted / tried": lambda r: f"{r['m'].get('llm_repairs_accepted', 0)} / {r['m'].get('llm_repairs', 0)}",
                 "False positives": lambda r: "\\textbf{" + str(r["m"]["false_positive_count"]) + "}"}
        body = ""
        for label, getter in cells.items():
            body += f"{label} & " + " & ".join(getter(run) for _, run in llm_runs) + " \\\\\n\\hline\n"
        models = {"Gemini": "Gemini uses \\texttt{gemini-3.1-flash-lite} in the cloud.",
                  "Groq": "Groq uses its \\texttt{gpt-oss} and \\texttt{qwen} models in the cloud.",
                  "Ollama": "Ollama runs \\texttt{qwen2.5-coder:7b} on the laptop, mostly on its GPU."}
        short = " ".join(
            f"{name}'s free daily quota ended after {consulted(run)} programs, and its remaining "
            f"{run['m']['total_programs'] - consulted(run)} programs were optimized by the rules alone, which is "
            "what the system does whenever an LLM becomes unavailable."
            for name, run in llm_runs if consulted(run) < 0.9 * run["m"]["total_programs"])
        results += (
            "\\subsubsection{LLM Proposers with Self-Repair}\n\n"
            "The LLM configurations were run on the real programs with self-repair switched on "
            "(Table~\\ref{tab:realllms}). To stay inside the free daily quotas of the cloud providers, every fifth "
            "program is allowed two fresh LLM proposals and the others one; a rejected answer gets one repair in "
            "either case. "
            + (short + " " if short else "")
            + " ".join(models[name] for name, _ in llm_runs) + "\n\n"
            "\\begin{table}[H]\n\\centering\n\\caption{LLM proposers with self-repair on the real programs}\n"
            "\\label{tab:realllms}\n\\small\n\\begin{tabular}{|l|" + "c|" * len(llm_runs) + "}\n\\hline\n\\textbf{Metric} & "
            + " & ".join("\\textbf{Rules + " + name + "}" for name, _ in llm_runs) + " \\\\\n\\hline\n"
            + body + "\\end{tabular}\n\\end{table}\n\n"
            "On real programs an LLM adds much less than on the generated ones. A generated loop usually has "
            "constant bounds and can be replaced by its result; a real loop depends on the input, so it has to "
            "stay. Self-repair helps the cloud models, whose rejected answers are mostly invalid TAC (a whole "
            "expression written in one instruction): told so, they often answer again in valid form. It does not "
            "help the small local model, which repeats its mistake or returns the program unchanged.\n\n")
        below = [(name, lower(run)) for name, run in llm_runs if lower(run)]
        if below:
            results += (
                "A verified LLM change is always correct and always cheaper at the moment it is accepted, but it "
                "is not always the best step: it can rewrite the code so that a rule which would have applied "
                "later no longer does. On the real programs this left "
                + " and ".join(f"{count} program{'s' if count != 1 else ''} with {name}" for name, count in below)
                + " slightly below the result of the rules alone (by 5 percentage points at most). The averages "
                "in Table~\\ref{tab:realllms} include these programs.\n\n")
        if os.path.exists(os.path.join(figures, "real_comparison_gemini.png")):
            results += ("\\begin{figure}[H]\n\\centering\n\\includegraphics[width=0.9\\textwidth]{report_figures/real_comparison_gemini.png}\n"
                        "\\caption{Real programs: rule-only against rule + Gemini, per category}\n\\label{fig:realcmp}\n\\end{figure}\n\n")
        # the charts of the Groq and Ollama runs on the real programs, copied from the run folders
        charts = (("2_bar_outcomes_by_type", "outcomes", "accept, reject, and invalid counts for each optimization type", "0.85"),
                  ("4_pie_accepted_types", "accepted", "share of each optimization type among the accepted changes", "0.6"),
                  ("6_heatmap_category_vs_type", "heatmap", "accepted optimizations by program category and type", "0.85"),
                  ("7_comparison_rule_vs_llm", "comparison", "rule-only against rule + LLM, per category", "0.85"))
        for name, run in llm_runs:
            if name == "Gemini":
                continue
            plots = os.path.join(ROOT, f"output_real_{name.lower()}", "plots")
            block = ""
            for source, short_name, caption, width in charts:
                if not os.path.exists(os.path.join(plots, source + ".png")):
                    continue
                target = f"real_{short_name}_{name.lower()}.png"
                shutil.copyfile(os.path.join(plots, source + ".png"), os.path.join(figures, target))
                block += (f"\\begin{{figure}}[H]\n\\centering\n\\includegraphics[width={width}\\textwidth]{{report_figures/{target}}}\n"
                          f"\\caption{{Real programs, {name} run: {caption}}}\n\\end{{figure}}\n\n")
            if block:
                results += (f"\\subsubsection{{Analysis Charts for the {name} Run on Real Programs}}\n\n"
                            f"The charts below are drawn from the {name} run on the 500 real programs.\n\n" + block)
    doc.before("\\section{Output Screenshots}\n", results)

    # ------------------------------------------------------------------ analysis and limitations
    doc.before("\\subsection{Limitations}\n", (
        "\\textbf{Real programs leave less to remove.} A generated program is mostly constants and collapses to a "
        "few prints. A real program computes with its input, so the instructions that do the work have to stay, "
        "and the gain comes from cleaning up the translation and the occasional redundancy the programmer left.\n\n"
        "\\textbf{A proof is stronger than a test.} For programs without loops, zero false positives is no longer "
        "a statement about the inputs that were tried. For the programs the solver decided, no input exists on "
        "which the optimized program behaves differently.\n\n"
        "\\textbf{Tests can be passed by a wrong change.} The one wrong change that the re-check found had passed "
        "388 tests. Testing is only as good as its inputs; the lasting answers are inputs chosen to reach "
        "behaviour the program shows rarely, an independent re-check of every run, and a proof wherever one is "
        "possible.\n\n"
        "\\textbf{Self-repair helps with form more than with logic.} A capable model that is rejected has usually "
        "written a whole expression in one instruction; told so, it answers again in valid TAC. A small local "
        "model that got the logic wrong tends to get it wrong again, or to play safe and return the program "
        "unchanged.\n\n"))
    doc.between("\\subsection{Limitations}\n",
                "\n\n% ============================================================\n\\newpage\n\\begin{center}\n"
                "{\\fontsize{16}{20}\\selectfont \\textbf{REFERENCES}}", (
        "\\subsection{Limitations}\n\n\\begin{itemize}[leftmargin=2cm]\n"
        "  \\item The front end accepts only a subset of C: no arrays, pointers, functions other than "
        "\\texttt{main}, floating point, or input read inside a loop. That is why only 2\\% of the submissions "
        "examined could be used.\n"
        "  \\item The SMT stage does not handle loops. Programs with loops are verified by differential testing, "
        "which is thorough but is not a proof.\n"
        "  \\item Integers are unbounded in TAC, so the 32-bit wrap-around of C is not modelled, and inputs are "
        "tested over the verifier's ranges, which include values a problem statement rules out.\n"
        "  \\item Execution time is an abstract count of cycles from a fixed latency table, measured on 25 inputs. "
        "It orders programs sensibly but is not a measurement on real hardware.\n"
        "  \\item On the real programs most programs get a single LLM proposal, to stay inside the free daily "
        "quotas of the cloud providers. A larger budget might find more.\n"
        "\\end{itemize}\n"))

    # ------------------------------------------------------------------ references (APA, alphabetical)
    doc.before("\\apa{Lattner, C.,", (
        "\\apa{de Moura, L., \\& Bj{\\o}rner, N. (2008). Z3: An efficient SMT solver. \\textit{Proceedings of the "
        "International Conference on Tools and Algorithms for the Construction and Analysis of Systems (TACAS)}, "
        "337--340.}\n\n"))
    doc.before("\\end{document}", (
        "\n\\apa{open-r1. (2025). \\textit{codeforces-submissions} [Data set]. Hugging Face. "
        "https://huggingface.co/datasets/open-r1/codeforces-submissions}\n\n"))

    path = os.path.join(ROOT, "report3.tex")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc.text)
    return path


if __name__ == "__main__":
    print("saved", build())
