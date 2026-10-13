"""Tests for the C-subset front-end used by the live demo (demo.py)."""
import glob
import os

import pytest

from src.agents.orchestrator import Orchestrator
from src.frontend.c_frontend import CFrontendError, compile_c, parse_c
from src.tac.interpreter import TACInterpreter


def run_c(source, inputs=None):
    tac, _ = compile_c(source)
    return TACInterpreter().execute(tac, inputs)


def wrap(body):
    return "#include <stdio.h>\nint main() {\n" + body + "\nreturn 0;\n}\n"


def test_minimal_program():
    assert run_c(wrap('printf("%d\\n", 3 + 4 * 2);')) == [11]


def test_include_and_comments_are_ignored():
    src = '#include <stdio.h>\n#include <stdlib.h>\n// c1\nint main(void) { /* c2 */ printf("%d", 1); return 0; }'
    assert run_c(src) == [1]


def test_multiple_declarations_in_one_statement():
    assert run_c(wrap('int a = 2, b, c = a + 5; b = c * 2; printf("%d %d %d", a, b, c);')) == [2, 14, 7]


def test_compound_assignment_and_increment():
    body = 'int x = 10; x += 5; x -= 3; x *= 2; x /= 4; x %= 4; x++; ++x; x--; printf("%d", x);'
    assert run_c(wrap(body)) == [3]          # ((10+5-3)*2/4) % 4 = 2, then +1 +1 -1


def test_if_else_if_else_without_braces():
    body = ('int x = {v}; if (x > 10) printf("%d", 1); else if (x > 5) printf("%d", 2); '
            'else printf("%d", 3);')
    assert run_c(wrap(body.replace("{v}", "20"))) == [1]
    assert run_c(wrap(body.replace("{v}", "7"))) == [2]
    assert run_c(wrap(body.replace("{v}", "1"))) == [3]


def test_for_loop_matches_c_semantics():
    assert run_c(wrap('int s = 0; for (int i = 1; i <= 5; i++) { s += i * i; } printf("%d", s);')) == [55]


def test_for_with_empty_parts_and_two_updates():
    body = 'int i = 0, j = 10; for (; i < j; i++, j--) ; printf("%d %d", i, j);'
    assert run_c(wrap(body)) == [5, 5]


def test_nested_loops_and_while():
    body = ('int c = 0; int i = 0; while (i < 3) { for (int j = 0; j < 4; j++) c++; i++; } '
            'printf("%d", c);')
    assert run_c(wrap(body)) == [12]


def test_operator_precedence_and_logic():
    assert run_c(wrap('printf("%d", 2 + 3 * 4 - 10 / 3 % 2);')) == [13]      # 10/3=3, 3%2=1
    assert run_c(wrap('printf("%d %d", 1 < 2 && 3 > 4 || !0, -(3 - 5));')) == [1, 2]
    assert run_c(wrap('printf("%d", -7 / 2);')) == [-3]                       # truncates like C


def test_scanf_makes_program_inputs():
    src = wrap('int n; scanf("%d", &n); printf("%d", n * 2);')
    tac, cprog = compile_c(src)
    assert cprog.inputs == [("in_n", "n")]
    assert tac.get_input_variables() == {"in_n"}
    assert TACInterpreter().execute(tac, {"in_n": 21}) == [42]


def test_scanf_two_variables():
    src = wrap('int a, b; scanf("%d %d", &a, &b); printf("%d", a - b);')
    assert run_c(src, {"in_a": 9, "in_b": 4}) == [5]


def test_printf_text_is_ignored_with_a_note():
    cprog = parse_c(wrap('int x = 4; printf("x is %d and twice is %d\\n", x, x * 2);'))
    assert any("text inside printf is ignored" in n for n in cprog.notes)
    assert run_c(wrap('int x = 4; printf("x is %d and twice is %d\\n", x, x * 2);')) == [4, 8]


def test_bare_snippet_without_main():
    assert run_c('int a = 6; int b = a * 7; printf("%d", b);') == [42]


def test_global_declaration_before_main():
    assert run_c('int g = 5;\nint main() { printf("%d", g + 1); return 0; }') == [6]


