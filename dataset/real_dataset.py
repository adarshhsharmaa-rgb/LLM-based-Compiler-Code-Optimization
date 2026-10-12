"""Real-program dataset: 500 accepted Codeforces submissions in the generator's seven categories.

The programs come from ``open-r1/codeforces-submissions`` on Hugging Face (CC-BY-4.0), a
2025 collection of 12.6 million Codeforces submissions. A submission is kept when

  * the judge accepted it (verdict ``OK``),
  * the C front-end compiles it in strict mode (see ``src/frontend/c_frontend.py``), so it
    is ``main`` only, integers only, no arrays -- written in C, or in C++ with ``scanf`` /
    ``printf`` and nothing else from C++,
  * it prints something and finishes quickly on every input set the Verification Module
    would try (otherwise no change to it could be verified).

The 500 are then chosen in the generator's proportions (``CATEGORY_COUNTS``), spread over
as many problems as possible, newest submissions first.

    python dataset/real_dataset.py collect     # download shards, keep what is usable
    python dataset/real_dataset.py select      # choose the 500 and write them
    python dataset/real_dataset.py rebuild     # write the same 500 again from the manifest

``collect`` and ``rebuild`` read Parquet files and need ``pip install pyarrow``. The
programs land in ``dataset/real_programs`` (committed, each file names its submission
and the dataset's licence) and the downloads in ``dataset/real_cache`` (git-ignored).
``dataset/real_manifest.json`` lists which submissions were chosen.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agents.verifier import Verifier  # noqa: E402
from src.frontend.ast_nodes import (  # noqa: E402
    Assignment,
    BinaryExpr,
    ForStmt,
    IfStmt,
    UnaryExpr,
    VarDecl,
    VarRef,
    WhileStmt,
)
from src.frontend.c_frontend import CFrontendError, compile_c  # noqa: E402
from src.tac.instruction import TACOp, is_literal  # noqa: E402

CATEGORY_COUNTS = {            # the same proportions as dataset/generator.py
    "arithmetic": 60,
    "nested": 60,
    "repeated_expr": 60,
    "dead_code": 60,
    "loops": 80,
    "conditionals": 80,
    "mixed": 100,
}

DATASET = "open-r1/codeforces-submissions"
LICENSE = "CC-BY-4.0"
SHARD_COUNT = 36
SHARD_URL = "https://huggingface.co/datasets/" + DATASET + "/resolve/main/data/train-{:05d}-of-00036.parquet"
DEFAULT_SHARDS = (35, 33, 30, 26, 5, 0)       # the six files the committed manifest was built from

CACHE_DIR = os.path.join(PROJECT_ROOT, "dataset", "real_cache")
CANDIDATES = os.path.join(CACHE_DIR, "candidates.jsonl")
OUT_DIR = os.path.join(PROJECT_ROOT, "dataset", "real_programs")
MANIFEST = os.path.join(PROJECT_ROOT, "dataset", "real_manifest.json")

MAX_SOURCE_CHARS = 4000        # longer submissions are never in the accepted subset
MIN_INSTRUCTIONS, MAX_INSTRUCTIONS = 8, 300
MAX_INPUTS = 8
MAX_STEPS = 20_000             # a run longer than this makes verification too slow to be useful
NESTED_DEPTH = 3               # "nested": an arithmetic expression at least this many operators deep
ARITHMETIC_OPS = {"+", "-", "*", "/", "%"}
SEED = 42


# ====================================================================== #
# What a program looks like
# ====================================================================== #
def _walk(node):
    """Every AST node below ``node`` (statements and expressions)."""
    if isinstance(node, list):
        for item in node:
            yield from _walk(item)
        return
    yield node
    for name in getattr(node, "__dataclass_fields__", ()):
        child = getattr(node, name)
        if isinstance(child, list) or hasattr(child, "__dataclass_fields__"):
            yield from _walk(child)


def _depth(expr) -> int:
    """How many arithmetic operators are stacked on top of each other in ``expr``."""
    if isinstance(expr, BinaryExpr):
        below = max(_depth(expr.left), _depth(expr.right))
        return below + (expr.op in ARITHMETIC_OPS)
    return _depth(expr.operand) if isinstance(expr, UnaryExpr) else 0


def features(statements: list) -> dict:
    """The properties the categories are decided on, read off the program's AST."""
    nodes = list(_walk(statements))
    read = {n.name for n in nodes if isinstance(n, VarRef)}
    written = {n.target for n in nodes if isinstance(n, Assignment)}
    written |= {n.name for n in nodes if isinstance(n, VarDecl) and n.init_expr is not None}
    # x = x + 1 is an update, not an expression the programmer wrote twice
    updates = {id(n.value) for n in nodes if isinstance(n, Assignment) and isinstance(n.value, BinaryExpr)
               and VarRef(n.target) in (n.value.left, n.value.right)}
    seen = Counter(repr(n) for n in nodes
                   if isinstance(n, BinaryExpr) and n.op in ARITHMETIC_OPS and id(n) not in updates
                   and any(isinstance(m, VarRef) for m in _walk(n)))
    return {
        "loop": any(isinstance(n, (WhileStmt, ForStmt)) for n in nodes),
        "branch": any(isinstance(n, IfStmt) for n in nodes),
        "depth": max((_depth(n) for n in nodes if isinstance(n, BinaryExpr)), default=0),
        "dead": bool(written - read),                    # a value is stored and never looked at
        "repeated": any(count > 1 for count in seen.values()),
    }


