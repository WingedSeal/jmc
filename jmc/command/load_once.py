from typing import Callable

from ._load_once import (
    player_first_join,
    player_rejoin,
    player_die
)
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack

LOAD_ONCE_COMMANDS: dict[str, Callable[
    [
        Token,
        DataPack,
        Tokenizer,
    ], str]] = {

    'Player.firstJoin': player_first_join,
    'Player.rejoin': player_rejoin,
    'Player.die': player_die,
}
