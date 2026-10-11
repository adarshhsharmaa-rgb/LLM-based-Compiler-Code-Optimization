"""Re-renders the 7 result charts with larger relative text for use on slides.

Shrinking every figure while keeping font sizes in points makes the text
proportionally larger once the image is scaled up to fill a slide.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import matplotlib.pyplot as plt
import plotly.graph_objects as go

from src.visualization import charts
from src.visualization.report import load_results, compare_runs

SHRINK = 0.66
_subplots = plt.subplots


def small_subplots(*args, figsize=None, **kw):
    if figsize:
        figsize = (figsize[0] * SHRINK, figsize[1] * SHRINK)
    return _subplots(*args, figsize=figsize, **kw)


plt.subplots = small_subplots
_write = go.Figure.write_image


def small_write(self, *args, **kw):
    self.update_layout(width=880, height=470, margin=dict(l=20, r=20, t=55, b=60))
    self.update_traces(textfont=dict(size=16), selector=dict(type="sankey"))
    return _write(self, *args, **kw)


go.Figure.write_image = small_write
go.Figure.write_html = lambda self, *a, **k: None

out = os.path.join(ROOT, "presentation")
records = load_results(os.path.join(ROOT, "output"))
baseline = load_results(os.path.join(ROOT, "output_rule_only"))
paths = charts.generate_all_charts(records, out)
paths.append(charts.comparison_chart(compare_runs(baseline, records), out))
for p in paths:
    print(os.path.relpath(p, ROOT))
