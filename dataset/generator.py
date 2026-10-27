"""Programmatic dataset generator: 500 mini-language programs in 7 categories.

Run directly:  python dataset/generator.py

Every generated program is compiled and executed before it is written, so each
file is guaranteed to be syntactically valid, terminate, and print at least one
value. Some programs use free *input* variables (read but never declared); they
are listed in an ``// inputs:`` header comment, and the verifier feeds them
random values during differential testing.
"""
from __future__ import annotations

import os
import random
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.frontend import compile_source  # noqa: E402
from src.tac.interpreter import TACInterpreter  # noqa: E402

CATEGORY_COUNTS = {
    "arithmetic": 60,
    "nested": 60,
    "repeated_expr": 60,
    "dead_code": 60,
    "loops": 80,
    "conditionals": 80,
    "mixed": 100,
}

FILE_PREFIX = {cat: cat for cat in CATEGORY_COUNTS}

DEFAULT_OUT_DIR = os.path.join(PROJECT_ROOT, "dataset", "programs")

NAMES = ["a", "b", "c", "d", "e", "f", "g", "h", "m", "n", "p", "q", "r", "s",
         "u", "v", "w", "x", "y", "z", "k", "val", "res", "tmp", "acc", "num"]
INPUT_NAMES = ["in_a", "in_b", "in_c", "in_x", "in_y", "in_n"]


class _Names:
    def __init__(self, reserved=()):
        self.pool = [n for n in NAMES if n not in reserved]
        random.shuffle(self.pool)
        self.extra = 0

    def fresh(self) -> str:
        if self.pool:
            return self.pool.pop()
        self.extra += 1
        return f"v{self.extra}"


def _const(lo: int = 1, hi: int = 20) -> str:
    return str(random.randint(lo, hi))


def _arith_op(allow_div: bool = False) -> str:
    ops = ["+", "+", "-", "*"]
    if allow_div:
        ops += ["/", "%"]
    return random.choice(ops)


def _expr(depth: int, variables: list[str], const_bias: float = 0.5, allow_div: bool = True,
          top: bool = False) -> str:
    """Random arithmetic expression. Divisors are always non-zero constants.

    With ``top=True`` the root (and its first level) is always an operator node.
    """
    if depth <= 0 or (not top and random.random() < 0.25):
        if variables and random.random() > const_bias:
            return random.choice(variables)
        return _const()
    op = _arith_op(allow_div)
    left = _expr(depth - 1, variables, const_bias, allow_div, top=top and depth > 2)
    if op in ("/", "%"):
        right = _const(2, 9)
    else:
        right = _expr(depth - 1, variables, const_bias, allow_div, top=top and depth > 2)
    return f"({left} {op} {right})"


def _strip(expr: str) -> str:
    if expr.startswith("(") and expr.endswith(")"):
        depth = 0
        for i, ch in enumerate(expr):
            depth += ch == "("
            depth -= ch == ")"
            if depth == 0 and i != len(expr) - 1:
                return expr
        return expr[1:-1]
    return expr


def _identity_wrap(var: str) -> str:
    return random.choice([f"{var} + 0", f"{var} * 1", f"0 + {var}", f"1 * {var}",
                          f"{var} - 0", f"{var} / 1"])


# ====================================================================== #
# Category generators. Each returns (source_lines, input_names).
# ====================================================================== #
def gen_arithmetic():
    names = _Names()
    lines, live = [], []
    for _ in range(random.randint(2, 4)):
        v = names.fresh()
        style = random.random()
        if style < 0.4 or not live:
            expr = f"{_const()} {_arith_op()} {_const()}"
        elif style < 0.75:
            expr = f"{random.choice(live)} {_arith_op()} {_const()}"
        else:
            expr = f"{random.choice(live)} {_arith_op()} {_const()} {random.choice(['+', '-'])} {_const()}"
        lines.append(f"int {v} = {expr};")
        live.append(v)
    lines.append(f"print({live[-1]});")
    if random.random() < 0.4:
        lines.append(f"print({live[0]} {random.choice(['+', '*', '-'])} {_const()});")
    return lines, []


def gen_nested():
    names = _Names()
    lines, live = [], []
    for _ in range(random.randint(2, 3)):
        v = names.fresh()
        expr = _strip(_expr(random.randint(2, 3), live, const_bias=0.7, top=True))
        lines.append(f"int {v} = {expr};")
        live.append(v)
    final = names.fresh()
    a = random.choice(live)
    lines.append(f"int {final} = {a} + ({a} * ({_const()} {_arith_op()} {_const()}));")
    lines.append(f"print({final});")
    return lines, []


