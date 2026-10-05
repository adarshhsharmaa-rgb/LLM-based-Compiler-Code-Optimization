"""AST node definitions for the mini-language."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ASTNode:
    pass


@dataclass
class Statement(ASTNode):
    pass


@dataclass
class Expression(ASTNode):
    pass


@dataclass
class Program(ASTNode):
    statements: list[Statement] = field(default_factory=list)


# ---------------------------------------------------------------- statements
@dataclass
class VarDecl(Statement):
    name: str
    init_expr: Expression | None = None


@dataclass
class Assignment(Statement):
    target: str
    value: Expression


@dataclass
class IfStmt(Statement):
    condition: Expression
    then_body: list[Statement]
    else_body: list[Statement] | None = None


@dataclass
class WhileStmt(Statement):
    condition: Expression
    body: list[Statement]


@dataclass
class ForStmt(Statement):
    init: Statement
    condition: Expression
    update: Statement
    body: list[Statement]


@dataclass
class PrintStmt(Statement):
    value: Expression


# --------------------------------------------------------------- expressions
@dataclass
class BinaryExpr(Expression):
    op: str
    left: Expression
    right: Expression


@dataclass
class UnaryExpr(Expression):
    op: str
    operand: Expression


@dataclass
class NumberLit(Expression):
    value: int


@dataclass
class VarRef(Expression):
    name: str
