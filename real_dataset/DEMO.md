# Running the demo

Everything runs from the project folder in a terminal (PowerShell or Command Prompt).

## Before the demo (once)

1. Install the packages: `py -m pip install -r requirements.txt`
   (this includes `z3-solver`, which the proofs need).
2. For the cloud LLMs, put the API keys in the project folder: the Groq key in a file named
   `.groq_key`, the Gemini key in `.gemini_key` (one line each, nothing else in the file).
3. For the offline model, start the Ollama app and check the model is there: `ollama list`
   should show `qwen2.5-coder:7b`. If it does not: `ollama pull qwen2.5-coder:7b`.
4. Check that everything works: `py -m pytest -q` should end with `407 passed`.

## The demo itself

Start the menu:

```
demo.bat
```

(or `py demo.py`). It asks three things:

1. **Which program.** Type a number for a sample, `r` for a real Codeforces program picked at
   random, `p` to paste your own C program, or the path of a `.c` file.
2. **Who proposes the optimizations.** `1` rules only, `2` rules + Groq, `3` rules + Gemini,
   `4` rules + Ollama (offline), `5` all of them side by side. The menu shows which LLMs are ready.
3. **Which cost model.** Press Enter for the static count, or `t` for measured execution time.

The run then goes through six stages; press Enter to move from one to the next:

| Stage | What is on screen |
|---|---|
| 1 | The C program |
| 2 | Its Three-Address Code, the weighted cost and the execution time |
| 3 | The agent loop: every suggestion, whether it was verified, and ACCEPTED or REJECTED |
| 4 | The suggestions counted: per source and per optimization type, with the wrong ones listed apart |
| 5 | Original and optimized TAC side by side |
| 6 | The same input run on both programs, how equivalence was established, and a summary |

## A good order to show

| Step | Command | What it shows |
|---|---|---|
| 1 | `py demo.py demo_programs/1_constants.c` | The rules alone: constant folding, copy propagation, dead code |
| 2 | `py demo.py demo_programs/4_branch.c` | A program with branches: stage 6 says *proved for all inputs by the Z3 SMT solver* |
| 3 | `py demo.py demo_programs/3_loop.c --use-llm --llm-provider groq` | The rules stop at the loop; the LLM replaces it, and the verifier checks the answer |
| 4 | `py demo.py demo_programs/3_loop.c --compare` | The same program under the rules, Groq, Gemini and Ollama in one table: cost, time, correct and wrong LLM suggestions |
| 5 | `py demo.py demo_programs/7_time_cost_model.c` and then the same with `--cost-model time` | Static model rejects `n * 2` to `n + n` (no gain); the time model accepts it |
| 6 | `ollama_demo.bat` | The offline model, no internet. When it is wrong, the verifier blocks it and self-repair gives it a second try |
| 7 | `py demo.py`, then `r` | A real Codeforces submission, in strict C mode |

Useful options: `--fast` (no pauses), `--step` (pause after every decision), `--verbose` (show
every decision), `--inputs n=10,k=3` (values for `scanf` variables), `--optimizer llm` (ask the
LLM before the rules, for more LLM steps to watch).

## The full experiments

| What | Command |
|---|---|
| Rules on the 500 generated programs | `py main.py --run-all --visualize --output-dir output_rule_only` |
| Rules on the 500 real programs | `py main.py --run-all --dataset real --max-iterations 200 --visualize --output-dir output_real_rule_only` |
| The same with an LLM | add `--use-llm --llm-provider groq --resume` and another `--output-dir` |

The results of all runs are already in the `output*` folders, so nothing has to be re-run for the demo.

## If something goes wrong

| Problem | Fix |
|---|---|
| The menu shows "no key" for Groq or Gemini | The key file is missing or empty; see step 2 above |
| "Ollama is not running" | Start the Ollama app, wait a few seconds, try again |
| Stage 6 says "tested" for `4_branch.c` instead of "proved" | `py -m pip install z3-solver` |
| A cloud LLM answers "rate limit" | Wait a minute, or use the other provider |
| The LLM is "not needed" | The rules already removed everything; use sample 3, 5 or 6 |
