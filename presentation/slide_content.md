# Slide Content — Corrected

All numbers below were checked against `output/metrics/`. Images are in
`output/plots/` (charts) and `presentation/` (the two diagrams).

---

## Slide 1 — Title
**Title:** Automated LLM/Agent-Guided Compiler Code Optimization
**Subtitle:** A Multi-Agent System for Autonomous TAC Analysis, Transformation & Verification
**Bottom:** Compiler Design Project · October 2026 · [Your names]

---

## Slide 2 — Introduction
- Modern compilers apply fixed optimization passes. They don't *reason* about what to try next.
- What if an agent could analyze code, propose optimizations, verify them, and keep improving the program on its own?
- We built a multi-agent system that does this on Three-Address Code (TAC).
- Every proposal must pass a correctness check **and** lower the program's cost before it is accepted.
- Tested on **500 programs** across 7 categories: **0 incorrect changes accepted**.

**Speaker notes:** Stress the safety result: across 10,978 proposals, no incorrect change was accepted. The system runs end-to-end with no human in the loop.

---

## Slide 3 — Objectives
- Build a multi-component agent architecture with separate responsibilities
- Implement the Orchestrator loop: Analyze → Propose → Verify → Evaluate → Accept/Reject
- Detect 6 optimization types: constant folding, algebraic simplification, dead code elimination, CSE, strength reduction, copy propagation
- Verify every change twice: differential testing (25+ input sets) and symbolic equivalence
- Accept a change only if it is verified correct AND lowers the weighted cost
- Add an LLM proposer (Google Gemini) alongside the rule-based optimizer
- Run on 500 programs, report the 6 metrics, generate 7 charts

---

## Slide 4 — Literature Review (table)
| Area | Key Works | Relevance |
|---|---|---|
| Classical compiler optimization | Aho, Lam, Sethi & Ullman — *Compilers: Principles, Techniques, and Tools* (2006) | Foundation for constant folding, DCE, CSE, copy propagation, dataflow analysis |
| Superoptimization | Massalin (1987); Schkufza, Sharma & Aiken — *STOKE* (2013); Phothilimthana et al. (2016) | Search for optimal instruction sequences; uses testing to check candidates |
| Translation validation | Pnueli, Siegel & Singerman (1998); Necula (2000) | Checking that compiler output matches the source; the idea behind our verifier |
| LLMs for code | Chen et al. — *Codex* (2021); Rozière et al. — *Code Llama* (2023) | Models that generate and transform code; we use Gemini as a proposer |
| LLM-assisted compilation | Cummins et al. — *CompilerGym* (2022); Cummins et al. — *LLM Compiler* (2024) | RL and LLM agents choosing compiler flags and pass orderings |
| Multi-agent systems | Wu et al. — *AutoGen* (2023) | Agent orchestration; inspired our Orchestrator + specialist design |

**Speaker notes:** We combine classical compiler techniques with an LLM. Unlike LLM Compiler, which picks pass orderings, our agent proposes actual code transformations and checks each one before accepting it.

---

## Slide 5 — Research Gaps
- **Gap 1:** Classical compilers run a fixed sequence of passes. They don't decide *which* optimization to try or check whether it helped.
- **Gap 2:** Superoptimizers (e.g. STOKE) are thorough but too slow for whole programs; they work on small code blocks.
- **Gap 3:** LLM code tools (Codex, Code Llama) produce code with **no correctness guarantee**; they can introduce bugs silently.
- **Gap 4:** LLM-for-compiler work (CompilerGym, LLM Compiler) focuses on **pass ordering and flag selection**, not on proposing new code-level transformations.
- **Gap 5:** Few systems put every LLM suggestion through a **verification gate** before it is accepted.

**Our contribution:** An agent that decides what to optimize, proposes transformations (rule-based + LLM), and accepts a change only after it is verified and shown to lower cost. In our experiments it accepted **0 incorrect changes out of 10,978 proposals**.

---

## Slide 6 — Proposed Methodology
**The agent loop (per program):**
1. **Parse:** source → AST → Three-Address Code (TAC)
2. **Analyze:** find optimization opportunities, ranked by priority
3. **Propose:** apply the top-ranked rule; if rules are rejected or run out, ask the LLM
4. **Verify:** differential testing (25+ input sets) + symbolic equivalence check
5. **Evaluate:** compute the weighted cost; accept only if it strictly decreases
6. **Repeat** until nothing is left or 50 iterations are reached
7. **Final check:** verify the optimized TAC against the original once more

