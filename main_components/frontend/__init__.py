from .lexer import Lexer, LexerError, Token, TokenType
from .parser import ParseError, Parser
from .tac_generator import TACGenerator


def compile_source(source: str):
    """Lex, parse and lower a source string to a TACProgram."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    return TACGenerator().generate(ast)


__all__ = ["Lexer", "LexerError", "Token", "TokenType", "Parser", "ParseError",
           "TACGenerator", "compile_source"]
