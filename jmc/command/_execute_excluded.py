from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack
from .utils import ArgType, verify_args


HARDCODE_REPEAT_ARG_TYPE = {
    "index_string": ArgType.string,
    "function": ArgType.arrow_func
}


def hardcode_repeat(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(HARDCODE_REPEAT_ARG_TYPE,
                       "Hardcode.repeat", token, tokenizer)
    return "hardcode_repeat"+str(args)


HARDCODE_SWITCH_ARG_TYPE = {
    "switch": ArgType.scoreboard,
    "index_string": ArgType.string,
    "function": ArgType.arrow_func,
    "count": ArgType.integer
}


def hardcode_switch(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(HARDCODE_SWITCH_ARG_TYPE,
                       "Hardcode.switch", token, tokenizer)
    return f"""TEST
{args["switch"].string}
{args["index_string"].string}

{datapack.parse_function_token(args["function"], tokenizer)}

{args["count"].string}
"""
