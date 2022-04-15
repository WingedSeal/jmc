from ..exception import JMCTypeError
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack
from .utils import ArgType, verify_args

TIMER_IS_OVER_ARG_TYPE = {
    "objective": ArgType.keyword,
    "selector": ArgType.selector
}


def timer_is_over(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(TIMER_IS_OVER_ARG_TYPE,
                       "Player.die", token, tokenizer)
    return "timer_is_over"
