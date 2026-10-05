"""Instruction-level control-flow graph and dataflow analyses over TAC.

Every analysis works on a plain list of TACInstruction.  Jumps to labels that
do not exist are treated as program exit (no successor) so that malformed
candidate programs never crash the analyses.
"""
from __future__ import annotations

from collections import deque

from .instruction import TACInstruction, TACOp


def label_map(instrs: list[TACInstruction]) -> dict[str, int]:
    labels: dict[str, int] = {}
    for i, ins in enumerate(instrs):
        if ins.op == TACOp.LABEL and ins.label not in labels:
            labels[ins.label] = i
    return labels


def successors(instrs: list[TACInstruction]) -> list[list[int]]:
    labels = label_map(instrs)
    n = len(instrs)
    succ: list[list[int]] = []
    for i, ins in enumerate(instrs):
        if ins.op == TACOp.GOTO:
            s = [labels[ins.label]] if ins.label in labels else []
        elif ins.op in (TACOp.IF_GOTO, TACOp.IF_FALSE_GOTO):
            s = [i + 1] if i + 1 < n else []
            target = labels.get(ins.label)
            if target is not None and target not in s:
                s.append(target)
        else:
            s = [i + 1] if i + 1 < n else []
        succ.append(s)
    return succ


def predecessors(succ: list[list[int]]) -> list[list[int]]:
    preds: list[list[int]] = [[] for _ in succ]
    for i, targets in enumerate(succ):
        for t in targets:
            preds[t].append(i)
    return preds


def reachable(succ: list[list[int]]) -> set[int]:
    if not succ:
        return set()
    seen = {0}
    queue = deque([0])
    while queue:
        node = queue.popleft()
        for nxt in succ[node]:
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def has_control_flow(instrs: list[TACInstruction]) -> bool:
    return any(ins.op in (TACOp.LABEL, TACOp.GOTO, TACOp.IF_GOTO, TACOp.IF_FALSE_GOTO)
               for ins in instrs)


def basic_blocks(instrs: list[TACInstruction]) -> list[tuple[int, int]]:
    """Half-open [start, end) index ranges of the basic blocks."""
    n = len(instrs)
    if n == 0:
        return []
    leaders = {0}
    for i, ins in enumerate(instrs):
        if ins.op == TACOp.LABEL:
            leaders.add(i)
        if ins.is_jump() and i + 1 < n:
            leaders.add(i + 1)
    starts = sorted(leaders)
    return [(s, starts[k + 1] if k + 1 < len(starts) else n) for k, s in enumerate(starts)]


def liveness(instrs: list[TACInstruction]) -> tuple[list[set[str]], list[set[str]]]:
    """Classic backward may-analysis. Nothing is live at program exit."""
    succ = successors(instrs)
    n = len(instrs)
    uses = [set(ins.used_vars()) for ins in instrs]
    defs = [{ins.defined_var()} if ins.defined_var() else set() for ins in instrs]
    live_in: list[set[str]] = [set() for _ in range(n)]
    live_out: list[set[str]] = [set() for _ in range(n)]
    changed = True
    while changed:
        changed = False
        for i in range(n - 1, -1, -1):
            out: set[str] = set()
            for s in succ[i]:
                out |= live_in[s]
            inn = uses[i] | (out - defs[i])
            if out != live_out[i] or inn != live_in[i]:
                live_out[i] = out
                live_in[i] = inn
                changed = True
    return live_in, live_out


def _forward_must(instrs, universe, transfer) -> list[set]:
    """Generic forward must-analysis (intersection at joins).

    Returns IN sets per instruction. Unreachable instructions get the empty set.
    """
    succ = successors(instrs)
    preds = predecessors(succ)
    reach = reachable(succ)
    n = len(instrs)
    in_sets: list[set] = [set(universe) if (i in reach and i != 0) else set() for i in range(n)]
    out_sets: list[set] = [transfer(i, in_sets[i]) for i in range(n)]
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if i not in reach or i == 0:
                continue
            reach_preds = [p for p in preds[i] if p in reach]
            new_in = set(out_sets[reach_preds[0]]) if reach_preds else set()
            for p in reach_preds[1:]:
                new_in &= out_sets[p]
            if new_in != in_sets[i]:
                in_sets[i] = new_in
                out_sets[i] = transfer(i, new_in)
                changed = True
        # instruction 0 may have predecessors (a loop label at index 0), but
        # its IN is pinned to the empty entry state.
    return in_sets


def available_copies(instrs: list[TACInstruction]) -> list[set[tuple[str, str]]]:
    """For each instruction, the set of copies ``x = y`` guaranteed to hold on entry."""
    universe = {(ins.result, ins.arg1) for ins in instrs
                if ins.op == TACOp.ASSIGN and ins.result != ins.arg1}

    def transfer(i: int, in_set: set) -> set:
        ins = instrs[i]
        d = ins.defined_var()
        out = {c for c in in_set if d not in c} if d else set(in_set)
        if ins.op == TACOp.ASSIGN and ins.result != ins.arg1:
            out.add((ins.result, ins.arg1))
        return out

    return _forward_must(instrs, universe, transfer)


def definitely_assigned(instrs: list[TACInstruction]) -> list[set[str]]:
    """For each instruction, variables assigned on every path reaching it."""
    universe = {ins.defined_var() for ins in instrs if ins.defined_var()}

    def transfer(i: int, in_set: set) -> set:
        d = instrs[i].defined_var()
        return in_set | {d} if d else set(in_set)

    return _forward_must(instrs, universe, transfer)
