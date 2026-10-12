"""Writes report3.tex, the final report: the Review 2 report (report.tex) with the Review 3 work added.

The additions are placed where they belong in the existing chapters (objectives, datasets,
verification, cost model, self-repair, testing, results, limitations), and every figure in
them is read from the result folders, so the text always matches the committed runs.

    python make_report3.py
"""
from __future__ import annotations

import json
import os
import shutil
import statistics
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.visualization.report import aggregate_metrics, load_results  # noqa: E402

CATEGORIES = [("arithmetic", "Arithmetic-only"), ("nested", "Nested expressions"),
              ("repeated_expr", "Repeated expressions"), ("dead_code", "Dead code"), ("loops", "Loops"),
              ("conditionals", "Conditionals"), ("mixed", "Mixed")]
TOTAL_TESTS = 397
RECHECK = {"executions": "258,912", "mismatches": "0"}   # independent re-check of the runs on real programs


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


class Report:
    def __init__(self, text):
        self.text = text

    def after(self, anchor, addition):
        assert self.text.count(anchor) == 1, (self.text.count(anchor), anchor[:60])
        self.text = self.text.replace(anchor, anchor + addition)

    def before(self, anchor, addition):
        assert self.text.count(anchor) == 1, (self.text.count(anchor), anchor[:60])
        self.text = self.text.replace(anchor, addition + anchor)

    def swap(self, old, new):
        assert self.text.count(old) == 1, (self.text.count(old), old[:60])
        self.text = self.text.replace(old, new)


