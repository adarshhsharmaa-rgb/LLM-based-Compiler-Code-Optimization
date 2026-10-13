"""Tests for the real-program dataset: the wider C front-end and the selection of the 500."""
import importlib.util
import os

import pytest

from src.agents.orchestrator import Orchestrator
from src.frontend.c_frontend import TEXT_CODE_BASE, CFrontendError, compile_c
from src.tac.interpreter import TACInterpreter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("real_dataset", os.path.join(ROOT, "dataset", "real_dataset.py"))
real_dataset = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(real_dataset)

YES, NO = TEXT_CODE_BASE, TEXT_CODE_BASE + 1


def run_c(source, inputs=None, strict=True):
    tac, _ = compile_c(source, strict=strict)
    return TACInterpreter().execute(tac, inputs)


def wrap(body):
    return "#include <stdio.h>\nint main() {\n" + body + "\nreturn 0;\n}\n"


# ---------------------------------------------------------------- the wider C subset
def test_return_in_the_middle_of_main_stops_the_program():
    body = 'int n; scanf("%d", &n); if (n < 0) { printf("%d", -1); return 0; } printf("%d", n * 2);'
    assert run_c(wrap(body), {"in_n": -5}) == [-1]
    assert run_c(wrap(body), {"in_n": 4}) == [8]


def test_exit_stops_the_program_inside_a_loop():
    body = 'int i; for (i = 0; i < 10; i++) { if (i == 3) { printf("%d", i); exit(0); } } printf("%d", 99);'
    assert run_c(wrap(body)) == [3]


def test_character_literals_are_their_codes():
    assert run_c(wrap("printf(\"%d %d %d\", 'a', '\\n', '0' + 5);")) == [97, 10, 53]


def test_number_spellings():
    assert run_c(wrap('long long x = 1000000007LL; printf("%lld %d %d %d", x, 0x1F, 010, 7u);')) == [1000000007, 31, 8, 7]


def test_a_number_glued_to_letters_is_refused():
    with pytest.raises(CFrontendError):
        compile_c(wrap('int x = 1e9; printf("%d", x);'))


def test_bool_keeps_only_zero_or_one():
    body = 'bool f = false; int n = 7; f = n; printf("%d", f); f = n > 9; printf("%d", f); f = true; printf("%d", f);'
    assert run_c(wrap(body)) == [1, 0, 1]


def test_integer_type_aliases():
    src = ('#include <stdio.h>\ntypedef long long ll;\n#define LL long long\n'
           'int main() { ll a = 3; LL b = 4; printf("%lld", a * b); return 0; }')
    assert run_c(src) == [12]


def test_other_macros_are_refused_when_used():
    src = '#define N 5\nint main() { int x = N; printf("%d", x); return 0; }'
    with pytest.raises(CFrontendError, match="macro 'N'"):
        compile_c(src)
    unused = '#define N 5\nint main() { int x = 2; printf("%d", x); return 0; }'
    assert run_c(unused) == [2]


def test_c_style_cpp_is_read():
    src = ('#include <cstdio>\nusing namespace std;\n'
           'int main() { int a, b; scanf("%d%d", &a, &b); printf("%d\\n", a + b); return 0; }')
    assert run_c(src, {"in_a": 2, "in_b": 5}) == [7]


def test_i64_format_is_an_integer_format():
    assert run_c(wrap('long long n; scanf("%I64d", &n); printf("%I64d", n + 1);'), {"in_n": 41}) == [42]


# ---------------------------------------------------------------- strict mode
def test_printed_text_gets_one_code_per_distinct_text():
    body = ('int n; scanf("%d", &n); if (n % 2 == 0) puts("YES"); else printf("NO\\n"); '
            'if (n > 100) printf("YES");')
    tac, cprog = compile_c(wrap(body), strict=True)
    assert cprog.texts == {"YES": YES, "NO": NO}
    run = TACInterpreter().execute
    assert run(tac, {"in_n": 4}) == [YES]
    assert run(tac, {"in_n": 7}) == [NO]
    assert run(tac, {"in_n": 200}) == [YES, YES]


def test_text_and_values_keep_their_order():
    body = 'int x = 3; printf("Case #%d: %d%%\\n", 1, x);'
    tac, cprog = compile_c(wrap(body), strict=True)
    assert list(cprog.texts) == ["Case #", ":", "%"]
    assert TACInterpreter().execute(tac) == [TEXT_CODE_BASE, 1, TEXT_CODE_BASE + 1, 3, TEXT_CODE_BASE + 2]


def test_spaces_and_newlines_are_only_separators():
    body = "int a = 1, b = 2; printf(\"%d %d\\n\", a, b); printf(\"%d%c\", a, '\\n'); putchar('\\n'); putchar('x');"
    assert run_c(wrap(body)) == [1, 2, 1, ord("x")]


def test_without_strict_mode_text_is_still_ignored():
    body = 'int x = 3; printf("x = %d\\n", x); puts("done");'
    tac, cprog = compile_c(wrap(body))
    assert TACInterpreter().execute(tac) == [3]
    assert cprog.texts == {} and cprog.notes


def test_strict_mode_refuses_a_division_that_needs_short_circuit():
    body = 'int a, b; scanf("%d%d", &a, &b); if (b != 0 && a % b == 0) printf("%d", 1);'
    with pytest.raises(CFrontendError, match="short-circuit"):
        compile_c(wrap(body), strict=True)
    compile_c(wrap(body))                                   # the demo keeps its old behaviour
    compile_c(wrap('int a = 9; if (a > 1 && a % 3 == 0) printf("%d", 1);'), strict=True)


