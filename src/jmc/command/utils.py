import ast
import operator as op
import re
from dataclasses import dataclass
from enum import Enum, auto

from ..datapack import DataPack
from ..tokenizer import Token, Tokenizer, TokenType
from ..exception import JMCSyntaxException
from ..utils import is_number, monitor_results


class PlayerType(Enum):
    variable = auto()
    integer = auto()
    scoreboard = auto()


@dataclass(frozen=True)
class ScoreboardPlayer:
    player_type: PlayerType
    value: int|tuple[str, str]
    """Contains either integer or (objective and selector)"""


def find_scoreboard_player_type(token: Token, tokenizer: Tokenizer, allow_integer: bool = True) -> ScoreboardPlayer:
    """
    Generate ScoreboardPlayer including its type from a keyword token

    :param token: keyword token to parse
    :param tokenizer: token's Tokenizer
    :param allow_integer: Whether to allow integer(rvalue), defaults to True
    :raises JMCSyntaxException: Token is not a keyword token
    :return: ScoreboardPlayer
    """
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
    _func_call = "function"
    scoreboard_player = "integer, variable, or objective:selector"
    any = None


class Arg:
    def __init__(self, token: Token, arg_type: ArgType = None,) -> None:
        self.token = token
        self.arg_type = arg_type

    def verify(self, verifier: ArgType, tokenizer: Tokenizer, key_string: str) -> "Arg":
        """
        Verify if the argument is valid

        :param verifier: Argument's type
        :param tokenizer: _description_
        :param key_string: Key(kwarg) in from of string
        :return: self
        """
        if verifier == ArgType.any:
            return self
        if verifier == ArgType.scoreboard_player:
            if self.arg_type in {ArgType.scoreboard, ArgType.integer}:
                return self
            raise JMCSyntaxException(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        if verifier == ArgType.func:
            if self.arg_type == ArgType.arrow_func:
                return self
            if self.arg_type == ArgType.keyword:
                self.arg_type = ArgType._func_call
                return self
            raise JMCSyntaxException(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        if verifier != self.arg_type:
            raise JMCSyntaxException(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        return self


def find_arg_type(token: Token, tokenizer: Tokenizer) -> ArgType:
    """
    Find type of the argument in form of token and return the ArgType

    :param token: any token representing argument
    :param tokenizer: Tokenizer
    :raises JMCSyntaxException: Cannot find ArgType.func type
    :return: Argument's type of the token
    """
    if token.token_type == TokenType.func:
        return ArgType.arrow_func
    if token.token_type == TokenType.paren_curly:
        if re.match(r'^{\s*"', token.string) is not None:
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
    """
    Verify argument types of a paren_round token

    :param params: Dictionary of arguments(string) and its type(ArgType)
    :param feature_name: Feature name to show up in error
    :param token: paren_round token
    :param tokenizer: token's tokenizer
    :raises JMCSyntaxException: Got too many positional arguments
    :raises JMCSyntaxException: Unknown key
    :return: Dictionary of arguments(string) and said argument in Arg form
    """
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

@monitor_results
def eval_expr(expr: str) -> str:
    """
    Evaluate mathematical expression and calculate the result number then cast it to string

    :param expr: Expression string
    :return: String representation of result number
    """
    return str(__eval(ast.parse(expr, mode='eval').body))


OPERATORS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow,
             ast.USub: op.neg}


def __eval(node):
    """
    Inner working of eval_expr

    :param node: expr(body of Expression returned from ast.parse)
    :raises TypeError: Invalid type of node
    :return: Result number
    """
    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return OPERATORS[type(node.op)](__eval(node.left), __eval(node.right))
    elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return OPERATORS[type(node.op)](__eval(node.operand))
    else:
        raise TypeError(node)


def parse_func_map(token: Token, tokenizer: Tokenizer, datapack: DataPack) -> dict[int, tuple[str, bool]]:
    """
    Parse JMC function hashmap

    :param token: paren_curly token
    :param tokenizer: token's tokenizer
    :param datapack: Datapack object
    :return: Dictionary of integer key and (tuple of function string and whether it is an arrow function)
    """
    func_map = dict()
    for key, value in tokenizer.parse_js_obj(token).items():
        try:
            num = int(key)
        except ValueError:
            raise JMCSyntaxException(
                f"Expected number as key (got {key})", token, tokenizer)

        if value.token_type == TokenType.keyword:
            func_map[num] = value.string, False
        elif value.token_type == TokenType.func:
            func_map[num] = '\n'.join(
                datapack.parse_function_token(value, tokenizer)), True
        else:
            raise JMCSyntaxException(
                f"Expected function, got {value.token_type.value}", token, tokenizer)
    return func_map
