from ..exception import JMCTypeError
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack
from .utils import ArgType, find_scoreboard_player_type, verify_args


def right_click_setup(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "right_click_setup"+str(token)


PLAYER_ON_EVENT_ARG_TYPE = {
    "objective": ArgType.keyword,
    "function": ArgType.func,
}

player_on_event_name = 'on_event'


def player_on_event(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(PLAYER_ON_EVENT_ARG_TYPE,
                       "Player.onEvent", token, tokenizer)

    if args["objective"] is None:
        raise JMCTypeError("objective", token, tokenizer)
    obj = args["objective"].token.string

    if args["function"] is None:
        raise JMCTypeError("function", token, tokenizer)

    count = datapack.get_count(player_on_event_name)
    base_func = datapack.add_raw_private_function(
        player_on_event_name, [f"scoreboard players reset @s {obj}"], count=count)

    datapack.ticks.append(
        f"execute as @a[scores={{{obj}=1..}}] at @s run {base_func}")

    if args["function"].arg_type == ArgType._func_call:
        datapack.private_functions[player_on_event_name][count].append(
            f"function {datapack.namespace}:{args['function'].token.string.lower().replace('.', '/')}"
        )
    else:
        datapack.private_functions[player_on_event_name][count].extend(
            datapack.parse_function_token(args['function'].token, tokenizer)
        )

    return ""


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
