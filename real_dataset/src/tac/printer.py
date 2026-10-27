"""Pretty-printer for TAC listings."""
from __future__ import annotations

from .instruction import TACOp
from .program import TACProgram


def format_tac(program: TACProgram, indent: str = "    ", line_numbers: bool = True,
               prefix: str = "") -> str:
    """Render a program with line numbers; labels are outdented, code indented."""
    if len(program) == 0:
        return f"{prefix}(empty program)"
    width = len(str(len(program) - 1))
    lines = []
    for idx, ins in enumerate(program.instructions):
        body = ins.to_string() if ins.op == TACOp.LABEL else indent + ins.to_string()
        if line_numbers:
            lines.append(f"{prefix}{idx:>{width}} | {body}")
        else:
            lines.append(f"{prefix}{body}")
    return "\n".join(lines)
