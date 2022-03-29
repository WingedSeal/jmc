from typing import Callable

from ._execute_excluded import (
    hardcode_repeat,
    hardcode_switch
)
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack

EXECUTE_EXCLUDED_COMMANDS: dict[str, Callable[
    [
        tuple[list[Token], dict[str, Token]],
        DataPack,
        Tokenizer,
    ], str]] = {

    'Hardcode.repeat': hardcode_repeat,
    'Hardcode.switch': hardcode_switch,
}
