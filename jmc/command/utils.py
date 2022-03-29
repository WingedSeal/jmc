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


def find_scoreboard_player_type(token: Token, tokenizer: Tokenizer) -> ScoreboardPlayer:
    if token.token_type != TokenType.keyword:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nExpected keyword at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-")
    if token.string.startswith(DataPack.VARIABLE_SIGN):
        return ScoreboardPlayer(player_type=PlayerType.variable, value=(DataPack.VAR_NAME, token.string))

    if token.string.isnumeric():
        return ScoreboardPlayer(player_type=PlayerType.integer, value=int(token.string))

    splits = token.string.split(':')
    if len(splits) == 1:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nExpected Integer, Variable, or ScoreboardPlayer(`objective:selector`) at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-")
    if len(splits) > 2:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nScoreboardPlayer(`objective:selector`) cannot contain more than 1 colon(:) at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-")
    return ScoreboardPlayer(player_type=PlayerType.scoreboard, value=(splits[0], splits[1]))