def test_a_program_with_text_output_is_optimized_and_stays_equivalent():
    body = ('int n, r = 0; scanf("%d", &n); int unused = n * 2; '
            'if (n % 2 == 0 && n > 2) { puts("YES"); return 0; } r = n + 0; printf("NO %d", r);')
    tac, _ = compile_c(wrap(body), strict=True)
    result = Orchestrator(max_iterations=100).optimize(tac, "watermelon.c")
    assert result.output_match and result.cost_reduction_pct > 0
    for n in (-3, 0, 2, 4, 7, 8):
        assert TACInterpreter().execute(result.optimized_tac, {"in_n": n}) == TACInterpreter().execute(tac, {"in_n": n})


# ---------------------------------------------------------------- categories and selection
def category(body):
    info, why = real_dataset.examine(wrap(body))
    assert info is not None, why
    return real_dataset.category_of(info)


def test_categories_follow_the_generator():
    read = 'int a, b; scanf("%d%d", &a, &b); '
    assert category(read + 'printf("%d", a + b - 1);') == "arithmetic"
    assert category(read + 'printf("%d", (a + b) * (a - 2) / 3);') == "nested"
    assert category(read + 'int s = a * b; printf("%d %d", s, a * b + 1);') == "repeated_expr"
    assert category(read + 'int spare = a * 7; printf("%d", a - b);') == "dead_code"
    assert category(read + 'int s = 0; for (int i = 0; i < 5; i++) s += a; printf("%d", s + b);') == "loops"
    assert category(read + 'if (a > b) printf("%d", a); else printf("%d", b);') == "conditionals"
    assert category(read + 'int s = b; for (int i = 0; i < 5; i++) { if (i > a) s++; } printf("%d", s);') == "mixed"


def test_a_dead_store_or_a_repeated_expression_decides_before_control_flow():
    read = 'int a, b; scanf("%d%d", &a, &b); '
    assert category(read + 'int spare = b; for (int i = 0; i < 5; i++) { if (i > a) a++; } printf("%d", a);') == "dead_code"
    assert category(read + 'if (a + b > 9) printf("%d", a + b); else printf("%d", 0);') == "repeated_expr"


def test_a_loop_counter_is_not_a_repeated_expression():
    body = ('int a; scanf("%d", &a); int s = 0; for (int i = 0; i < 3; i++) s += a; '
            'for (int j = 0; j < 3; j++) s += 2; printf("%d", s);')
    info, _ = real_dataset.examine(wrap(body))
    assert not info["repeated"]


@pytest.mark.parametrize("body,why", [
    ('int n; scanf("%d", &n); int a[5]; printf("%d", n);', "not in the accepted C subset"),
    ('int n; scanf("%d", &n); int s = 0; while (n != 1) { s++; } printf("%d", s);', "runs too long on a test input"),
    ('int n; scanf("%d", &n); int s = n * 2 + 1; s = s - n;', "prints nothing"),
])
def test_unusable_programs_are_turned_away(body, why):
    assert real_dataset.examine(wrap(body)) == (None, why)


def _candidate(number, problem, cat, created=0):
    feat = {"loop": cat in ("loops", "mixed"), "branch": cat in ("conditionals", "mixed"), "depth": 0,
            "dead": False, "repeated": False, "canonical": f"c{number}"}
    return {"submission_id": str(number), "problem_id": problem, "created": created, "features": feat}


def test_choice_fills_quotas_one_problem_at_a_time():
    cands = [_candidate(i, f"{i % 5}/A", "loops", created=i) for i in range(40)]
    cands += [_candidate(100 + i, "9/B", "mixed") for i in range(10)]
    chosen = real_dataset.choose(cands, {"loops": 12, "mixed": 4})
    per_problem = [sum(c["problem_id"] == f"{p}/A" for c in chosen["loops"]) for p in range(5)]
    assert len(chosen["loops"]) == 12 and sorted(per_problem) == [2, 2, 2, 3, 3]
    assert len(chosen["mixed"]) == 4
    # newest submission of each problem first
    assert {c["submission_id"] for c in chosen["loops"][:5]} == {"35", "36", "37", "38", "39"}
    assert chosen == real_dataset.choose(list(reversed(cands)), {"loops": 12, "mixed": 4})


def test_the_same_program_twice_counts_once():
    a, b = _candidate(1, "1/A", "loops"), _candidate(2, "2/A", "loops")
    b["features"]["canonical"] = a["features"]["canonical"]
    assert len(real_dataset.choose([a, b], {"loops": 5})["loops"]) == 1


def test_renamed_variables_give_the_same_canonical_form():
    one, _ = real_dataset.examine(wrap('int a, b; scanf("%d%d", &a, &b); printf("%d", a * b + a - 1);'))
    two, _ = real_dataset.examine(wrap('int x, y; scanf("%d%d", &x, &y); printf("%d", x * y + x - 1);'))
    three, _ = real_dataset.examine(wrap('int x, y; scanf("%d%d", &x, &y); printf("%d", x * y + y - 1);'))
    assert one["canonical"] == two["canonical"] != three["canonical"]


def test_the_proportions_are_the_generators():
    spec = importlib.util.spec_from_file_location("generator", os.path.join(ROOT, "dataset", "generator.py"))
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    assert real_dataset.CATEGORY_COUNTS == generator.CATEGORY_COUNTS
    assert sum(real_dataset.CATEGORY_COUNTS.values()) == 500
