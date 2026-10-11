"""Draws the architecture (slide 8) and agent-workflow (slide 9) diagrams."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

OUT = os.path.dirname(os.path.abspath(__file__))
BG, INK, INK2, LINE = "#fcfcfb", "#1d2433", "#52514e", "#8a8f99"
BLUE, BLUE_L = "#2a78d6", "#e3eefb"
GREEN, GREEN_L = "#0b8a0b", "#e2f3e2"
RED, RED_L = "#c23434", "#fbe5e5"
GREY_L = "#efeee9"
plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans", "sans-serif"]


def box(ax, x, y, w, h, text, fc=BLUE_L, ec=BLUE, size=11, weight="normal", color=INK):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.6))
    ax.text(x, y, text, ha="center", va="center", fontsize=size, color=color, weight=weight, linespacing=1.3)


def arrow(ax, x1, y1, x2, y2, color=LINE, text=None, tx=0, ty=0, style="-|>", rad=0.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=1.6, mutation_scale=16,
                                connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))
    if text:
        ax.text((x1 + x2) / 2 + tx, (y1 + y2) / 2 + ty, text, ha="center", va="center", fontsize=9.5,
                color=color, weight="bold", bbox=dict(fc=BG, ec="none", pad=1.5))


def diamond(ax, x, y, w, h, text):
    ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)],
                         closed=True, fc="#fff6df", ec="#c98500", lw=1.6))
    ax.text(x, y, text, ha="center", va="center", fontsize=10.5, color=INK)


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


# ------------------------------------------------------------- architecture
fig, ax = canvas(16, 9)
# frontend row
ax.text(0.5, 7.55, "FRONTEND", fontsize=10, weight="bold", color=INK2)
stages = ["Source\nprogram (.src)", "Lexer", "Parser", "AST", "TAC\nGenerator", "TAC\nprogram"]
xs = [1.5, 4.0, 6.5, 9.0, 11.5, 14.3]
for i, (x, s) in enumerate(zip(xs, stages)):
    fc, ec = (GREY_L, LINE) if i in (0, 5) else (BLUE_L, BLUE)
    box(ax, x, 6.75, 2.0, 1.0, s, fc=fc, ec=ec)
    if i:
        arrow(ax, xs[i - 1] + 1.0, 6.75, x - 1.0, 6.75)
# agent loop panel
ax.add_patch(FancyBboxPatch((1.0, 0.75), 10.6, 4.65, boxstyle="round,pad=0.02,rounding_size=0.25",
                            fc="#f6f8fb", ec=BLUE, lw=1.4, ls=(0, (5, 4))))
ax.text(2.45, 5.0, "AGENT LOOP  (Orchestrator, up to 50 iterations per program)", fontsize=10,
        weight="bold", color=BLUE)
comps = [(3.0, 3.75, "1  Code Analyzer\ndataflow analysis,\nranked opportunities"),
         (6.3, 3.75, "2  Proposer\nrule-based (6 types)\n+ Gemini LLM"),
         (9.6, 3.75, "3  Verifier\ndifferential testing\n+ symbolic check"),
         (9.6, 1.65, "4  Cost Evaluator\nweighted static cost"),
         (6.3, 1.65, "5  Decision\naccept only if verified\nAND cheaper")]
for x, y, t in comps:
    box(ax, x, y, 2.75, 1.35, t, size=10.5)
arrow(ax, 4.375, 3.75, 4.925, 3.75)
arrow(ax, 7.675, 3.75, 8.225, 3.75)
arrow(ax, 9.6, 3.075, 9.6, 2.325)
arrow(ax, 8.225, 1.65, 7.675, 1.65)
arrow(ax, 4.925, 1.65, 3.0, 3.07, text="next iteration", tx=-0.55, ty=-0.3, rad=-0.25)
# TAC into loop
ax.plot([14.3, 14.3, 1.9, 1.9], [6.25, 5.8, 5.8, 4.9], color=LINE, lw=1.6)
arrow(ax, 1.9, 4.95, 1.9, 4.43)
ax.text(8.1, 5.8, "TAC enters the agent loop", ha="center", va="center", fontsize=9.5, color=LINE,
        weight="bold", bbox=dict(fc=BG, ec="none", pad=1.5))
# outputs
ax.text(12.4, 5.0, "OUTPUTS", fontsize=10, weight="bold", color=INK2)
outs = ["Optimized TAC", "Decision logs\n(.log + .json)", "Metrics\n(CSV + JSON)", "7 charts (PNG)"]
for i, t in enumerate(outs):
    box(ax, 14.0, 4.25 - i * 1.05, 3.2, 0.85, t, fc=GREEN_L, ec=GREEN, size=10.5)
arrow(ax, 11.6, 2.9, 12.4, 2.9, text="final\ncheck", ty=0.45)
fig.savefig(os.path.join(OUT, "slide8_architecture.png"), dpi=150, bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ------------------------------------------------------------- workflow (vertical)
fig, ax = canvas(10.2, 9.6)
C = 3.2                                    # main column
box(ax, C, 9.0, 1.9, 0.6, "START", fc=GREY_L, ec=LINE, weight="bold")
box(ax, C, 7.9, 2.6, 0.8, "Analyze TAC\nfind opportunities")
diamond(ax, C, 6.6, 2.6, 1.1, "Any untried\nopportunity?")
box(ax, C, 5.3, 2.6, 0.7, "Pick highest priority")
box(ax, C, 4.2, 2.6, 0.7, "Propose transformation\n(rule-based or Gemini)", size=10)
diamond(ax, C, 2.9, 2.6, 1.1, "Verified\ncorrect?")
diamond(ax, C, 1.5, 2.6, 1.1, "Cost\nlower?")
box(ax, C, 0.3, 2.6, 0.6, "ACCEPT: update program", fc=GREEN_L, ec=GREEN, weight="bold", size=10.5)
box(ax, 6.3, 6.6, 2.2, 0.7, "Final check\nvs. original", fc=GREY_L, ec=LINE, size=10)
box(ax, 8.3, 6.6, 1.5, 0.6, "END", fc=GREY_L, ec=LINE, weight="bold")
box(ax, 6.3, 2.9, 2.6, 0.7, "REJECT: invalid", fc=RED_L, ec=RED, size=10.5)
box(ax, 6.3, 1.5, 2.6, 0.7, "REJECT: no cost gain", fc=RED_L, ec=RED, size=10.5)

arrow(ax, C, 8.7, C, 8.3)
arrow(ax, C, 7.5, C, 7.15)
arrow(ax, C, 6.05, C, 5.65, text="Yes", tx=0.35, color=GREEN)
arrow(ax, C, 4.95, C, 4.55)
arrow(ax, C, 3.85, C, 3.45)
arrow(ax, C, 2.35, C, 2.05, text="Pass", tx=0.4, color=GREEN)
arrow(ax, C, 0.95, C, 0.6, text="Yes", tx=0.35, color=GREEN)
arrow(ax, 4.5, 6.6, 5.2, 6.6, text="No", ty=0.22, color=RED)
arrow(ax, 7.4, 6.6, 7.55, 6.6)
arrow(ax, 4.5, 2.9, 5.0, 2.9, text="Fail", ty=0.22, color=RED)
arrow(ax, 4.5, 1.5, 5.0, 1.5, text="No", ty=0.22, color=RED)
# accepted -> back to Analyze (left side)
ax.plot([1.9, 0.75, 0.75], [0.3, 0.3, 7.9], color=GREEN, lw=1.6)
arrow(ax, 0.75, 7.9, 1.9, 7.9, color=GREEN)
ax.text(0.45, 4.1, "accepted: analyze again (new opportunities may appear)", rotation=90,
        ha="center", va="center", fontsize=9.5, color=GREEN, weight="bold")
# rejected -> back to Analyze (right side)
ax.plot([7.6, 9.6], [2.9, 2.9], color=LINE, lw=1.5, ls=(0, (4, 3)))
ax.plot([7.6, 9.6, 9.6, 5.0], [1.5, 1.5, 8.35, 8.35], color=LINE, lw=1.5, ls=(0, (4, 3)))
arrow(ax, 5.0, 8.35, 4.5, 8.1, color=LINE)
ax.text(9.9, 4.6, "rejected: remember it, try the next one", rotation=90, ha="center", va="center",
        fontsize=9.5, color=INK2)
fig.savefig(os.path.join(OUT, "slide9_workflow.png"), dpi=150, bbox_inches="tight", facecolor=BG)
plt.close(fig)
print("ok")