@pytest.mark.parametrize("body,fragment", [
    ("float f = 1.5;", "floating-point"),
    ("char c;", "type 'char' is not supported"),
    ("int a[10];", "arrays are not supported"),
    ("int *p;", "pointers are not supported"),
    ("int x = 1; while (x) { break; }", "'break' is not supported"),
    ("int x = foo(3);", "calling function 'foo'"),
    ("int x = 1; int y = x++;", "inside an expression"),
    ("int x = 5 & 3;", "bitwise operator"),
    ("int x = 1 ? 2 : 3;", "ternary"),
    ('printf("%f", 1);', "only %d"),
    ('printf("%d %d", 1);', "expected ','"),
    ("int x = 1; while (x < 3) { scanf(\"%d\", &x); }", "scanf inside a loop"),
    ("int x = 5", "expected ';'"),
    ("int a; int b; a = b = 3;", "chained assignment"),
])
def test_unsupported_c_gives_clear_error(body, fragment):
    with pytest.raises(CFrontendError) as exc:
        compile_c(wrap(body))
    assert fragment in str(exc.value)
    assert "line" in str(exc.value)


def test_other_functions_are_rejected():
    with pytest.raises(CFrontendError, match="only main"):
        compile_c("int helper(int a) { return a; }\nint main() { return 0; }")


def test_error_reports_the_right_line():
    with pytest.raises(CFrontendError) as exc:
        compile_c("#include <stdio.h>\nint main() {\n  int a = 1;\n  int b[3];\n}")
    assert exc.value.line == 4


def test_c_program_optimizes_and_stays_correct():
    src = wrap('int n; scanf("%d", &n); int a = n * 3 + 10; int b = n * 3 + 10; '
               'int dead = a - a; printf("%d", (a + b) * (2 + 6));')
    tac, _ = compile_c(src)
    result = Orchestrator(max_iterations=200).optimize(tac)
    assert result.output_match and result.cost_reduction_pct > 50
    assert "CSE" in result.optimization_types_applied
    for n in (-4, 0, 9):
        assert TACInterpreter().execute(result.optimized_tac, {"in_n": n}) == [(2 * (n * 3 + 10)) * 8]


# ------------------------------------------------------------- C scoping
def test_inner_block_variable_does_not_overwrite_outer_one():
    # In C the inner x is a different variable, so the program prints 1 (and 5 inside).
    body = 'int x = 1; if (x) { int x = 5; printf("%d", x); } printf("%d", x);'
    assert run_c(wrap(body)) == [5, 1]


def test_assignment_before_inner_declaration_hits_the_outer_variable():
    body = 'int x = 1; { x = 2; int x = 3; x = 4; printf("%d", x); } printf("%d", x);'
    assert run_c(wrap(body)) == [4, 2]


def test_nested_loops_may_reuse_the_same_counter_name():
    body = ('int c = 0; for (int i = 0; i < 3; i++) { for (int i = 0; i < 4; i++) { c++; } } '
            'printf("%d", c);')
    assert run_c(wrap(body)) == [12]


def test_for_variable_is_not_visible_after_the_loop():
    with pytest.raises(CFrontendError, match="'i' is not declared"):
        compile_c(wrap('for (int i = 0; i < 3; i++) { } printf("%d", i);'))


def test_sibling_loops_can_each_declare_i():
    body = ('int s = 0; for (int i = 0; i < 3; i++) s += i; for (int i = 0; i < 4; i++) s += i; '
            'printf("%d", s);')
    assert run_c(wrap(body)) == [9]


def test_undeclared_variable_is_an_error():
    with pytest.raises(CFrontendError, match="'total' is not declared") as exc:
        compile_c("int main() {\n  int sum = 1;\n  total = sum + 1;\n  return 0;\n}")
    assert exc.value.line == 3


def test_redeclaration_in_the_same_scope_is_an_error():
    with pytest.raises(CFrontendError, match="already declared"):
        compile_c(wrap("int a = 1; int a = 2;"))


def test_local_variable_may_shadow_a_global():
    assert run_c('int g = 5;\nint main() { int g = 7; printf("%d", g); return 0; }') == [7]


def test_scanf_twice_reads_two_separate_inputs():
    src = wrap('int n; scanf("%d", &n); int a = n; scanf("%d", &n); printf("%d %d", a, n);')
    tac, cprog = compile_c(src)
    assert [name for name, _ in cprog.inputs] == ["in_n", "in_n_2"]
    assert TACInterpreter().execute(tac, {"in_n": 3, "in_n_2": 8}) == [3, 8]


def test_literal_percent_in_printf():
    assert run_c(wrap('int p = 40; printf("%d%% done\\n", p);')) == [40]


def test_all_bundled_demo_programs_work():
    folder = os.path.join(os.path.dirname(__file__), "..", "demo_programs")
    files = sorted(glob.glob(os.path.join(folder, "*.c")))
    assert files, "demo_programs/ should contain sample C files"
    for path in files:
        with open(path, encoding="utf-8") as fh:
            tac, _ = compile_c(fh.read())
        result = Orchestrator(max_iterations=200).optimize(tac)
        assert result.output_match, path
        assert result.cost_reduction_pct > 30, path
