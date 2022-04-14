import ast
import operator as op
from typing import Union
from dataclasses import dataclass
from enum import Enum, auto

from ..datapack import DataPack
from ..tokenizer import Token, Tokenizer, TokenType
from ..exception import JMCSyntaxException
from ..utils import is_number

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

    if is_number(token.string):
        return ScoreboardPlayer(player_type=PlayerType.integer, value=int(token.string))

    splits = token.string.split(':')
    if len(splits) == 1:
        if allow_integer:
            raise JMCSyntaxException(
                f"Expected integer, variable, or objective:selector", token, tokenizer)
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

    func = "function"
    func_call = "function"
    scoreboard_player = "integer, variable, or objective:selector"
    any = None


class Arg:
    def __init__(self, token: Token, arg_type: ArgType = None,) -> None:
        self.token = token
        self.arg_type = arg_type

    def verify(self, verifier: ArgType, tokenizer: Tokenizer, key_string: str) -> "Arg":
        if verifier == ArgType.any:
            return
        if verifier == ArgType.scoreboard_player:
            if self.arg_type in {ArgType.scoreboard, ArgType.integer}:
                return
            raise JMCSyntaxException(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        if verifier == ArgType.func:
            if self.arg_type == ArgType.arrow_func:
                return
            if self.arg_type == ArgType.keyword:
                self.arg_type = ArgType.func_call
                return
            raise JMCSyntaxException(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        if verifier != self.arg_type:
            raise JMCSyntaxException(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        return self


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
        if is_number(token.string):
            return ArgType.integer
        if token.string.startswith('@'):
            return ArgType.selector
        return ArgType.keyword
    if token.token_type == TokenType.string:
        return ArgType.string

    raise JMCSyntaxException(
        f"Unknown argument type", token, tokenizer)


def verify_args(params: dict[str, ArgType], feature_name: str, token: Token, tokenizer: Tokenizer) -> dict[str, Arg]:
    args, kwargs = tokenizer.parse_func_args(token)
    result = {key: None for key in params}
    key_list = list(params)
    if len(args) > len(key_list):
        raise JMCSyntaxException(
            f"{feature_name} takes {len(key_list)} positional arguments, got {len(args)}", token, tokenizer)
    for key, arg in zip(key_list, args):
        arg_type = find_arg_type(arg, tokenizer)
        result[key] = Arg(arg, arg_type).verify(params[key], tokenizer, key)
    for key, arg in kwargs.items():
        if key not in result:
            raise JMCSyntaxException(
                f"{feature_name} got unexpected keyword argument '{key}'", token, tokenizer)
        arg_type = find_arg_type(arg, tokenizer)
        result[key] = Arg(arg, arg_type).verify(params[key], tokenizer, key)

    return result


def eval_expr(expr) -> str:
    return str(__eval(ast.parse(expr, mode='eval').body))


OPERATORS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow,
             ast.USub: op.neg}


def __eval(node):
    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return OPERATORS[type(node.op)](__eval(node.left), __eval(node.right))
    elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return OPERATORS[type(node.op)](__eval(node.operand))
    else:
        raise TypeError(node)
