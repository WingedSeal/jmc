from typing import Callable

from ._jmc_command import (
    timer_set,
    math_sqrt,
    math_random
)
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack

JMC_COMMANDS: dict[str, Callable[
    [
        tuple[list[Token], dict[str, Token]],
        DataPack,
        Tokenizer,
        bool
    ], str]] = {

    'Timer.set': timer_set,
}