def gen_repeated_expr():
    use_inputs = random.random() < 0.5
    names = _Names()
    if use_inputs:
        a, b = random.sample(INPUT_NAMES, 2)
        lines = []
        inputs = [a, b]
    else:
        a, b = names.fresh(), names.fresh()
        lines = [f"int {a} = {_const()};", f"int {b} = {_const()};"]
        inputs = []
    op = random.choice(["+", "*", "-"])
    c, d, e = names.fresh(), names.fresh(), names.fresh()
    second = f"{b} {op} {a}" if op in "+*" and random.random() < 0.4 else f"{a} {op} {b}"
    lines.append(f"int {c} = {a} {op} {b};")
    lines.append(f"int {d} = {second};")
    variant = random.random()
    if variant < 0.33:
        lines.append(f"int {e} = {c} + {d};")
    elif variant < 0.66:
        op2 = random.choice(["+", "-", "*"])
        lines.append(f"int {e} = ({a} {op2} {b}) * ({a} {op2} {b});")
    else:
        # operand is redefined between the two occurrences: CSE must NOT fire here
        lines.append(f"{a} = {a} + {_const(1, 5)};")
        lines.append(f"int {e} = ({a} {op} {b}) + {c};")
    out = [e]
    if random.random() < 0.5:
        f = names.fresh()
        lines.append(f"int {f} = {c} * {d} + {c} * {d};")
        out.append(f)
    lines.append(f"print({' + '.join(out)});")
    return lines, inputs


def gen_dead_code():
    names = _Names()
    kinds = ["live"] * random.randint(1, 3) + ["dead"] * random.randint(1, 3)
    random.shuffle(kinds)
    kinds[0] = "live"
    lines, live, declared = [], [], []
    for kind in kinds:
        v = names.fresh()
        src = random.choice(declared) if declared and random.random() < 0.6 else None
        if kind == "live":
            expr = _const() if src is None else f"{src} {_arith_op()} {_const()}"
            live.append(v)
        else:
            style = random.random()
            if src is None or style < 0.25:
                expr = _const(10, 99)
            elif style < 0.75:
                expr = f"{src} {random.choice(['*', '+', '-'])} {_const()}"
            else:
                expr = f"{src} / {_const(2, 9)}"
        lines.append(f"int {v} = {expr};")
        declared.append(v)
    if random.random() < 0.5:
        # overwritten before use: the first store is dead
        v = random.choice(live)
        lines.append(f"{v} = {_const(50, 90)};")
        lines.append(f"{v} = {v} + {_const()};")
    result = names.fresh()
    lines.append(f"int {result} = {random.choice(live)} + {_const()};")
    lines.append(f"print({result});")
    return lines, []


def gen_loops():
    names = _Names(reserved=("i", "j"))
    acc = random.choice(["sum", "total", "acc", "prod"])
    bound = random.randint(3, 12)
    invariant = names.fresh()
    init = "1" if acc == "prod" else "0"
    lines = [f"int {acc} = {init};"]
    body = [f"int {invariant} = {_const(1, 9)} {random.choice(['+', '*', '-'])} {_const(1, 9)};"]
    upd_op = "*" if acc == "prod" else "+"
    if acc == "prod":
        body = [f"int {invariant} = {_const(1, 3)} {random.choice(['+', '*'])} {_const(0, 1)};"]
        bound = random.randint(3, 6)
    body.append(f"{acc} = {acc} {upd_op} {_identity_wrap(invariant) if random.random() < 0.5 else invariant};")
    if random.random() < 0.4:
        dead = names.fresh()
        body.append(f"int {dead} = {invariant} * {_const()};")
    use_while = random.random() < 0.5
    nested = random.random() < 0.2
    inner = []
    if nested:
        cnt = names.fresh()
        lines.append(f"int {cnt} = 0;")
        inner = [f"for (int j = 0; j < {random.randint(2, 4)}; j = j + 1) {{",
                 f"    {cnt} = {cnt} + {random.choice(['1', '2 - 1', '1 * 1'])};",
                 "}"]
    if use_while:
        lines.append("int i = 0;")
        lines.append(f"while (i < {bound}) {{")
        lines += ["    " + s for s in body + inner]
        lines.append("    i = i + 1;")
        lines.append("}")
    else:
        lines.append(f"for (int i = 0; i < {bound}; i = i + 1) {{")
        lines += ["    " + s for s in body + inner]
        lines.append("}")
    lines.append(f"print({acc});")
    if nested:
        lines.append(f"print({cnt});")
    if random.random() < 0.3:
        lines.append(f"print({acc} * {random.choice(['2', '4', '8', '1'])});")
    return lines, []


def gen_conditionals():
    use_input = random.random() < 0.5
    names = _Names()
    x = random.choice(INPUT_NAMES) if use_input else names.fresh()
    y = names.fresh()
    lines = [] if use_input else [f"int {x} = {random.randint(-20, 20)};"]
    lines.append(f"int {y} = 0;")
    k = random.randint(-10, 10)
    cmp = random.choice([">", "<", ">=", "<=", "==", "!="])
    cond = f"{x} {cmp} {k}"
    if random.random() < 0.25:
        cond = f"{cond} && {x} != {random.randint(-30, 30)}"
    elif random.random() < 0.2:
        cond = f"{cond} || {x} == {random.randint(-5, 5)}"
    then_stmts = [f"{y} = {_identity_wrap(x)};"]
    else_stmts = [f"{y} = {x} {random.choice(['+', '-', '*'])} {_const(1, 9)};"]
    if random.random() < 0.4:
        then_stmts.append(f"{y} = {y} + ({_const(1, 5)} * {_const(1, 5)});")
    if random.random() < 0.3:
        z = names.fresh()
        then_stmts.insert(0, f"int {z} = {_const()} + {_const()};")
    has_else = random.random() < 0.8
    lines.append(f"if ({cond}) {{")
    lines += ["    " + s for s in then_stmts]
    if has_else:
        lines.append("} else {")
        lines += ["    " + s for s in else_stmts]
    lines.append("}")
    if random.random() < 0.3:
        w = names.fresh()
        lines.append(f"int {w} = {random.randint(1, 9)};")
        lines.append(f"if ({w} > {random.randint(0, 9)}) {{")
        lines.append(f"    {y} = {y} + {w} * 1;")
        lines.append("}")
    lines.append(f"print({y});")
    return lines, [x] if use_input else []


