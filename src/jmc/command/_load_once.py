from ..exception import JMCTypeError
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack
from .utils import ArgType, verify_args

PLAYER_FIRST_JOIN_ARG_TYPE = {
    "function": ArgType.func,
}
PLAYER_FIRST_JOIN_NAME = 'player_first_join'


def player_first_join(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(PLAYER_FIRST_JOIN_ARG_TYPE,
                       "Player.die", token, tokenizer)
    if args["function"] is None:
        raise JMCTypeError("function", token, tokenizer)

    if args["function"].arg_type == ArgType._func_call:
        datapack.add_private_json("advancements", PLAYER_FIRST_JOIN_NAME, {
            "criteria": {
                "requirement": {
                    "trigger": "minecraft:tick"
                }
            },
            "rewards": {
                "function": f"{datapack.namespace}:{args['function'].token.string}"
            }
        })
    else:
        datapack.add_custom_private_function(
            'player', args['function'].token, tokenizer, PLAYER_FIRST_JOIN_NAME)
        datapack.add_private_json("advancements", PLAYER_FIRST_JOIN_NAME, {
            "criteria": {
                "requirement": {
                    "trigger": "minecraft:tick"
                }
            },
            "rewards": {
                "function": f"{datapack.namespace}:{DataPack.PRIVATE_NAME}/player/{PLAYER_FIRST_JOIN_NAME}"
            }
        })

    return ""


def player_rejoin(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "player_rejoin"+str(token)


PLAYER_DIE_ARG_TYPE = {
    "onDeath": ArgType.func,
    "onRespawn": ArgType.func,
}
PLAYER_DIE_OBJ = '__die__'
PLAYER_DIE_NAME = 'player_die'
PLAYER_DIE_ON_DEATH = f'scoreboard players set @s {PLAYER_DIE_OBJ} 2'
PLAYER_DIE_ON_RESPAWN = f'scoreboard players reset @s {PLAYER_DIE_OBJ}'


def player_die(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(PLAYER_DIE_ARG_TYPE,
                       "Player.die", token, tokenizer)

    if args["onDeath"] is None and args["onRespawn"] is None:
        raise JMCTypeError("onDeath or onRespawn", token, tokenizer)

    datapack.loads.append(
        f'scoreboard objectives add {PLAYER_DIE_OBJ} deathCount')
    datapack.ticks.append(
        f'execute as @a[scores={{{PLAYER_DIE_OBJ}=1..}}] at @s run function {datapack.namespace}:{DataPack.PRIVATE_NAME}/{PLAYER_DIE_NAME}/on_death')
    datapack.ticks.append(
        f'execute as @e[type=player,scores={{{PLAYER_DIE_OBJ}=2..}}] at @s run function {datapack.namespace}:{DataPack.PRIVATE_NAME}/{PLAYER_DIE_NAME}/on_respawn')

    if args["onDeath"] is None:
        datapack.add_raw_private_function(
            PLAYER_DIE_NAME, [PLAYER_DIE_ON_DEATH], "on_death")
    elif args["onDeath"].arg_type == ArgType._func_call:
        datapack.add_raw_private_function(
            PLAYER_DIE_NAME, [
                PLAYER_DIE_ON_DEATH,
                f"function {datapack.namespace}:{args['onDeath'].token.string.lower().replace('.', '/')}"
            ], "on_death")
    else:
        datapack.add_custom_private_function(
            PLAYER_DIE_NAME,
            args["onDeath"].token,
            tokenizer,
            "on_death",
            precommands=[PLAYER_DIE_ON_DEATH]
        )

    if args["onRespawn"] is None:
        datapack.add_raw_private_function(
            PLAYER_DIE_NAME, [PLAYER_DIE_ON_RESPAWN], "on_respawn")
    elif args["onRespawn"].arg_type == ArgType._func_call:
        datapack.add_raw_private_function(
            PLAYER_DIE_NAME, [
                PLAYER_DIE_ON_RESPAWN,
                f"function {datapack.namespace}:{args['onRespawn'].token.string.lower().replace('.', '/')}"
            ], "on_respawn")
    else:
        datapack.add_custom_private_function(
            PLAYER_DIE_NAME,
            args["onRespawn"].token,
            tokenizer,
            "on_respawn",
            precommands=[PLAYER_DIE_ON_RESPAWN]
        )
    return ""