**Key principle:** The LLM is *only a proposer*. Its suggestions go through the same verification and cost gates as the rules, so a wrong suggestion is caught and rejected.

---

## Slide 7 — Dataset: 500 Programs, 7 Categories (table)
| Category | Count | Example | Main optimization targets |
|---|---|---|---|
| Arithmetic | 60 | `int k = 1 + 14;` | Constant folding |
| Nested expressions | 60 | `((a+b)*(c-d))` | Constant folding, copy propagation |
| Repeated expressions | 60 | `a*b` computed twice | Common subexpression elimination |
| Dead code | 60 | `int v = e*5;` never used | Dead code elimination |
| Loops | 80 | `for` / `while` with invariant work | Folding inside loops, DCE |
| Conditionals | 80 | `if` / `else` with identities like `x*1` | Algebraic simplification, folding |
| Mixed | 100 | several of the above combined | All of the above |
| **Total** | **500** | | |

- Generated by `dataset/generator.py` with a fixed random seed (reproducible)
- Some programs read **input variables**, which are tested with random and boundary values
- Covers straight-line, branching, looping and nested code

---

## Slide 8 — System Architecture
**Image:** `presentation/slide8_architecture.png`
- **Frontend:** Lexer → Parser → AST → TAC Generator
- **Agent loop:** Analyzer → Proposer → Verifier → Cost Evaluator → Decision
- **Outputs:** per-program decision logs (.log + .json), metrics (CSV + JSON), 7 charts

---

## Slide 9 — Agent Workflow
**Image:** `presentation/slide9_workflow.png` (place it left; key points on the right)
- Max 50 iterations per program
- On accept: clear the "already tried" list (new opportunities may appear)
- On reject: remember it and try the next opportunity
- Gemini is asked when a rule is rejected or the rules run out
- At the end: re-verify the optimized TAC against the original

---

## Slide 10 — Tools & Technologies (table)
| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.10+ | `match` statements, dataclasses, type hints |
| LLM provider | Google Gemini (`gemini-3.1-flash-lite`) | Free-tier LLM proposer via the `google-genai` SDK |
| Visualization | Matplotlib, Seaborn, Plotly | Bar, line, scatter, heatmap, pie and Sankey charts |
| Testing | pytest (190 tests) | Unit and integration tests for every component |
| Numerical | NumPy | Trend lines, statistics |
| Export | Kaleido | Saving Plotly charts as PNG |

**Project structure (code-style text box):**
```
src/frontend/       Lexer, Parser, AST nodes, TAC generator
src/tac/            TAC instructions, program, interpreter, dataflow analysis
src/agents/         Orchestrator, Analyzer, Rule Optimizer, LLM Optimizer,
                    Verifier, Cost Evaluator, Decision Logger
src/visualization/  Charts (7 types), report and metrics
```

---

## Slide 11 — Implementation: The Five Agents
1. **Code Analyzer:** scans TAC using dataflow analysis (control-flow graph, liveness, available copies). Ranks 6 types: Constant Fold (100) → Algebraic (90) → Dead Code (80) → CSE (70) → Strength Reduction (60) → Copy Propagation (50).
2. **Rule-Based Optimizer:** copies the program and applies exactly one transformation. Copy propagation also removes the copy once it is unused.
3. **LLM Optimizer (Gemini):** sends the TAC with a structured prompt and reads back `<tac>` and `<reasoning>` tags. Calls are spaced 6.5 s apart (free tier); it retries on rate-limit/overload errors and switches off if the daily quota runs out.
4. **Verifier:** differential testing (20 random + 5 edge-case + boundary input sets) and symbolic checking for straight-line code.
5. **Cost Evaluator:** `cost = 1.0·instructions + 2.0·arithmetic + 0.5·temps + 1.5·copies + 1.0·branches`

---

## Slide 12 — Verification Deep Dive
**How we keep incorrect changes out:**
- **Gate 1, differential testing:** run original and candidate on 25+ input sets; compare printed output **and** failure behaviour (division by zero, timeout, undefined variable). If both time out, the result is inconclusive and the change is rejected.
- **Gate 2, symbolic check (straight-line code):** values become canonical polynomials, so `x*2`, `x+x` and `x<<1` are recognised as equal, and so are `a+b` and `b+a`. Skipped for loops/branches, where Gate 1 applies.
- **Gate 3, cost:** a correct change is still rejected unless the cost strictly drops.
- **Final re-check:** the finished program is verified against the untouched original.

