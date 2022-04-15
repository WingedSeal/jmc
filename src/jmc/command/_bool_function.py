from ..exception import JMCTypeError
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack
from .utils import ArgType, verify_args

IF = True
UNLESS = False

TIMER_IS_OVER_ARG_TYPE = {
    "objective": ArgType.keyword,
    "selector": ArgType.selector
}


def timer_is_over(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> tuple[str, bool]:
    args = verify_args(TIMER_IS_OVER_ARG_TYPE,
                       "Timer.isOver", token, tokenizer)
    if args["objective"] is None:
        raise JMCTypeError("objective", token, tokenizer)
    if args["selector"] is None:
        selector = '@s'
    else:
        selector = args["selector"].token.string
    return f'score {selector} {args["objective"].token.string} matches 1..', UNLESS
