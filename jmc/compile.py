from .lexer import Lexer
from time import sleep


def compile(config: dict[str, str]) -> None:
    lexer = Lexer(config)
    print("SIMULATING COMPILING")
    sleep(3)
    print("DONE")
