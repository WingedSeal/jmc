from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack


def player_first_join(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "player_first_join"+str(token)


def player_rejoin(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "player_rejoin"+str(token)


def player_die(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "player_die"+str(token)
