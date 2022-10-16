import ast
import json
import operator as op
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable

from ..datapack import DataPack
from ..tokenizer import Token, Tokenizer, TokenType
from ..exception import JMCSyntaxException, JMCValueError
from ..utils import is_number, is_float


class PlayerType(Enum):
    VARIABLE = auto()
    INTEGER = auto()
    SCOREBOARD = auto()


@dataclass(frozen=True, slots=True)
class ScoreboardPlayer:
    player_type: PlayerType
    value: int | tuple[str, str]
    """Contains either integer or (objective and selector)"""


def find_scoreboard_player_type(
        token: Token, tokenizer: Tokenizer, allow_integer: bool = True) -> ScoreboardPlayer:
    """
    Generate ScoreboardPlayer including its type from a keyword token

    :param token: keyword token to parse
    :param tokenizer: token's Tokenizer
    :param allow_integer: Whether to allow integer(rvalue), defaults to True
    :raises JMCSyntaxException: Token is not a keyword token
    :return: ScoreboardPlayer
    """
    if token.token_type != TokenType.KEYWORD:
        raise JMCSyntaxException(
            f"Expected keyword", token, tokenizer)

    if token.string.startswith(DataPack.VARIABLE_SIGN):
        return ScoreboardPlayer(player_type=PlayerType.VARIABLE, value=(
            DataPack.var_name, token.string))

    if is_number(token.string):
        return ScoreboardPlayer(
            player_type=PlayerType.INTEGER, value=int(token.string))

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

    return ScoreboardPlayer(
        player_type=PlayerType.SCOREBOARD, value=(splits[0], splits[1]))


class ArgType(Enum):
    ARROW_FUNC = "arrow(anonymous) function"
    JS_OBJECT = "JavaScript object (dictionary)"
    JSON = "JSON"
    SCOREBOARD = "variable or objective:selector"
    INTEGER = "integer"
    FLOAT = "integer or decimal(real number)"
    STRING = "string"
    KEYWORD = "keyword"
    SELECTOR = "target selector"
    LIST = "list/array"
    FUNC = "function"
    _FUNC_CALL = "function"
    SCOREBOARD_PLAYER = "integer, variable, or objective:selector"
    ANY = None


