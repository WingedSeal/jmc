from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack


def hardcode_repeat(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "hardcode_repeat"+str(arguments)


def hardcode_switch(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "hardcode_switch"+str(arguments)