def category_of(feat: dict) -> str:
    """What the program is a test of.

    A stored value that is never read, or an expression written twice, decides first: the
    generator builds its dead_code and repeated_expr programs around exactly that, and in
    real code both nearly always sit among loops and branches. Everything else goes by its
    control flow, and straight-line programs by how deep their arithmetic is.
    """
    if feat["dead"]:
        return "dead_code"
    if feat["repeated"]:
        return "repeated_expr"
    if feat["loop"] and feat["branch"]:
        return "mixed"
    if feat["loop"]:
        return "loops"
    if feat["branch"]:
        return "conditionals"
    return "nested" if feat["depth"] >= NESTED_DEPTH else "arithmetic"


def canonical(tac) -> str:
    """The TAC with names replaced by their order of appearance, to spot the same program twice."""
    names: dict[str, str] = {}
    lines = []
    for ins in tac.instructions:
        parts = [ins.op.value, ins.operator or ""]
        for value in (ins.result, ins.arg1, ins.arg2, ins.label):
            if value is not None and not is_literal(value):
                value = names.setdefault(value, f"n{len(names)}")
            parts.append(str(value))
        lines.append(" ".join(parts))
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def examine(source: str) -> tuple[dict | None, str]:
    """(features and sizes, "") if the program can be used, else (None, why not)."""
    if len(source) > MAX_SOURCE_CHARS:
        return None, "too long"
    try:
        tac, cprog = compile_c(source, strict=True)
    except CFrontendError:
        return None, "not in the accepted C subset"
    except RecursionError:
        return None, "expression too deep"
    size = len(tac.instructions)
    if not MIN_INSTRUCTIONS <= size <= MAX_INSTRUCTIONS:
        return None, "too small or too large"
    if not any(ins.op == TACOp.PRINT for ins in tac.instructions):
        return None, "prints nothing"
    variables = sorted(tac.get_input_variables())
    if len(variables) > MAX_INPUTS:
        return None, "too many inputs"
    verifier = Verifier(max_steps=MAX_STEPS)
    finished = 0
    tried: set[tuple] = set()
    for inputs in verifier.input_sets(variables, verifier._constants(tac)):
        key = tuple(sorted(inputs.items()))
        if key in tried:
            continue
        tried.add(key)
        outcome = verifier._run(tac, inputs)
        if outcome.timed_out:
            return None, "runs too long on a test input"
        finished += outcome.error is None and bool(outcome.outputs)
    if not finished:
        return None, "never finishes with output"
    info = features(cprog.ast.statements)
    info.update(instructions=size, inputs=len(variables), texts=len(cprog.texts), canonical=canonical(tac))
    return info, ""