class Arg:
    __slots__ = ('token', 'arg_type')

    def __init__(self, token: Token, arg_type: ArgType) -> None:
        self.token = token
        self.arg_type = arg_type

    def verify(self, verifier: ArgType, tokenizer: Tokenizer,
               key_string: str) -> "Arg":
        """
        Verify if the argument is valid

        :param verifier: Argument's type
        :param tokenizer: _description_
        :param key_string: Key(kwarg) in from of string
        :return: self
        """
        if verifier == ArgType.ANY:
            return self
        if verifier == ArgType.SCOREBOARD_PLAYER:
            if self.arg_type in {ArgType.SCOREBOARD, ArgType.INTEGER}:
                return self
            raise JMCValueError(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        if verifier == ArgType.FLOAT:
            if self.arg_type in {ArgType.FLOAT, ArgType.INTEGER}:
                return self
            raise JMCValueError(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        if verifier == ArgType.FUNC:
            if self.arg_type == ArgType.ARROW_FUNC:
                return self
            if self.arg_type == ArgType.KEYWORD:
                self.arg_type = ArgType._FUNC_CALL
                return self
            raise JMCValueError(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        if verifier != self.arg_type:
            raise JMCValueError(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        return self


def find_arg_type(token: Token, tokenizer: Tokenizer) -> ArgType:
    """
    Find type of the argument in form of token and return the ArgType

    :param token: any token representing argument
    :param tokenizer: Tokenizer
    :raises JMCValueError: Cannot find ArgType.FUNC type
    :return: Argument's type of the token
    """
    if token.token_type == TokenType.FUNC:
        return ArgType.ARROW_FUNC
    if token.token_type == TokenType.PAREN_CURLY:
        if re.match(r'^{\s*"', token.string) is not None:
            return ArgType.JSON
        else:
            return ArgType.JS_OBJECT
    if token.token_type == TokenType.PAREN_SQUARE:
        return ArgType.LIST

    if token.token_type == TokenType.KEYWORD:
        if token.string.startswith(
                DataPack.VARIABLE_SIGN) or ':' in token.string:
            return ArgType.SCOREBOARD
        if is_number(token.string):
            return ArgType.INTEGER
        if is_float(token.string):
            return ArgType.FLOAT
        if token.string.startswith('@'):
            return ArgType.SELECTOR
        return ArgType.KEYWORD
    if token.token_type == TokenType.STRING:
        return ArgType.STRING

    raise JMCValueError(
        "Unknown argument type", token, tokenizer)


def verify_args(params: dict[str, ArgType], feature_name: str,
                token: Token, tokenizer: Tokenizer) -> dict[str, Arg | None]:
    """
    Verify argument types of a paren_round token

    :param params: Dictionary of arguments(string) and its type(ArgType)
    :param feature_name: Feature name to show up in error
    :param token: paren_round token
    :param tokenizer: token's tokenizer
    :raises JMCValueError: Got too many positional arguments
    :raises JMCValueError: Unknown key
    :return: Dictionary of arguments(string) and said argument in Arg form
    """
    args, kwargs = tokenizer.parse_func_args(token)
    result: dict[str, Arg | None] = {key: None for key in params}
    key_list = list(params)
    if len(args) > len(key_list):
        raise JMCValueError(
            f"{feature_name} takes {len(key_list)} positional arguments, got {len(args)}", token, tokenizer)
    for key, arg in zip(key_list, args):
        arg_type = find_arg_type(arg, tokenizer)
        result[key] = Arg(arg, arg_type).verify(params[key], tokenizer, key)
    for key, kwarg in kwargs.items():
        if key not in key_list:
            raise JMCValueError(
                f"{feature_name} got unexpected keyword argument '{key}'", token, tokenizer)
        arg_type = find_arg_type(kwarg, tokenizer)
        result[key] = Arg(kwarg, arg_type).verify(params[key], tokenizer, key)
    return result


def eval_expr(expr: str) -> str:
    """
    Evaluate mathematical expression and calculate the result number then cast it to string

    :param expr: Expression string
    :return: String representation of result number
    """
    return str(__eval(ast.parse(expr, mode='eval').body))


OPERATORS: dict[type, Callable[..., Any]] = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
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


class FormattedText:
    """
    Parse formatted text into raw json string

    :param raw_text: Text
    :param token: Token
    :param tokenizer: Tokenizer
    :param is_default_no_italic: Whether to set italic to False by default, defaults to False
    :return: Raw JSON string

    .. Example::
    >>> minecraft_formatted_text("&4&lName")
    '{"text":"Name", "color":"red", "bold":true}'
    """
    __slots__ = ('raw_text', 'current_json', 'result',
                 'bracket_content', 'token', 'tokenizer',
                 'current_color', 'is_default_no_italic')

    SIGN = "&"
    OPEN_BRACKET = "<"
    CLOSE_BRACKET = ">"
    PROPS = {
        "1": "dark_blue",
        "2": "dark_green",
        "3": "dark_aqua",
        "4": "dark_red",
        "5": "dark_purple",
        "6": "gold",
        "7": "gray",
        "8": "dark_gray",
        "9": "blue",
        "0": "black",
        "a": "green",
        "b": "aqua",
        "c": "red",
        "d": "light_purple",
        "e": "yellow",
        "f": "white",
        "k": "obfuscated",
        "l": "bold",
        "m": "strikethrough",
        "n": "underlined",
        "o": "italic",
        "r": "reset",
    }

    def __init__(self, raw_text: str, token: Token,
                 tokenizer: Tokenizer, *, is_default_no_italic: bool = False) -> None:
        self.raw_text = raw_text
        self.token = token
        self.tokenizer = tokenizer
        self.is_default_no_italic = is_default_no_italic
        self.bracket_content = ""
        self.result: list[dict[str, str | bool]] = []
        self.current_json: dict[str, str | bool] = {"text": ""}
        self.current_color = ""
        self.parse()

    def push(self) -> None:
        if not self.current_json["text"]:
            return None
        self.result.append(self.current_json)
        self.current_json = {"text": ""}

    def parse_bracket(self) -> None:
        bracket_content = self.bracket_content
        self.bracket_content = ""
        properties = bracket_content.split(",")
        for prop in properties:
            value = True
            prop = prop.strip()
            if prop.startswith("!"):
                value = False
                prop = prop[1:]
            if prop in {
                'dark_red',
                'red',
                'gold',
                'yellow',
                'dark_green',
                'green',
                'aqua',
                'dark_aqua',
                'blue',
                'light_purple',
                'dark_purple',
                'white',
                'gray',
                'dark_gray',
                'black',
                'reset',
            }:
                if 'color' in self.current_json:
                    raise JMCValueError(
                        f'color({prop}) used twice in formatted text', self.token, self.tokenizer)

                self.current_json['color'] = prop
                self.current_color = prop
                if not value:
                    raise JMCValueError(
                        f'Color({prop}) cannot be false', self.token, self.tokenizer)
                continue

            if prop in {'bold', 'italic', 'underlined',
                        'strikethrough', 'obfuscated'}:
                self.current_json[prop] = value
                continue

            if prop.startswith('#') and len(prop) == 7:
                if 'color' in self.current_json:
                    raise JMCValueError(
                        f'color({prop}) used twice in formatted text', self.token, self.tokenizer)

                self.current_json['color'] = prop
                if not value:
                    raise JMCValueError(
                        f'Color({prop}) cannot be false', self.token, self.tokenizer)
                continue

            raise JMCValueError(
                f"Unknown property '{prop}'", self.token, self.tokenizer)

        if 'color' not in self.current_json and self.current_color:
            self.current_json['color'] = self.current_color

    def parse_code(self, char: str) -> None:
        prop = self.PROPS.get(char, None)
        if prop is None:
            JMCValueError(
                f"Unknown code format '{char}'", self.token, self.tokenizer)

        if prop in {
            'dark_red',
            'red',
            'gold',
            'yellow',
            'dark_green',
            'green',
            'aqua',
            'dark_aqua',
            'blue',
            'light_purple',
            'dark_purple',
            'white',
            'gray',
            'dark_gray',
            'black',
            'reset',
        }:
            if 'color' in self.current_json:
                raise JMCValueError(
                    f'color({prop}) used twice in formatted text', self.token, self.tokenizer)

            self.current_json['color'] = prop
            self.current_color = prop

        if prop in {'bold', 'italic', 'underlined',
                    'strikethrough', 'obfuscated'}:
            if self.current_color:
                self.current_json['color'] = self.current_color
            self.current_json[prop] = True

    def parse(self) -> None:
        is_expect_color_code = False
        is_bracket_format = False

        for char in self.raw_text:
            if is_bracket_format:
                if char == self.CLOSE_BRACKET:
                    is_bracket_format = False
                    self.parse_bracket()
                    continue
                self.bracket_content += char
                continue

            if is_expect_color_code:
                is_expect_color_code = False
                if char == self.OPEN_BRACKET:
                    is_bracket_format = True
                    continue
                if char == self.SIGN:
                    if isinstance(self.current_json["text"], str):
                        self.current_json["text"] += char
                        continue
                self.parse_code(char)
                continue

            if char == self.SIGN:
                self.push()
                is_expect_color_code = True
                continue

            if isinstance(self.current_json["text"], str):
                self.current_json["text"] += char

        self.push()

        if is_expect_color_code:
            raise JMCValueError(
                f"Unexpected trailing '{self.SIGN}'", self.token, self.tokenizer, suggestion=f"Remove last '{self.SIGN}'")

    def __str__(self) -> str:
        if len(self.result) == 1:
            if 'italic' not in self.result[0]:
                self.result[0]['italic'] = False
            return json.dumps(self.result[0])
        return json.dumps(
            [{"italic": False} if self.is_default_no_italic else ""] + self.result)

    def __repr__(self) -> str:
        return f"FormattedText(raw_text={repr(self.raw_text)}, result={repr(json.dumps(self.result))})"
