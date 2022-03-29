from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack


def right_click_setup(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "right_click_setup"+str(arguments)


def player_on_event(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "player_on_event"+str(arguments)


def trigger_setup(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "trigger_setup"+str(arguments)


def timer_add(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "timer_add"+str(arguments)


def recipe_table(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "recipe_table"+str(arguments)


def debug_track(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "debug_track"+str(arguments)


def debug_history(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "debug_history"+str(arguments)


def debug_cleanup(arguments: tuple[list[Token], dict[str, Token]], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "debug_cleanup"+str(arguments)
