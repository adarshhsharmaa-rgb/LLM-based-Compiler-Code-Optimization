"""Render the report's class and data-flow diagrams (PlantUML through kroki.io).

    py gen_diagrams.py

Writes class_diagram.png and data_flow_diagram.png next to this file. The
diagram sources live in presentation/make_review2_diagrams.py, so the report
and the presentation always show the same architecture.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "presentation"))

from make_review2_diagrams import CLASS_DIAGRAM, DATA_FLOW, render  # noqa: E402

if __name__ == "__main__":
    render(CLASS_DIAGRAM, "class_diagram.png", ROOT)
    render(DATA_FLOW, "data_flow_diagram.png", ROOT)
    print("Diagrams updated.")