**Strength of the guarantee:** for programs with no inputs, and for straight-line code, equivalence is proven. For branching code with inputs it is tested thoroughly, including boundary values.

**Result:** 10,978 proposals → **0 incorrect changes accepted**.

---

## Slide 13 — Results: Key Metrics (table)
| Metric | Rule-based only | Rule-based + Gemini |
|---|---|---|
| **Average cost reduction** | 82.49% | **91.50%** |
| Programs with >30% reduction | 500 / 500 | 500 / 500 |
| Verification pass rate | 100.00% | 99.76% |
| Acceptance rate (of verified) | 98.96% | 98.87% |
| Steps to convergence (mean) | 22.2 | 22.7 |
| LLM validity rate | n/a | **92.35%** |
| False positives | **0** | **0** |
| Total proposals | 10,628 | 10,978 |
| Accepted | 10,517 | 10,828 |

**Key takeaway:** Gemini raised the average cost reduction from 82.5% to 91.5% (+9 percentage points), and the verifier blocked all 26 incorrect Gemini suggestions.

---

## Slide 14 — Results: Per-Category Cost Reduction (table)
| Category | Programs | Rule-only | Rule + Gemini | Change |
|---|---|---|---|---|
| Arithmetic | 60 | 96.0% | 96.0% | — |
| Nested | 60 | 98.1% | 98.2% | +0.1 |
| Repeated expr | 60 | 80.7% | 81.7% | +1.0 |
| Dead code | 60 | 97.4% | 97.4% | — |
| **Loops** | 80 | 65.1% | **93.3%** | **+28.2** |
| **Conditionals** | 80 | 73.9% | **84.1%** | **+10.2** |
| **Mixed** | 100 | 77.9% | **91.6%** | **+13.7** |

**Key takeaway:** Gemini helped most on loops and conditionals, where the six rules can't remove branches. It worked out whole constant loops (e.g. "adds −4 twelve times" → `print -48`). 196 programs improved; none got worse.

---

## Slide 15 — Results: Proposal Flow
**Image:** `output/plots/1_sankey_proposal_flow.png`
**Caption:** All 10,978 proposals: 10,952 passed verification and 26 were invalid; 10,828 were accepted and 124 rejected for no cost gain. All 26 invalid proposals came from the LLM and were blocked by the verifier.

---

## Slide 16 — Results: Optimization Types
**Left image:** `output/plots/2_bar_outcomes_by_type.png`
**Right image:** `output/plots/4_pie_accepted_types.png`
**Caption (left):** Accepted / rejected / invalid counts per type. Copy propagation dominates (6,465 accepted). Strength reduction has the most rejections (62), because `x*2 → x+x` doesn't lower cost.
**Caption (right):** Share of accepted optimizations: Copy Propagation 59.7%, Dead Code 17.5%, Constant Fold 16.7%, LLM 2.4%, Algebraic 1.6%, CSE 1.4%, Strength Reduction 0.8%.

---

## Slide 17 — Results: Cost Over Iterations & Steps vs. Improvement
**Left image:** `output/plots/3_line_cost_over_iterations.png`
**Right image:** `output/plots/5_scatter_steps_vs_improvement.png`
**Caption (left):** Cost trajectory for 5 representative programs. Cost falls steadily with each accepted optimization until no opportunities remain.
**Caption (right):** Agent steps vs. cost improvement, one panel per category. Overall, programs that take more steps tend to reach higher reductions (trend +0.41 percentage points per step).

---

## Slide 18 — Results: Heatmap & Rule vs. LLM
**Left image:** `output/plots/6_heatmap_category_vs_type.png`
**Right image:** `output/plots/7_comparison_rule_vs_llm.png`
**Caption (left):** Accepted optimizations by category and type. Copy propagation is the most applied in every category; nested programs have the most constant folds (527); mixed programs have the most dead-code removals (463).
**Caption (right):** Rule-only vs. rule + Gemini per category. The LLM closes most of the gap on loops (65% → 93%) and conditionals (74% → 84%).

---

