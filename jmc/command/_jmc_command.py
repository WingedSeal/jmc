from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack


def timer_set(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer, is_execute: bool) -> str:
    return "timer_set"+str(arguments)


def math_sqrt(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer, is_execute: bool) -> str:
    return "math_sqrt"+str(arguments)


def math_random(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer, is_execute: bool) -> str:
    return "math_random"+str(arguments)
