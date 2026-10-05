"""AST -> Three-Address Code translation.

The translation is intentionally naive (every literal is first loaded into a
temporary, every expression result lands in a fresh temporary). That leaves
plenty of redundancy for the optimisation agents to remove.

Notes:
  * ``int x;`` without an initialiser is emitted as ``x = 0``.
  * ``&&`` and ``||`` evaluate both operands (there is no short-circuiting).
  * Temporary names never collide with user identifiers: a candidate name
    ``tN`` that the program already uses is skipped.
"""
from __future__ import annotations

from ..tac.instruction import TACInstruction, TACOp
from ..tac.program import TACProgram
from .ast_nodes import (
    Assignment,
    BinaryExpr,
    Expression,
    ForStmt,
    IfStmt,
    NumberLit,
    PrintStmt,
    Program,
    Statement,
    UnaryExpr,
    VarDecl,
    VarRef,
    WhileStmt,
)


def _collect_identifiers(node, out: set[str]) -> None:
    if isinstance(node, list):
        for item in node:
            _collect_identifiers(item, out)
        return
    if isinstance(node, VarRef):
        out.add(node.name)
    elif isinstance(node, VarDecl):
        out.add(node.name)
    elif isinstance(node, Assignment):
        out.add(node.target)
    if hasattr(node, "__dataclass_fields__"):
        for name in node.__dataclass_fields__:
            child = getattr(node, name)
            if isinstance(child, (list, Statement, Expression)):
                _collect_identifiers(child, out)


class TACGenerator:
    def __init__(self) -> None:
        self._temp_counter = 0
        self._label_counter = 0
        self._instructions: list[TACInstruction] = []
        self._reserved: set[str] = set()

    def generate(self, program: Program) -> TACProgram:
        self._temp_counter = 0
        self._label_counter = 0
        self._instructions = []
        self._reserved = set()
        _collect_identifiers(program.statements, self._reserved)
        for stmt in program.statements:
            self._gen_statement(stmt)
        return TACProgram(self._instructions)

    # ------------------------------------------------------------ helpers
    def _new_temp(self) -> str:
        while True:
            name = f"t{self._temp_counter}"
            self._temp_counter += 1
            if name not in self._reserved:
                return name

    def _new_label(self) -> str:
        name = f"L{self._label_counter}"
        self._label_counter += 1
        return name

    def _emit(self, ins: TACInstruction) -> None:
        self._instructions.append(ins)

    # --------------------------------------------------------- statements
    def _gen_statement(self, stmt: Statement) -> None:
        match stmt:
            case VarDecl(name=name, init_expr=init):
                value = self._gen_expr(init) if init is not None else "0"
                self._emit(TACInstruction(TACOp.ASSIGN, result=name, arg1=value))
            case Assignment(target=target, value=value_expr):
                value = self._gen_expr(value_expr)
                self._emit(TACInstruction(TACOp.ASSIGN, result=target, arg1=value))
            case PrintStmt(value=value_expr):
                value = self._gen_expr(value_expr)
                self._emit(TACInstruction(TACOp.PRINT, arg1=value))
            case IfStmt():
                self._gen_if(stmt)
            case WhileStmt():
                self._gen_while(stmt)
            case ForStmt():
                self._gen_for(stmt)
            case _:
                raise TypeError(f"Unknown statement node: {type(stmt).__name__}")

    def _gen_block(self, body: list[Statement]) -> None:
        for s in body:
            self._gen_statement(s)

    def _gen_if(self, stmt: IfStmt) -> None:
        cond = self._gen_expr(stmt.condition)
        if stmt.else_body is not None:
            l_else = self._new_label()
            l_end = self._new_label()
            self._emit(TACInstruction(TACOp.IF_FALSE_GOTO, arg1=cond, label=l_else))
            self._gen_block(stmt.then_body)
            self._emit(TACInstruction(TACOp.GOTO, label=l_end))
            self._emit(TACInstruction(TACOp.LABEL, label=l_else))
            self._gen_block(stmt.else_body)
            self._emit(TACInstruction(TACOp.LABEL, label=l_end))
        else:
            l_end = self._new_label()
            self._emit(TACInstruction(TACOp.IF_FALSE_GOTO, arg1=cond, label=l_end))
            self._gen_block(stmt.then_body)
            self._emit(TACInstruction(TACOp.LABEL, label=l_end))

    def _gen_while(self, stmt: WhileStmt) -> None:
        l_start = self._new_label()
        l_end = self._new_label()
        self._emit(TACInstruction(TACOp.LABEL, label=l_start))
        cond = self._gen_expr(stmt.condition)
        self._emit(TACInstruction(TACOp.IF_FALSE_GOTO, arg1=cond, label=l_end))
        self._gen_block(stmt.body)
        self._emit(TACInstruction(TACOp.GOTO, label=l_start))
        self._emit(TACInstruction(TACOp.LABEL, label=l_end))

    def _gen_for(self, stmt: ForStmt) -> None:
        self._gen_statement(stmt.init)
        l_start = self._new_label()
        l_end = self._new_label()
        self._emit(TACInstruction(TACOp.LABEL, label=l_start))
        cond = self._gen_expr(stmt.condition)
        self._emit(TACInstruction(TACOp.IF_FALSE_GOTO, arg1=cond, label=l_end))
        self._gen_block(stmt.body)
        self._gen_statement(stmt.update)
        self._emit(TACInstruction(TACOp.GOTO, label=l_start))
        self._emit(TACInstruction(TACOp.LABEL, label=l_end))

    # -------------------------------------------------------- expressions
    def _gen_expr(self, expr: Expression) -> str:
        match expr:
            case NumberLit(value=v):
                t = self._new_temp()
                self._emit(TACInstruction(TACOp.ASSIGN, result=t, arg1=str(v)))
                return t
            case VarRef(name=name):
                return name
            case BinaryExpr(op=op, left=left, right=right):
                a = self._gen_expr(left)
                b = self._gen_expr(right)
                t = self._new_temp()
                self._emit(TACInstruction(TACOp.BINARY, result=t, arg1=a, operator=op, arg2=b))
                return t
            case UnaryExpr(op=op, operand=operand):
                a = self._gen_expr(operand)
                t = self._new_temp()
                self._emit(TACInstruction(TACOp.UNARY, result=t, operator=op, arg1=a))
                return t
        raise TypeError(f"Unknown expression node: {type(expr).__name__}")
