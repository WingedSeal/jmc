from typing import Union
from dataclasses import dataclass
from enum import Enum, auto

from ..datapack import DataPack
from ..tokenizer import Token, Tokenizer, TokenType
from ..exception import JMCSyntaxException

NEW_LINE = '\n'


class PlayerType(Enum):
    variable = auto()
    integer = auto()
    scoreboard = auto()


@dataclass(frozen=True)
class ScoreboardPlayer:
    player_type: PlayerType
    value: Union[int, tuple[str, str]]
    """Contains either integer or (objective and selector)"""


def find_scoreboard_player_type(token: Token, tokenizer: Tokenizer, allow_integer: bool = True) -> ScoreboardPlayer:
    if token.token_type != TokenType.keyword:
        raise JMCSyntaxException(
            f"Expected keyword", token, tokenizer)

    if token.string.startswith(DataPack.VARIABLE_SIGN):
        return ScoreboardPlayer(player_type=PlayerType.variable, value=(DataPack.VAR_NAME, token.string))

    if token.string.isnumeric():
        return ScoreboardPlayer(player_type=PlayerType.integer, value=int(token.string))

    splits = token.string.split(':')
    if len(splits) == 1:
        if allow_integer:
            raise JMCSyntaxException(
                f"Expected integer, variable, or objective:selector ", token, tokenizer)
        else:
            raise JMCSyntaxException(
                f"Expected variable or objective:selector", token, tokenizer)
    if len(splits) > 2:
        raise JMCSyntaxException(
            "Scoreboard's player cannot contain more than 1 colon(:)", token, tokenizer)

    return ScoreboardPlayer(player_type=PlayerType.scoreboard, value=(splits[0], splits[1]))
