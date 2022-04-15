from typing import Callable

from ._bool_function import (
    timer_is_over
)
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack

BOOL_FUNCTIONS: dict[str, Callable[
    [
        Token,
        DataPack,
        Tokenizer,
        bool
    ], tuple[str, bool]]] = {

    'Timer.isOver': timer_is_over,
}
