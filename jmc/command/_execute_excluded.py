from ..exception import JMCSyntaxException, JMCTypeError
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack
from .utils import ArgType, find_scoreboard_player_type, verify_args
from ._flow_control import parse_switch

HARDCODE_REPEAT_ARG_TYPE = {
    "index_string": ArgType.string,
    "function": ArgType.arrow_func,
    "count": ArgType.integer,
    "start": ArgType.integer,
    "stop": ArgType.integer,
    "step": ArgType.integer
}


def hardcode_repeat(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(HARDCODE_REPEAT_ARG_TYPE,
                       "Hardcode.repeat", token, tokenizer)

    if args["index_string"] is None:
        raise JMCTypeError("index_string", token, tokenizer)
    else:
        index_string = args["index_string"].token.string

    if args["function"] is None:
        raise JMCTypeError("function", token, tokenizer)

    if args["start"] is None:
        start = 0
    else:
        start = int(args["start"].token.string)

    if args["stop"] is None:
        raise JMCTypeError("stop", token, tokenizer)
    else:
        stop = int(args["stop"].token.string)

    if args["step"] is None:
        step = 1
    else:
        step = int(args["step"].token.string)
        if step == 0:
            raise JMCSyntaxException(
                "'step' must not be zero", args["step"].token, tokenizer)

    code = datapack.parse_function_token(
        args["function"].token, tokenizer)

    commands: list[str] = []
    for i in range(start, stop, step):
        commands.extend(line.replace(index_string, str(i)) for line in code)

    return "\n".join(commands)

# TODO: Implement Hardcode.calc()


HARDCODE_SWITCH_ARG_TYPE = {
    "switch": ArgType.scoreboard,
    "index_string": ArgType.string,
    "function": ArgType.arrow_func,
    "count": ArgType.integer
}


def hardcode_switch(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(HARDCODE_SWITCH_ARG_TYPE,
                       "Hardcode.switch", token, tokenizer)

    if args["switch"] is None:
        raise JMCTypeError("switch", token, tokenizer)
    else:
        scoreboard_player = find_scoreboard_player_type(
            args["switch"].token, tokenizer)

    if args["index_string"] is None:
        raise JMCTypeError("index_string", token, tokenizer)
    else:
        index_string = args["index_string"].token.string

    if args["function"] is None:
        raise JMCTypeError("function", token, tokenizer)

    if args["count"] is None:
        raise JMCTypeError("count", token, tokenizer)
    else:
        count = int(args["count"].token.string)

    code = datapack.parse_function_token(
        args["function"].token, tokenizer)

    func_contents: list[list[str]] = []
    for i in range(count):
        func_contents.append(line.replace(index_string, str(i))
                             for line in code)

    return parse_switch(scoreboard_player, func_contents, datapack, name="hardcode_switch")
