from ..exception import JMCTypeError
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack
from .utils import ArgType, verify_args, find_scoreboard_player_type, PlayerType

TIMER_SET_ARG_TYPE = {
    "objective": ArgType.keyword,
    "target_selector": ArgType.selector,
    "tick": ArgType.scoreboard_player
}


def timer_set(token: Token, datapack: DataPack, tokenizer: Tokenizer, is_execute: bool) -> str:
    args = verify_args(TIMER_SET_ARG_TYPE,
                       "Timer.set", token, tokenizer)
    if args["objective"] is None:
        raise JMCTypeError("objective", token, tokenizer)
    if args["target_selector"] is None:
        raise JMCTypeError("target_selector", token, tokenizer)
    if args["tick"] is None:
        raise JMCTypeError("tick", token, tokenizer)

    scoreboard_player = find_scoreboard_player_type(
        args["tick"].token, tokenizer)
    if scoreboard_player.player_type == PlayerType.integer:
        return f'scoreboard players set {args["target_selector"].token.string} {args["objective"].token.string} {scoreboard_player.value}'
    else:
        return f'scoreboard players operation {args["target_selector"].token.string} {args["objective"].token.string} = {scoreboard_player.value[1]} {scoreboard_player.value[0]}'


def math_sqrt(token: Token, datapack: DataPack, tokenizer: Tokenizer, is_execute: bool) -> str:
    return "math_sqrt"+str(token)


def math_random(token: Token, datapack: DataPack, tokenizer: Tokenizer, is_execute: bool) -> str:
    return "math_random"+str(token)
