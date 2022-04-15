from json import JSONDecodeError, loads, dumps

from ..exception import JMCDecodeJSONError, JMCSyntaxException, JMCTypeError
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack
from .utils import ArgType, verify_args


def right_click_setup(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "right_click_setup"+str(token)


PLAYER_ON_EVENT_ARG_TYPE = {
    "objective": ArgType.keyword,
    "function": ArgType.func,
}

PLAYER_ON_EVENT_NAME = 'player_on_event'


def player_on_event(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(PLAYER_ON_EVENT_ARG_TYPE,
                       "Player.onEvent", token, tokenizer)

    if args["objective"] is None:
        raise JMCTypeError("objective", token, tokenizer)
    obj = args["objective"].token.string

    if args["function"] is None:
        raise JMCTypeError("function", token, tokenizer)

    count = datapack.get_count(PLAYER_ON_EVENT_NAME)
    base_func = datapack.add_raw_private_function(
        PLAYER_ON_EVENT_NAME, [f"scoreboard players reset @s {obj}"], count=count)

    datapack.ticks.append(
        f"execute as @a[scores={{{obj}=1..}}] at @s run {base_func}")

    if args["function"].arg_type == ArgType._func_call:
        datapack.private_functions[PLAYER_ON_EVENT_NAME][count].append(
            f"function {datapack.namespace}:{args['function'].token.string.lower().replace('.', '/')}"
        )
    else:
        datapack.private_functions[PLAYER_ON_EVENT_NAME][count].extend(
            datapack.parse_function_token(args['function'].token, tokenizer)
        )

    return ""


def trigger_setup(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "trigger_setup"+str(token)


def timer_add(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "timer_add"+str(token)


RECIPE_TABLE_ARG_TYPE = {
    "recipe": ArgType.json,
    "baseItem": ArgType.keyword,
    "onCraft": ArgType.func
}
RECIPE_TABLE_NAME = 'recipe_table'


def recipe_table(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(RECIPE_TABLE_ARG_TYPE,
                       "Recipe.table", token, tokenizer)

    if args["recipe"] is None:
        raise JMCTypeError("recipe", token, tokenizer)
    if args["baseItem"] is None:
        base_item = 'minecraft:knowledge_book'
    else:
        base_item = args["baseItem"].token.string
        if not base_item.startswith("minecraft:"):
            base_item = 'minecraft:'+base_item

    if args["onCraft"] is None:
        func = ""
    elif args["onCraft"].arg_type == ArgType._func_call:
        func = f"function {datapack.namespace}:{args['onCraft'].token.string.lower().replace('.', '/')}"
    else:
        func = '\n'.join(datapack.parse_function_token(
            args["onCraft"].token, tokenizer))

    count = datapack.get_count(RECIPE_TABLE_NAME)
    datapack.add_private_json('advancements', f'{RECIPE_TABLE_NAME}/{count}', {
        "criteria": {
            "requirement": {
                "trigger": "minecraft:recipe_unlocked",
                "conditions": {
                    "recipe": f"{datapack.namespace}:{DataPack.PRIVATE_NAME}/{RECIPE_TABLE_NAME}/{count}"
                }
            }
        },
        "rewards": {
            "function": f"{datapack.namespace}:{DataPack.PRIVATE_NAME}/{RECIPE_TABLE_NAME}/{count}"
        }
    })

    try:
        json = loads(args["recipe"].token.string)
    except JSONDecodeError as error:
        raise JMCDecodeJSONError(error, args["recipe"].token, tokenizer)

    if "result" not in json:
        raise JMCSyntaxException("'result' key not found in recipe",
                                 args["recipe"].token, tokenizer, display_col_length=True, suggestion="recipe json maybe invalid")
    if "item" not in json["result"]:
        raise JMCSyntaxException("'item' key not found in 'result' in recipe",
                                 args["recipe"].token, tokenizer, display_col_length=True, suggestion="recipe json maybe invalid")
    if "count" not in json["result"]:
        raise JMCSyntaxException("'count' key not found in 'result' in recipe",
                                 args["recipe"].token, tokenizer, display_col_length=True, suggestion="recipe json maybe invalid")
    result_item = json["result"]["item"]
    json["result"]["item"] = base_item
    result_count = json["result"]["count"]
    json["result"]["count"] = 1

    datapack.add_private_json('recipes', f'{RECIPE_TABLE_NAME}/{count}', json)
    datapack.add_raw_private_function(
        RECIPE_TABLE_NAME,
        [
            f"clear @s {base_item} 1",
            f"give @s {result_item} {result_count}",
            f"recipe take @s {datapack.namespace}:{DataPack.PRIVATE_NAME}/{RECIPE_TABLE_NAME}/{count}",
            f"advancement revoke @s only {datapack.namespace}:{DataPack.PRIVATE_NAME}/{RECIPE_TABLE_NAME}/{count}",
            func
        ],
        count
    )
    return ""


def debug_track(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "debug_track"+str(token)


def debug_history(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "debug_history"+str(token)


def debug_cleanup(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "debug_cleanup"+str(token)
