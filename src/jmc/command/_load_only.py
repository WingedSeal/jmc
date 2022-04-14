from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack


def right_click_setup(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "right_click_setup"+str(token)


def player_on_event(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "player_on_event"+str(token)


def trigger_setup(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "trigger_setup"+str(token)


def timer_add(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "timer_add"+str(token)


def recipe_table(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "recipe_table"+str(token)


def debug_track(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "debug_track"+str(token)


def debug_history(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "debug_history"+str(token)


def debug_cleanup(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "debug_cleanup"+str(token)
