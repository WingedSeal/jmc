from typing import Any, Optional, Union
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


class ArgType(Enum):
    arrow_func = "arrow(anonymous) function"
    js_object = "JavaScript object (dictionary)"
    json = "JSON"
    scoreboard = "variable or objective:selector"
    integer = "integer"
    string = "string"
    keyword = "keyword"
    selector = "target selector"


def find_arg_type(token: Token, tokenizer: Tokenizer) -> ArgType:
    """Cannot find ArgType.func type"""
    if token.token_type == TokenType.func:
        return ArgType.arrow_func
    if token.token_type == TokenType.paren_curly:
        if token.string.startswith('{"'):
            return ArgType.json
        else:
            return ArgType.js_object
    if token.token_type == TokenType.keyword:
        if token.string.startswith(DataPack.VARIABLE_SIGN) or ':' in token.string:
            return ArgType.scoreboard
        if token.string.isnumeric():
            return ArgType.integer
        if token.string.startswith('@'):
            return ArgType.selector
        return ArgType.keyword
    if token.token_type == TokenType.string:
        return ArgType.string

    raise JMCSyntaxException(
        f"Unknown argument type", token, tokenizer)


def verify_args(params: dict[str, ArgType], feature_name: str, token: Token, tokenizer: Tokenizer) -> dict[str, Token]:
    args, kwargs = tokenizer.parse_func_args(token)
    result = {key: None for key in params}
    key_list = list(params)
    if len(args) > len(key_list):
        raise JMCSyntaxException(
            f"{feature_name} takes {len(key_list)} positional arguments, got {len(args)}", token, tokenizer)
    for key, arg in zip(key_list, args):
        result[key] = arg
    for key, arg in kwargs.items():
        if key not in result:
            raise JMCSyntaxException(
                f"{feature_name} got unexpected keyword argument '{key}'", token, tokenizer)
        result[key] = arg

    for key, value in result.items():
        if value is not None:
            arg_type = find_arg_type(value, tokenizer)
            if params[key] != arg_type:
                raise JMCSyntaxException(
                    f"For '{key}' key, expected {params[key].value}, got {arg_type.value}", token, tokenizer)

    return result