def gen_mixed():
    names = _Names(reserved=("i",))
    use_inputs = random.random() < 0.3
    lines: list[str] = []
    inputs: list[str] = []
    if use_inputs:
        base = random.choice(INPUT_NAMES)
        inputs.append(base)
    else:
        base = names.fresh()
        lines.append(f"int {base} = {_const()} + {_const()};")
    live = [base]
    features = random.sample(["algebraic", "dead", "cse", "strength", "fold", "loop", "branch"],
                             k=random.randint(3, 5))
    for feat in features:
        v = names.fresh()
        src = random.choice(live)
        if feat == "algebraic":
            lines.append(f"int {v} = {_identity_wrap(src)};")
            live.append(v)
        elif feat == "dead":
            lines.append(f"int {v} = {random.choice([_const(10, 99), f'{src} * {_const()}'])};")
        elif feat == "cse":
            other = random.choice(live)
            w = names.fresh()
            lines.append(f"int {v} = {src} * {other};")
            lines.append(f"int {w} = {src} * {other} + {v};")
            live.append(w)
        elif feat == "strength":
            lines.append(f"int {v} = {src} * {random.choice(['2', '4', '8', '16'])};")
            live.append(v)
        elif feat == "fold":
            lines.append(f"int {v} = {src} + ({_const()} * {_const()});")
            live.append(v)
        elif feat == "loop":
            lines.append(f"int {v} = 0;")
            lines.append(f"for (int i = 0; i < {random.randint(2, 6)}; i = i + 1) {{")
            lines.append(f"    {v} = {v} + ({_const(1, 4)} + {_const(1, 4)});")
            lines.append("}")
            live.append(v)
        elif feat == "branch":
            lines.append(f"int {v} = {src};")
            lines.append(f"if ({src} > {random.randint(-5, 15)}) {{")
            lines.append(f"    {v} = {v} * 1 + {_const(1, 5)};")
            lines.append("} else {")
            lines.append(f"    {v} = {v} - 0;")
            lines.append("}")
            live.append(v)
    picks = live[-2:] if len(live) > 1 else live
    lines.append(f"print({' + '.join(picks)});")
    return lines, inputs


GENERATORS = {
    "arithmetic": gen_arithmetic,
    "nested": gen_nested,
    "repeated_expr": gen_repeated_expr,
    "dead_code": gen_dead_code,
    "loops": gen_loops,
    "conditionals": gen_conditionals,
    "mixed": gen_mixed,
}


def _validate(source: str, inputs: list[str]) -> bool:
    """Compile the program and run it on a few input sets."""
    try:
        tac = compile_source(source)
        interp = TACInterpreter()
        for trial in range(3):
            env = {v: random.Random(trial).randint(-100, 100) for v in inputs}
            if not interp.execute(tac, env, max_steps=20000):
                return False
        return not (set(tac.get_input_variables()) - set(inputs))
    except Exception:  # any compile/runtime failure -> regenerate
        return False


def generate_program(category: str, index: int) -> str:
    gen = GENERATORS[category]
    for _ in range(100):
        lines, inputs = gen()
        header = [f"// category: {category}  (program {index:03d})"]
        if inputs:
            header.append(f"// inputs: {', '.join(inputs)}")
        source = "\n".join(header + lines) + "\n"
        if _validate(source, inputs):
            return source
    raise RuntimeError(f"could not generate a valid {category} program")


def generate_dataset(out_dir: str = DEFAULT_OUT_DIR, seed: int = 42) -> dict[str, int]:
    random.seed(seed)
    counts = {}
    for category, count in CATEGORY_COUNTS.items():
        cat_dir = os.path.join(out_dir, category)
        os.makedirs(cat_dir, exist_ok=True)
        for old in os.listdir(cat_dir):
            if old.endswith(".src"):
                os.remove(os.path.join(cat_dir, old))
        for idx in range(1, count + 1):
            source = generate_program(category, idx)
            path = os.path.join(cat_dir, f"{FILE_PREFIX[category]}_{idx:03d}.src")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(source)
        counts[category] = count
    return counts


def main() -> None:
    counts = generate_dataset()
    total = sum(counts.values())
    for cat, n in counts.items():
        print(f"  {cat:<14} {n:>4} programs")
    print(f"Generated {total} programs in {DEFAULT_OUT_DIR}")


if __name__ == "__main__":
    main()
