from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack


def timer_set(token: Token, datapack: DataPack, tokenizer: Tokenizer, is_execute: bool) -> str:
    return "timer_set"+str(token)


def math_sqrt(token: Token, datapack: DataPack, tokenizer: Tokenizer, is_execute: bool) -> str:
    return "math_sqrt"+str(token)


def math_random(token: Token, datapack: DataPack, tokenizer: Tokenizer, is_execute: bool) -> str:
    return "math_random"+str(token)
