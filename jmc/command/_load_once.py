from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack


def player_first_join(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "player_first_join"+str(arguments)


def player_rejoin(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "player_rejoin"+str(arguments)


def player_die(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "player_die"+str(arguments)
