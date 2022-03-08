from .lexer import Lexer


def compile(config: dict[str, str]) -> None:
    lexer = Lexer(config)