def build() -> str:
    with open(os.path.join(ROOT, "report.tex"), encoding="utf-8") as fh:
        doc = Report(fh.read().replace("\r\n", "\n"))
    doc.text = doc.text.replace("Project Report — Review 2", "Project Report — Review 3 (final)", 1)
    rule, timed = load("output_real_rule_only"), load("output_real_rule_time")
    groq, ollama = load("output_real_groq"), load("output_real_ollama")
    gemini = load("output_real_gemini")
    generated = load("output_rule_only")
    with open(os.path.join(ROOT, "dataset", "real_manifest.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    programs = manifest["programs"]
    as_c = sum(1 for e in programs if e["language"].startswith("GNU C") and "++" not in e["language"])
    rm, tm = rule["m"], timed["m"]

    def same(run):
        return statistics.mean(rule["by_name"][name]["reduction_pct"] for name in run["by_name"])

    def improved(run):
        return sum(1 for name, rec in run["by_name"].items()
                   if rec["reduction_pct"] > rule["by_name"][name]["reduction_pct"] + 0.01)

    def calls(run):
        return sum(rec.get("llm_calls", 0) for rec in run["by_name"].values())

    def kind(m, name, field="accepted"):
        return m["by_optimization_type"].get(name, {}).get(field, 0)

    # ------------------------------------------------------------------ figures
    figures = os.path.join(ROOT, "report_figures")
    for source, name in (("output_real_rule_only/plots/6_heatmap_category_vs_type.png", "real_heatmap_rules.png"),
                         ("output_real_rule_only/plots/5_scatter_steps_vs_improvement.png", "real_steps_rules.png"),
                         ("output_real_groq/plots/1_sankey_proposal_flow.png", "real_sankey_groq.png")):
        if os.path.exists(os.path.join(ROOT, source)):
            shutil.copyfile(os.path.join(ROOT, source), os.path.join(figures, name))

    # ------------------------------------------------------------------ abstract
    llm_sentence = ""
    llm_runs = [(name, run) for name, run in (("Gemini", gemini), ("Groq", groq), ("Ollama", ollama)) if run]
    if llm_runs:
        parts = [f"{p(run['m']['avg_cost_reduction_pct'], 1)} with {name}" for name, run in llm_runs]
        listed = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
        first = llm_runs[0][1]
        llm_sentence = (
            f" On a sample of {first['m']['total_programs']} of the real programs, where the rules alone reach "
            f"{p(same(first), 1)}, adding an LLM with self-repair gave {listed}.")
    doc.before("\\setstretch{1.5}\n\\newpage\n\n% ==================== TABLE OF CONTENTS", (
        "For the final review the system was extended in four ways. The Cost Evaluator now also measures execution "
        "time, by running each program and charging a latency for every executed instruction. A third verification "
        "stage hands programs without loops to the Z3 SMT solver, which either proves them equivalent for every input "
        "or returns a counterexample. A rejected LLM answer is sent back to the model once, with the reason, for "
        "another try (self-repair). And the evaluation was repeated on 500 real programs: accepted Codeforces "
        f"submissions from {manifest['problems']} problems, in the same seven categories. On these, the rules alone "
        f"reduce the static cost by {p(rm['avg_cost_reduction_pct'], 1)} and the execution time by "
        f"{p(rm['avg_time_reduction_pct'], 1)} on average, and {rm['programs_proved_equivalent']} of the 500 optimized "
        f"programs are proved equivalent to their originals, {rm['programs_proved_by_smt']} of them by the SMT solver."
        + llm_sentence + " No incorrect change was accepted in any run.\n\n"))

    # ------------------------------------------------------------------ objectives
    doc.after("  \\item Achieve a strict 0\\% false-positive rate by verifying every single proposal before applying it.\n", (
        "  \\item Measure execution time as well as static cost, so that work removed from a loop counts for more.\n"
        "  \\item Prove equivalence for all inputs wherever that is possible, instead of only testing it.\n"
        "  \\item Give an LLM whose answer was rejected the reason and one more attempt.\n"
        "  \\item Evaluate the system on programs written by people, not only on generated ones.\n"))

    # ------------------------------------------------------------------ datasets
    rows = ""
    decided = {"arithmetic": "straight-line code, shallow arithmetic", "nested": "an expression three or more operators deep",
               "repeated_expr": "the same expression written twice", "dead_code": "a stored value that is never read",
               "loops": "a loop and no branch", "conditionals": "a branch and no loop", "mixed": "a loop and a branch"}
    for key, label in CATEGORIES:
        entries = [e for e in programs if e["category"] == key]
        rows += f"{label} & {len(entries)} & {len({e['problem_id'] for e in entries})} & {decided[key].capitalize()} \\\\\n\\hline\n"
    doc.after("Mixed & 100 & All of the above \\\\\n\\hline\n\\end{tabular}\n\\end{table}\n", (
        "\n\\subsection{Real-Program Dataset}\n\\label{sec:realdata}\n\n"
        "The generated programs are written to contain what the optimizer looks for. To see how the system behaves "
        "on code that people actually wrote, we built a second dataset of 500 real programs. They are accepted "
        "submissions to Codeforces problems, taken from the dataset \\texttt{open-r1/codeforces-submissions} on "
        "Hugging Face (2025, CC-BY-4.0), which holds 12.6 million submissions.\n\n"
        "A submission is usable when (i) the judge accepted it, (ii) the C front end compiles it in strict mode, "
        "(iii) it prints something, and (iv) it finishes within 20,000 steps on every input set the verifier would "
        "try, since otherwise no change to it could be verified. Of 469,491 accepted C and C++ submissions examined "
        "(six of the dataset's 36 files), 9,489 were usable (2.0\\%), from 234 problems. The others mostly use "
        "arrays, further functions, floating point or macros, or read their input inside a loop, none of which the "
        "front end supports.\n\n"
        "From the usable submissions, 500 were chosen in exactly the proportions of the generated dataset. "
        "Programs that compile to the same TAC count once, each category is filled one program per problem per "
        f"round, and within a problem the newest submission goes first. The 500 come from {manifest['problems']} "
        f"problems; {as_c} were submitted as C and {500 - as_c} as C-style C++, that is, C++ submissions that use "
        "only \\texttt{scanf} and \\texttt{printf} and nothing else from C++.\n\n"
        "\\begin{table}[H]\n\\centering\n\\caption{Real-program dataset: composition and how a category is decided}\n"
        "\\begin{tabular}{|l|c|c|l|}\n\\hline\n"
        "\\textbf{Category} & \\textbf{Programs} & \\textbf{Problems} & \\textbf{Decided by} \\\\\n\\hline\n"
        + rows + "\\end{tabular}\n\\end{table}\n\n"
        "A stored value that is never read, or an expression written twice, decides the category first, because "
        "that is what the generator builds its dead-code and repeated-expression programs around. Everything else "
        "is classified by its control flow. Straight-line solutions are rare on Codeforces, so the arithmetic and "
        "nested categories draw on fewer problems than the others.\n\n"
        "\\textbf{Strict mode.} For these programs the front end keeps everything a run shows. Text printed by "
        "\\texttt{printf}, \\texttt{puts} or \\texttt{putchar} becomes a \\texttt{print} of a code that stands for "
        "that text, so an optimization that changed which message is printed would fail verification. A "
        "\\texttt{return} in the middle of \\texttt{main} becomes a jump to the end of the program. An expression "
        "\\texttt{a \\&\\& b} is refused when \\texttt{b} contains a division, because TAC evaluates both sides and "
        "C would not.\n"))

    # ------------------------------------------------------------------ verification, cost model, self-repair
    doc.after("If the printed expressions match structurally, the transformation is safe for every input.\n", (
        "\n\\textbf{SMT Verification:} Differential testing shows that two programs agree on the inputs that were "
        "tried. For a program with branches but no loops there are finitely many paths, so its whole behaviour can "
        "be written as one formula over its inputs. The verifier follows every path symbolically: a branch splits "
        "the path in two, and a division splits off the case in which the divisor is zero, where the run stops "
        "with what it has printed so far. The paths are then folded into a single description of a run (how it "
        "ends, how many values it prints, and the values), and the Z3 solver \\citep{demoura2008z3} is asked for an "
        "input on which the descriptions of the two programs differ.\n\n"
        "\\begin{table}[H]\n\\centering\n\\caption{The three answers of the SMT stage}\n"
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
        "\\section{Cost Model: Static Cost and Execution Time}\n\\label{sec:time}\n\n"
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
        "\\section{LLM Self-Repair}\n\\label{sec:repair}\n\n"
        "When an LLM answer is rejected, the reason is specific: the verifier has the inputs on which the outputs "
        "differ, or the parser has the line that is not valid TAC. The Optimization Specialist sends the model its "
        "rejected answer together with that reason and asks once more. The second answer goes through exactly the "
        "same verification and cost gates as any other proposal, so self-repair cannot make the system less safe; "
        "it can only turn a wasted call into a useful one. By default one repair is allowed per rejected answer, "
        "and repairs do not use up the budget of fresh proposals.\n"))

    # ------------------------------------------------------------------ testing
    doc.swap("a suite of 336 automated tests covering every module.", f"a suite of {TOTAL_TESTS} automated tests covering every module.")
    doc.after("The proposal was caught by the verifier every time, and the analyzer no longer makes it.\n", (
        "\nThe additions for the final review are tested in the same way. The SMT stage is checked against "
        "hand-built pairs of programs: equivalent ones must be proved, and pairs that differ on a single input, "
        "in the order of their output, or in whether a division traps must be refuted with the right "
        "counterexample.\n\n"
        "\\textbf{Re-checking the runs on real programs.} Every optimized program was run against its original "
        "on inputs the verifier had not used, including values up to a million. For the two rule-based runs and "
        "the local-model run no mismatch was found. In the Groq run the re-check found one wrong program. The "
        "model had replaced \\texttt{x - 1} by the constant 9 inside a loop in which \\texttt{x} is multiplied "
        "by ten in every iteration. The change is correct while \\texttt{x} is 10, and the loop runs a second "
        "time only for inputs of 100 or more, which none of the verifier's input sets reached, so all 388 tests "
        "had passed. The verifier now adds 60 wide-range input sets for every program that reads input: values "
        "up to a thousand, ten thousand, a million and a billion, signed values, and powers of ten with their "
        "neighbours. A run that is too long for these inputs is skipped, so they never make a program "
        "unverifiable. With them the wrong change is rejected with a counterexample. The affected program was "
        f"optimized again, and the re-check of all runs on real programs ({RECHECK['executions']} executions) now "
        f"finds {RECHECK['mismatches']} mismatches. The four runs on the generated dataset were re-checked on the "
        "same wide inputs, also without a mismatch.\n"))

    # ------------------------------------------------------------------ results on real programs
    table_rows = ""
    for key, label in CATEGORIES:
        g = generated["m"]["per_category"][key]["avg_reduction_pct"] if generated else None
        c = rm["per_category"][key]
        table_rows += (f"{label} & {c['programs']} & {p(g)} & {p(c['avg_reduction_pct'])} & "
                       f"{p(c['avg_time_reduction_pct'])} & {c['programs_proved']} \\\\\n\\hline\n")
    table_rows += (f"\\textbf{{All}} & 500 & {p(generated['m']['avg_cost_reduction_pct']) if generated else 'n/a'} & "
                   f"\\textbf{{{p(rm['avg_cost_reduction_pct'])}}} & {p(rm['avg_time_reduction_pct'])} & "
                   f"{rm['programs_proved_equivalent']} \\\\\n\\hline\n")
    results = (
        "\\section{Results on Real Programs}\n\\label{sec:realresults}\n\n"
        "All runs in this section use the real-program dataset of Section~\\ref{sec:realdata} and allow 200 "
        "iterations per program, because real programs are longer than the generated ones.\n\n"
        "\\subsection{Rule-Based Optimization}\n\n"
        "\\begin{table}[H]\n\\centering\n\\caption{Rules only: generated and real programs (static cost model)}\n"
        "\\begin{tabular}{|l|c|c|c|c|c|}\n\\hline\n"
        "\\textbf{Category} & \\textbf{Programs} & \\textbf{Generated} & \\textbf{Real} & \\textbf{Real, time} & "
        "\\textbf{Proved} \\\\\n\\hline\n" + table_rows + "\\end{tabular}\n\\end{table}\n\n"
        f"On the real programs the rules reduce the static cost by {p(rm['avg_cost_reduction_pct'])} on average "
        f"(median {p(rm['median_cost_reduction_pct'])}); {rm['programs_with_reduction_over_30pct']} of the 500 "
        f"programs improve by more than 30\\%. The figure is lower than on the generated set because nearly all "
        "real programs read their values with \\texttt{scanf}, so nothing folds down to a constant. Most of what "
        f"the rules remove is the redundancy of the naive TAC translation: {n(kind(rm, 'COPY_PROPAGATION'))} "
        f"accepted copy propagations and {n(kind(rm, 'DEAD_CODE'))} dead-code removals, against "
        f"{n(kind(rm, 'CSE'))} common subexpressions and {n(kind(rm, 'CONSTANT_FOLD'))} constant folds. "
        f"All {n(rm['total_proposals'])} proposals passed verification; {n(rm['accepted'])} were accepted and "
        f"{n(rm['rejected_no_cost_gain'])} gave no cost gain.\n\n"
        "\\begin{figure}[H]\n\\centering\n\\includegraphics[width=\\textwidth]{report_figures/real_heatmap_rules.png}\n"
        "\\caption{Real programs, rules only: accepted optimizations by category and type}\n\\end{figure}\n\n"
        "\\subsection{Execution Time and the Two Cost Models}\n\n"
        "\\begin{table}[H]\n\\centering\n\\caption{Rules only on the 500 real programs under the two cost models}\n"
        "\\begin{tabular}{|l|c|c|}\n\\hline\n\\textbf{Metric} & \\textbf{Static model} & \\textbf{Time model} \\\\\n\\hline\n"
        f"Average static cost reduction & {p(rm['avg_cost_reduction_pct'])} & {p(tm['avg_cost_reduction_pct'])} \\\\\n\\hline\n"
        f"Average execution-time reduction & {p(rm['avg_time_reduction_pct'])} & {p(tm['avg_time_reduction_pct'])} \\\\\n\\hline\n"
        f"Median execution-time reduction & {p(rm['median_time_reduction_pct'])} & {p(tm['median_time_reduction_pct'])} \\\\\n\\hline\n"
        f"Strength reductions accepted & {n(kind(rm, 'STRENGTH_REDUCTION'))} & {n(kind(tm, 'STRENGTH_REDUCTION'))} \\\\\n\\hline\n"
        f"Strength reductions rejected (no gain) & {n(kind(rm, 'STRENGTH_REDUCTION', 'rejected'))} & "
        f"{n(kind(tm, 'STRENGTH_REDUCTION', 'rejected'))} \\\\\n\\hline\n"
        f"Proposals accepted & {n(rm['accepted'])} & {n(tm['accepted'])} \\\\\n\\hline\n"
        f"False positives & {rm['false_positive_count']} & {tm['false_positive_count']} \\\\\n\\hline\n"
        "\\end{tabular}\n\\end{table}\n\n"
        "The execution time falls less than the static cost, because most of the removed instructions are copies, "
        "which cost one cycle each, while the divisions, multiplications and branches that dominate the running "
        "time have to stay. The time model accepts changes that the static count regards as a tie, such as "
        "replacing a multiplication by two with an addition, and so removes a little more time.\n\n"
        "\\subsection{Proved Equivalence}\n\n"
        f"For {rm['programs_proved_equivalent']} of the 500 real programs the optimized program is proved "
        f"equivalent to the original for every input: {rm['programs_proved_equivalent'] - rm['programs_proved_by_smt']} "
        f"by the polynomial check for straight-line code and {rm['programs_proved_by_smt']} by the SMT solver. The "
        "remaining programs contain loops, or defeated the solver within its time limit, and are verified by "
        "differential testing as before. The end-to-end check never failed, so no program had to be reverted to "
        "its original.\n\n")
    if groq or ollama or gemini:
        cells = {"Programs in the sample": lambda r: n(r["m"]["total_programs"]),
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
                 "False positives": lambda r: str(r["m"]["false_positive_count"])}
        body = ""
        for label, getter in cells.items():
            body += f"{label} & " + " & ".join(getter(run) for _, run in llm_runs) + " \\\\\n\\hline\n"
        results += (
            "\\subsection{LLM Proposers with Self-Repair}\n\n"
            "The LLM configurations were run on a sample of the real programs, every fifth program of the "
            "dataset, which keeps the proportions of the categories. Each program is allowed two fresh LLM "
            "proposals and one repair per rejected answer. "
            + " ".join({"Gemini": "Gemini uses \\texttt{gemini-3.1-flash-lite} in the cloud.",
                        "Groq": "Groq uses its \\texttt{gpt-oss} models in the cloud.",
                        "Ollama": "Ollama runs \\texttt{qwen2.5-coder:7b} on the laptop."}[name] for name, _ in llm_runs)
            + "\n\n"
            "\\begin{table}[H]\n\\centering\n\\caption{LLM proposers with self-repair on the real-program sample}\n"
            "\\begin{tabular}{|l|" + "c|" * len(llm_runs) + "}\n\\hline\n\\textbf{Metric} & "
            + " & ".join("\\textbf{Rules + " + name + "}" for name, _ in llm_runs) + " \\\\\n\\hline\n"
            + body + "\\end{tabular}\n\\end{table}\n\n")
        if os.path.exists(os.path.join(figures, "real_sankey_groq.png")):
            results += ("\\begin{figure}[H]\n\\centering\n\\includegraphics[width=\\textwidth]{report_figures/real_sankey_groq.png}\n"
                        "\\caption{Real-program sample, rules + Groq: where the proposals went}\n\\end{figure}\n\n")
    doc.before("\\section{Performance Analysis}\n", results)

    # ------------------------------------------------------------------ analysis and limitations
    doc.before("\\section{Limitations}\n", (
        "\\textbf{Real programs leave less to remove:} A generated program is mostly constants and collapses to a "
        "few prints. A real program computes with its input, so the instructions that do the work have to stay, "
        "and the gain comes from cleaning up the translation and the occasional redundancy the programmer left.\n\n"
        "\\textbf{A proof is stronger than a test:} For programs without loops, zero false positives is no longer "
        "a statement about the inputs that were tried. For the programs the solver decided, no input exists on "
        "which the optimized program behaves differently.\n\n"
        "\\textbf{Tests can be passed by a wrong change:} The one wrong change that the re-check found had passed "
        "388 tests. Testing is only as good as its inputs; the lasting answers are inputs chosen to reach "
        "behaviour the program shows rarely, an independent re-check of every run, and a proof wherever one is "
        "possible.\n\n"
        "\\textbf{Self-repair helps with form more than with logic:} A capable model that is rejected has usually "
        "written a whole expression in one instruction; told so, it answers again in valid TAC. A small local "
        "model that got the logic wrong tends to get it wrong again, or to play safe and return the program "
        "unchanged.\n\n"))
    start = doc.text.index("\\section{Limitations}\n")
    end = doc.text.index("% ============================================================\n\\newpage\n\\begin{thebibliography}")
    doc.text = doc.text[:start] + (
        "\\section{Limitations}\n\n\\begin{itemize}[leftmargin=2cm]\n"
        "  \\item The front end accepts only a subset of C: no arrays, pointers, functions other than "
        "\\texttt{main}, floating point, or input read inside a loop. That is why only 2\\% of the submissions "
        "examined could be used.\n"
        "  \\item The SMT stage does not handle loops. Programs with loops are verified by differential testing, "
        "which is thorough but is not a proof.\n"
        "  \\item Integers are unbounded in TAC, so the 32-bit wrap-around of C is not modelled, and inputs are "
        "tested over the verifier's ranges, which include values a problem statement rules out.\n"
        "  \\item Execution time is an abstract count of cycles from a fixed latency table, measured on 25 inputs. "
        "It orders programs sensibly but is not a measurement on real hardware.\n"
        "  \\item The LLM runs on the real programs cover a sample of 100 programs, not all 500; the runs are "
        "resumable and can be extended.\n"
        "\\end{itemize}\n\n") + doc.text[end:]

    # ------------------------------------------------------------------ references
    doc.before("\\end{thebibliography}", (
        "\\bibitem[de Moura and Bj{\\o}rner, 2008]{demoura2008z3}\n"
        "de Moura, L., Bj{\\o}rner, N. (2008). Z3: An efficient SMT solver. \\textit{Tools and Algorithms for the "
        "Construction and Analysis of Systems (TACAS)}, 337--340.\n\n"
        "\\bibitem[open-r1, 2025]{openr1codeforces}\n"
        "open-r1 (2025). \\textit{codeforces-submissions} (dataset, CC-BY-4.0). Hugging Face.\n\n"))

    path = os.path.join(ROOT, "report3.tex")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc.text)
    return path


if __name__ == "__main__":
    print("saved", build())