# ====================================================================== #
# collect: shards -> candidates.jsonl
# ====================================================================== #
def download(url: str, path: str, attempts: int = 8) -> None:
    """Fetch ``url`` into ``path``, picking up where a broken connection stopped."""
    part = path + ".part"
    for attempt in range(1, attempts + 1):
        have = os.path.getsize(part) if os.path.exists(part) else 0
        request = urllib.request.Request(url, headers={"User-Agent": "compiler-lab-dataset",
                                                       "Range": f"bytes={have}-"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status != 206:
                    have = 0                       # the server is sending the whole file again
                with open(part, "ab" if have else "wb") as fh:
                    while chunk := response.read(1 << 20):
                        fh.write(chunk)
            os.replace(part, path)
            return
        except urllib.error.HTTPError as exc:
            if exc.code == 416:                    # nothing left to fetch
                os.replace(part, path)
                return
            error = exc
        except OSError as exc:
            error = exc
        print(f"    download interrupted ({error}); retry {attempt}/{attempts}", flush=True)
        time.sleep(min(30, 3 * attempt))
    raise RuntimeError(f"could not download {url}")


def shard_rows(index: int, keep: bool = False):
    """Rows of one shard as dicts, downloading the file first if it is not in the cache."""
    try:
        import pyarrow.parquet as pq
    except ImportError:
        raise SystemExit("This step reads Parquet files: run  pip install pyarrow  first.") from None
    path = os.path.join(CACHE_DIR, "shards", f"train-{index:05d}.parquet")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        print(f"  downloading shard {index} ...", flush=True)
        download(SHARD_URL.format(index), path)
    columns = ["submission_id", "source", "problem_id", "programmingLanguage", "verdict", "creationTimeSeconds"]
    parquet = pq.ParquetFile(path)
    for batch in parquet.iter_batches(batch_size=4000, columns=columns):
        yield from batch.to_pylist()
    parquet.close()
    if not keep:
        os.remove(path)


def is_c_family(language: str) -> bool:
    return language.startswith("GNU C") or "C++" in language


def collect(shards: list[int], keep: bool) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    done: set[int] = set()
    if os.path.exists(CANDIDATES):
        with open(CANDIDATES, encoding="utf-8") as fh:
            done = {json.loads(line)["shard"] for line in fh}
    for index in shards:
        if index in done:
            print(f"shard {index}: already collected")
            continue
        seen = kept = 0
        why = Counter()
        records = []
        for row in shard_rows(index, keep):
            source = row["source"] or ""
            if row["verdict"] != "OK" or not is_c_family(row["programmingLanguage"] or ""):
                continue
            if "main" not in source or ("printf" not in source and "puts" not in source):
                continue
            seen += 1
            info, reason = examine(source)
            if info is None:
                why[reason] += 1
                continue
            kept += 1
            records.append({"submission_id": row["submission_id"], "problem_id": row["problem_id"],
                            "language": row["programmingLanguage"], "created": int(row["creationTimeSeconds"] or 0),
                            "shard": index, "features": info, "source": source})
        with open(CANDIDATES, "a", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record) + "\n")
        print(f"shard {index}: {seen} accepted C/C++ submissions looked at, {kept} usable "
              f"({len({r['problem_id'] for r in records})} problems)")
        for reason, n in why.most_common():
            print(f"    {n:6d}  {reason}")


# ====================================================================== #
# select: candidates.jsonl -> 500 programs + manifest
# ====================================================================== #
def load_candidates() -> list[dict]:
    if not os.path.exists(CANDIDATES):
        raise SystemExit(f"No candidates yet: run  python dataset/real_dataset.py collect  first.")
    with open(CANDIDATES, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def choose(candidates: list[dict], counts: dict[str, int] = CATEGORY_COUNTS, seed: int = SEED) -> dict[str, list[dict]]:
    """Fill every category's quota, taking one program per problem per round.

    Programs that compile to the same TAC (up to renaming) count once. Within a problem the
    newest submission goes first, and the order of the problems is a seeded shuffle, so the
    same candidates always give the same choice.
    """
    unique: dict[str, dict] = {}
    for cand in sorted(candidates, key=lambda c: (-c["created"], c["submission_id"])):
        unique.setdefault(cand["features"]["canonical"], cand)
    pools: dict[str, dict[str, list[dict]]] = {cat: defaultdict(list) for cat in counts}
    for cand in unique.values():
        pools[category_of(cand["features"])][cand["problem_id"]].append(cand)
    rng = random.Random(seed)
    chosen: dict[str, list[dict]] = {}
    for category, quota in counts.items():
        problems = sorted(pools[category])
        rng.shuffle(problems)
        picked: list[dict] = []
        depth = 0
        while len(picked) < quota and any(len(pools[category][p]) > depth for p in problems):
            for problem in problems:
                if len(pools[category][problem]) > depth and len(picked) < quota:
                    picked.append(pools[category][problem][depth])
            depth += 1
        chosen[category] = picked
    return chosen


def header(category: str, number: int, cand: dict) -> str:
    contest, _, _ = cand["problem_id"].partition("/")
    day = datetime.datetime.fromtimestamp(cand["created"], datetime.timezone.utc).date()
    return (f"// category: {category}  (real program {number:03d})\n"
            f"// Codeforces submission {cand['submission_id']}, problem {cand['problem_id']}, "
            f"{cand['language']}, {day}\n"
            f"// https://codeforces.com/contest/{contest}/submission/{cand['submission_id']}\n"
            f"// from the dataset {DATASET} ({LICENSE})\n")


def write_programs(chosen: dict[str, list[dict]]) -> list[dict]:
    entries = []
    for category, picked in chosen.items():
        folder = os.path.join(OUT_DIR, category)
        os.makedirs(folder, exist_ok=True)
        for old in os.listdir(folder):
            if old.endswith(".c"):
                os.remove(os.path.join(folder, old))
        for number, cand in enumerate(picked, start=1):
            name = f"{category}_{number:03d}.c"
            source = cand["source"].replace("\r\n", "\n").replace("\r", "\n")
            with open(os.path.join(folder, name), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(header(category, number, cand) + source.rstrip("\n") + "\n")
            entries.append({"file": f"{category}/{name}", "category": category,
                            "submission_id": cand["submission_id"], "problem_id": cand["problem_id"],
                            "language": cand["language"], "created": cand["created"], "shard": cand["shard"],
                            "sha256": hashlib.sha256(cand["source"].encode("utf-8")).hexdigest(),
                            "features": {k: v for k, v in cand["features"].items() if k != "canonical"}})
    return entries


def select() -> int:
    candidates = load_candidates()
    chosen = choose(candidates)
    short = {cat: (len(chosen[cat]), quota) for cat, quota in CATEGORY_COUNTS.items() if len(chosen[cat]) < quota}
    print(f"{len(candidates)} usable submissions from {len({c['problem_id'] for c in candidates})} problems")
    for category, picked in chosen.items():
        per_problem = Counter(c["problem_id"] for c in picked)
        print(f"  {category:<14} {len(picked):>3} / {CATEGORY_COUNTS[category]:<3}  from {len(per_problem):>3} problems"
              f"  (at most {max(per_problem.values(), default=0)} per problem)")
    if short:
        print("Not enough programs for: " + ", ".join(f"{c} ({have} of {need})" for c, (have, need) in short.items()))
        print("Collect more shards, e.g.  python dataset/real_dataset.py collect --shards 1 2 3")
        return 1
    entries = write_programs(chosen)
    manifest = {"dataset": DATASET, "license": LICENSE, "seed": SEED,
                "candidates": len(candidates), "shards": sorted({c["shard"] for c in candidates}),
                "counts": {cat: len(picked) for cat, picked in chosen.items()},
                "problems": len({e["problem_id"] for e in entries}), "programs": entries}
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    print(f"Wrote {len(entries)} programs from {manifest['problems']} problems to {os.path.relpath(OUT_DIR, PROJECT_ROOT)}")
    return 0


def rebuild(keep: bool) -> int:
    """Write the programs the manifest lists, fetching their source from the dataset again."""
    with open(MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)
    wanted = {e["submission_id"]: e for e in manifest["programs"]}
    found: dict[str, list[dict]] = {cat: [] for cat in CATEGORY_COUNTS}
    for index in sorted({e["shard"] for e in manifest["programs"]}):
        for row in shard_rows(index, keep):
            entry = wanted.get(row["submission_id"])
            source = row["source"] or ""
            if entry and entry["shard"] == index and hashlib.sha256(source.encode("utf-8")).hexdigest() == entry["sha256"]:
                found[entry["category"]].append({**entry, "source": source, "features": {**entry["features"], "canonical": ""}})
    order = {e["submission_id"]: i for i, e in enumerate(manifest["programs"])}
    for picked in found.values():
        picked.sort(key=lambda c: order[c["submission_id"]])
    written = write_programs(found)
    print(f"Wrote {len(written)} of {len(wanted)} programs to {os.path.relpath(OUT_DIR, PROJECT_ROOT)}")
    return 0 if len(written) == len(wanted) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the real-program dataset from Codeforces submissions")
    sub = parser.add_subparsers(dest="command", required=True)
    p_collect = sub.add_parser("collect", help="download shards and keep the usable submissions")
    p_collect.add_argument("--shards", type=int, nargs="+", default=list(DEFAULT_SHARDS),
                           help=f"which of the {SHARD_COUNT} files to read, about 150 MB each "
                                f"(default: {' '.join(map(str, DEFAULT_SHARDS))})")
    p_collect.add_argument("--keep-shards", action="store_true", help="do not delete a shard after reading it")
    sub.add_parser("select", help="choose the 500 programs and write them with the manifest")
    p_rebuild = sub.add_parser("rebuild", help="write the programs listed in the manifest again")
    p_rebuild.add_argument("--keep-shards", action="store_true", help="do not delete a shard after reading it")
    args = parser.parse_args()
    if args.command == "collect":
        bad = [i for i in args.shards if not 0 <= i < SHARD_COUNT]
        if bad:
            parser.error(f"shard numbers go from 0 to {SHARD_COUNT - 1}")
        collect(args.shards, args.keep_shards)
        return 0
    if args.command == "select":
        return select()
    return rebuild(args.keep_shards)


if __name__ == "__main__":
    sys.exit(main())