## Slide 19 — Example Decision Log (terminal-style box)
```
=== Program: repeated_expr_009.src ===
--- Iteration 1 ---
  [ANALYZE] Found 7 opportunities: CSE (priority=70), COPY_PROPAGATIONx6
  [PROPOSE] Applying CSE at instruction 2: t1 = in_b + in_a → t1 = t0
  [VERIFY]  PASS (differential: 25/25 matched, symbolic: equivalent)
  [COST]    Before: 19.0, After: 18.5 (reduction: 2.6%)
  [ACCEPT]  ✓ Change accepted
--- Iteration 5 ---
  [PROPOSE] Applying COPY_PROPAGATION: t2 = t0 + t0; s = t2 → s = t0 + t0
  [VERIFY]  PASS (25/25 matched, symbolic: equivalent)
  [COST]    Before: 10.5, After: 7.5 (reduction: 28.6%)
  [ACCEPT]  ✓ Change accepted
--- Iteration 6 ---
  [ANALYZE] No more opportunities found.
=== RESULT ===  Original cost 19.0 → Final cost 7.5 (60.5% reduction)   Output match: PASS ✓

Original TAC (7 instructions)     Optimized TAC (3 instructions)
  t0 = in_b + in_a                  t0 = in_b + in_a
  a = t0                            s = t0 + t0
  t1 = in_b + in_a                  print s
  h = t1
  t2 = a + h
  s = t2
  print s
```

---

## Slide 20 — Project Status
**Work completed**
- Full frontend: Lexer → Parser → AST → TAC Generator
- All 5 agent components as separate classes
- Orchestrator loop with full decision logging (JSON + readable text)
- Dual verification (differential testing + symbolic equivalence)
- Rule-based optimizer with 6 optimization types
- Google Gemini integration (free tier, `gemini-3.1-flash-lite`)
- 500-program dataset across 7 categories
- 190 tests, all passing
- 7 charts and comparison metrics
- Two complete runs: rule-only (82.5%) and rule + Gemini (91.5%)

**Next steps (planned)**
- **Prompt tuning for Gemini:** cut the 7.65% invalid-proposal rate (26 of 340) with few-shot examples and stricter output format
- **Constant-loop evaluator rule:** let the rule-based optimizer collapse constant loops itself (e.g. a loop adding 3 ten times → `acc = 30`), reducing LLM dependence
- **Offline mode:** a local model via Ollama, so the system runs without internet or API keys
- **Deeper analysis:** convergence histograms, statistical significance of the LLM improvement, a taxonomy of failure cases

---

## Slide 21 — Conclusion
- We built an autonomous multi-agent compiler optimizer that analyzes, proposes, verifies and evaluates transformations with no human in the loop.
- **82.5%** average cost reduction with rules alone, **91.5%** with Gemini, across all 500 programs.
- **0 incorrect changes accepted** across 10,978 proposals, confirmed by an independent re-check of all 500 programs (3,776 runs).
- The LLM is a strong complement: **+28 points on loops**, **+10 on conditionals**, while the verifier caught all 26 of its incorrect suggestions.
- Modular design: new optimization types, verification methods or LLM providers plug in as separate classes.
- **Key insight:** LLMs propose useful, creative transformations, but they must be verified. 7.65% of Gemini's suggestions were wrong.

---

## Slide 22 — References
1. Aho, A.V., Lam, M.S., Sethi, R. & Ullman, J.D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Pearson.
2. Massalin, H. (1987). Superoptimizer: A Look at the Smallest Program. *ASPLOS*.
3. Schkufza, E., Sharma, R. & Aiken, A. (2013). Stochastic Superoptimization. *ASPLOS*.
4. Phothilimthana, P.M. et al. (2016). Scaling up Superoptimization. *ASPLOS*.
5. Pnueli, A., Siegel, M. & Singerman, E. (1998). Translation Validation. *TACAS*.
6. Necula, G.C. (2000). Translation Validation for an Optimizing Compiler. *PLDI*.
7. Chen, M. et al. (2021). Evaluating Large Language Models Trained on Code. *arXiv:2107.03374*.
8. Rozière, B. et al. (2023). Code Llama: Open Foundation Models for Code. *arXiv:2308.12950*.
9. Cummins, C. et al. (2022). CompilerGym: Robust, Performant Compiler Optimization Environments for AI Research. *CGO*.
10. Cummins, C. et al. (2024). Meta Large Language Model Compiler: Foundation Models of Compiler Optimization. *arXiv:2407.02524*.
11. Wu, Q. et al. (2023). AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation. *arXiv:2308.08155*.
12. Gemini Team, Google (2023). Gemini: A Family of Highly Capable Multimodal Models. *arXiv:2312.11805*.
