"""Untility for commands"""
import ast
import json
import operator as op
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable

from ..header import Header
from ..datapack import DataPack
from ..tokenizer import Token, Tokenizer, TokenType
from ..exception import JMCSyntaxException, JMCValueError
from ..utils import is_number, is_float, convention_jmc_to_mc


class PlayerType(Enum):
    VARIABLE = auto()
    INTEGER = auto()
    SCOREBOARD = auto()


@dataclass(frozen=True, slots=True)
class ScoreboardPlayer:
    player_type: PlayerType
    value: int | tuple[str, str]
    """Contains either integer or (objective and selector)"""


def is_obj_selector(tokens: list[Token], start_index: int = 0) -> bool:
    return (
        len(tokens) >= start_index + 3
        and
        tokens[start_index].token_type == TokenType.KEYWORD
        and
        tokens[start_index + 1].token_type == TokenType.OPERATOR
        and
        tokens[start_index + 1].string == ":"
        and
        tokens[start_index + 2].token_type == TokenType.KEYWORD
    )


def merge_obj_selector(tokens: list[Token], tokenizer: Tokenizer,
                       datapack: DataPack, start_index: int = 0) -> Token:
    """
    Merge objective:selector[] into one token

    :param tokens: List of tokens
    :param tokenizer: Tokenizer
    :param datapack: Datapack
    :param start_index: Index of the first token(keyword) in objective:selector[], defaults to 0
    :raises ValueError: Impossible tokens array length (merge_obj_selector used without is_obj_selector)
    :return: Merged token
    """
    if len(tokens) >= start_index + \
            4 and tokens[start_index + 3].token_type == TokenType.PAREN_SQUARE:
        tokens[start_index + 3] = Token(tokens[start_index + 3].token_type, tokens[start_index + 3].line, tokens[start_index + 3].col, datapack.lexer.clean_up_paren_token(
            tokens[start_index + 3], tokenizer))
        return_value = tokenizer.merge_tokens(
            tokens[start_index:start_index + 4])
        del tokens[start_index + 1:start_index + 4]
        return return_value
    elif len(tokens) >= start_index + 3:
        return_value = tokenizer.merge_tokens(
            tokens[start_index:start_index + 3])
        del tokens[start_index + 1:start_index + 3]
        return return_value
    raise ValueError(
        "Impossible tokens array length (merge_obj_selector used without is_obj_selector)")


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
            "Expected keyword", token, tokenizer)

    if token.string.startswith(DataPack.VARIABLE_SIGN):
        return ScoreboardPlayer(player_type=PlayerType.VARIABLE, value=(
            DataPack.var_name, token.string))

    if is_number(token.string):
        return ScoreboardPlayer(
            player_type=PlayerType.INTEGER, value=int(token.string))

    splits = token.string.split(":", 1)
    if len(splits) == 1:
        if allow_integer:
            raise JMCSyntaxException(
                "Expected integer, variable, or objective:selector", token, tokenizer, suggestion="Did you mean ")
        raise JMCSyntaxException(
            "Expected variable or objective:selector", token, tokenizer)
    return ScoreboardPlayer(
        player_type=PlayerType.SCOREBOARD, value=(splits[0], splits[1]))


class NumberType(Enum):
    POSITIVE = "more than zero"
    ZERO_POSITIVE = "more than or equal to zero"
    NON_ZERO = "non-zero"


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
    SCOREBOARD_INT = "integer, variable, or objective:selector"
    ANY = None


class Arg:
    __slots__ = ("token", "arg_type")

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
        if verifier == ArgType.SCOREBOARD_INT:
            if self.arg_type in {ArgType.SCOREBOARD, ArgType.INTEGER}:
                return self
            if self.arg_type == ArgType.KEYWORD and self.token.string.count(
                    ":") == 1:
                return self
            raise JMCValueError(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        if verifier == ArgType.SCOREBOARD:
            if self.arg_type == ArgType.SCOREBOARD:
                return self
            if self.arg_type == ArgType.KEYWORD and self.token.string.count(
                    ":") == 1:
                self.arg_type = ArgType.SCOREBOARD
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
            if self.arg_type in {ArgType.KEYWORD, ArgType.SCOREBOARD}:
                self.arg_type = ArgType._FUNC_CALL
                return self
            raise JMCValueError(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        if verifier == ArgType.SELECTOR:
            if self.arg_type == ArgType.SELECTOR:
                return self
            if self.arg_type == ArgType.KEYWORD:
                self.arg_type = ArgType.SELECTOR
                return self
            raise JMCValueError(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer)
        if verifier == ArgType.KEYWORD:
            if key_string.startswith("@"):
                raise JMCValueError(
                    f"For '{key_string}' key, expected {verifier.value}, got {ArgType.SELECTOR.value}",
                    self.token,
                    tokenizer)
            if ":" in key_string:
                raise JMCValueError(
                    f"For '{key_string}' key, expected {verifier.value}, got {ArgType.SCOREBOARD.value}",
                    self.token,
                    tokenizer)
        if verifier != self.arg_type:
            suggestion = None
            if verifier == ArgType.STRING:
                suggestion = f"Did you mean: ' \"{self.token.string}\" '"
            raise JMCValueError(
                f"For '{key_string}' key, expected {verifier.value}, got {self.arg_type.value}", self.token, tokenizer, suggestion=suggestion)
        return self


def find_arg_type(tokens: list[Token], tokenizer: Tokenizer) -> ArgType:
    """
    Find type of the argument in form of token and return the ArgType

    :param tokens: List of tokens representing an argument
    :param tokenizer: Tokenizer
    :raises JMCValueError: Cannot find ArgType.FUNC type
    :return: Argument's type of the token
    """
    if not tokens:
        raise ValueError("Trying to find type of empty argument")
    if len(tokens) == 1:
        if tokens[0].token_type == TokenType.PAREN_CURLY:
            if re.match(r'^{\s*"', tokens[0].string) is not None:
                return ArgType.JSON
            return ArgType.JS_OBJECT
        if tokens[0].token_type == TokenType.PAREN_SQUARE:
            return ArgType.LIST
        if tokens[0].token_type == TokenType.FUNC:
            return ArgType.ARROW_FUNC
        if tokens[0].token_type == TokenType.STRING:
            return ArgType.STRING

    if is_number(tokens[0].string):
        if len(tokens) > 1:
            raise JMCSyntaxException(
                f"Unexpected {tokens[1].token_type.value} after integer in function argument",
                tokens[1],
                tokenizer)
        return ArgType.INTEGER
    if is_float(tokens[0].string):
        if len(tokens) > 1:
            raise JMCSyntaxException(
                f"Unexpected {tokens[1].token_type.value} after float/decimal in function argument",
                tokens[1],
                tokenizer)
        return ArgType.FLOAT

    if tokens[0].string in {'-', '+'} and len(tokens) > 1:
        if is_number(tokens[1].string):
            if len(tokens) > 2:
                raise JMCSyntaxException(
                    f"Unexpected {tokens[2].token_type.value} after integer in function argument",
                    tokens[2],
                    tokenizer)
            return ArgType.INTEGER
        if is_float(tokens[1].string):
            if len(tokens) > 1:
                raise JMCSyntaxException(
                    f"Unexpected {tokens[2].token_type.value} after float/decimal in function argument",
                    tokens[2],
                    tokenizer)
            return ArgType.FLOAT

    if (
        len(tokens) == 3
        and
        tokens[0].string.startswith(
            DataPack.VARIABLE_SIGN)
        and
        tokens[1].string == ':'
    ):
        return ArgType.SCOREBOARD
    if tokens[0].string.startswith("@"):
        if len(tokens) == 1:
            return ArgType.SELECTOR
        if tokens[1].token_type == TokenType.PAREN_SQUARE:
            if len(tokens) > 2:
                raise JMCSyntaxException(
                    "Unexpected token after target selector",
                    tokens[2],
                    tokenizer,
                    suggestion="This can be a result from missing comma or missing quotation mark")
            return ArgType.SELECTOR
        raise JMCSyntaxException(
            f"Expected '[' or nothing after target selector type (got {tokens[1].token_type})",
            tokens[1],
            tokenizer)

    if tokens[0].token_type == TokenType.KEYWORD:
        if len(tokens) == 1:
            if tokens[0].string.startswith(DataPack.VARIABLE_SIGN):
                return ArgType.SCOREBOARD
            return ArgType.KEYWORD
        for index, token in enumerate(tokens[1:]):
            if token.token_type == tokens[index].token_type == TokenType.KEYWORD:
                raise JMCSyntaxException(
                    "2 keywords are next to each other in function argument",
                    token,
                    tokenizer,
                    suggestion="This can be a result from missing comma or missing quotation mark")
        return ArgType.KEYWORD

    raise JMCValueError(
        "Unknown argument type", tokens[-1], tokenizer)


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
        arg_token = tokenizer.merge_tokens(arg)
        result[key] = Arg(
            arg_token,
            arg_type).verify(
            params[key],
            tokenizer,
            key)
    for key, kwarg in kwargs.items():
        if key not in key_list:
            raise JMCValueError(
                f"{feature_name} got unexpected keyword argument '{key}'", kwarg[-1], tokenizer,
                suggestion=f"""Available arguments are\n{', '.join(f"'{param}'" for param in params)}""")
        arg_type = find_arg_type(kwarg, tokenizer)
        kwarg_token = tokenizer.merge_tokens(kwarg)
        result[key] = Arg(
            kwarg_token,
            arg_type).verify(
            params[key],
            tokenizer,
            key)
    return result


def eval_expr(expr: str) -> str:
    """
    Evaluate mathematical expression and calculate the result number then cast it to string

    :param expr: Expression string
    :return: String representation of result number
    """
    number = __eval(ast.parse(expr.replace("\\", "//"), mode="eval").body)
    if isinstance(number, int):
        return f"{number:d}"
    if isinstance(number, float):
        if abs(number) >= 100:
            return f"{number:.2f}"
        elif abs(number) >= 10:
            return f"{number:.3f}"
        elif abs(number) >= 1:
            return f"{number:.3f}"
        string = f"{number:.12f}"
        whole, decimal = string.split(".")
        for i, char in enumerate(decimal):
            if char != "0":
                break
        return whole + "." + decimal[:i + 5].rstrip("0")
    return str(number)


OPERATORS: dict[type, Callable[..., Any]] = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                                             ast.Div: op.truediv, ast.FloorDiv: op.floordiv, ast.Mod: op.mod,
                                             ast.Pow: op.pow, ast.USub: op.neg}


def __eval(node):
    """
    Inner working of eval_expr

    :param node: expr(body of Expression returned from ast.parse)
    :raises TypeError: Invalid type of node
    :return: Result number
    """
    if isinstance(node, ast.Num):  # <number>
        return node.n
    if isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return OPERATORS[type(node.op)](__eval(node.left), __eval(node.right))
    if isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return OPERATORS[type(node.op)](__eval(node.operand))

    raise TypeError(node)


SIMPLE_JSON_TYPE = dict[
    str,
    str | bool | dict[
        str, str | bool
    ]
]


class FormattedText:
    """
    Parse formatted text into raw json string

    :param raw_text: Text
    :param token: Token (only used for error)
    :param tokenizer: Tokenizer
    :param is_default_no_italic: Whether to set italic to False by default, defaults to False
    :param is_allow_score_selector: Whether to allow score selector in the string, defaults to True
    :return: Raw JSON string

    .. example::
    >>> str(FormattedText("&4&lName", token, tokenizer))
    '{"text":"Name", "color":"red", "bold":true}'
    >>> str(FormattedText("&<red,bold>Name", token, tokenizer, is_default_no_italic=True))
    '{"text":"Name", "color":"red", "bold":true, "italic":false}'
    """
    __slots__ = ("raw_text", "current_json", "result",
                 "bracket_content", "token", "tokenizer",
                 "current_color", "is_default_no_italic", "datapack",
                 "is_allow_score_selector")

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
                 tokenizer: Tokenizer, datapack: DataPack, *, is_default_no_italic: bool = False, is_allow_score_selector: bool = True) -> None:
        self.raw_text = raw_text
        self.token = token
        self.tokenizer = tokenizer
        self.datapack = datapack
        self.is_default_no_italic = is_default_no_italic
        self.is_allow_score_selector = is_allow_score_selector
        self.bracket_content = ""
        self.result: list[SIMPLE_JSON_TYPE] = []
        self.current_json: SIMPLE_JSON_TYPE = {"text": ""}
        self.current_color = ""
        self.__parse()

    def add_key(self, key: str, value: str | bool |
                dict[str, str | bool]) -> None:
        """
        Add json to result

        :param key: JSON Key
        :param value: JSON Value
        """
        if self.result:
            self.result[0][key] = value
            return

        self.result.append({key: value})

    def __can_merge(self) -> bool:
        """
        Whether current_json and result[-1] can merge
        """
        return (
            bool(self.result) and
            len(self.result[-1]) == 2 and
            "text" in self.result[-1] and
            "color" in self.result[-1] and
            len(self.current_json) == 2 and
            "text" in self.current_json and
            "color" in self.current_json and
            self.result[-1]["color"] == self.current_json["color"]
        )

    def __push(self) -> None:
        """
        Append current_json to result and reset it
        """
        if not self.current_json["text"]:
            return
        if self.__can_merge():
            self.result[-1]["text"] += self.current_json["text"]  # type: ignore # fmt: off
            self.current_json = {"text": ""}
            return
        if "color" in self.current_json and self.current_json["color"] == "reset":
            del self.current_json["color"]
        self.result.append(self.current_json)
        self.current_json = {"text": ""}

    def __parse_bracket(self) -> None:
        """
        Parse self.bracket_content and reset it
        """
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
                "dark_red",
                "red",
                "gold",
                "yellow",
                "dark_green",
                "green",
                "aqua",
                "dark_aqua",
                "blue",
                "dark_blue",
                "light_purple",
                "dark_purple",
                "white",
                "gray",
                "dark_gray",
                "black",
                "reset",
            }:
                if "color" in self.current_json:
                    raise JMCValueError(
                        f"color({prop}) used twice in formatted text", self.token, self.tokenizer)

                self.current_json["color"] = prop
                self.current_color = prop
                if not value:
                    raise JMCValueError(
                        f"Color({prop}) cannot be false", self.token, self.tokenizer)
                continue

            if prop in {"bold", "italic", "underlined",
                        "strikethrough", "obfuscated"}:
                self.current_json[prop] = value
                continue

            if prop.startswith("#") and len(prop) == 7:
                if "color" in self.current_json:
                    raise JMCValueError(
                        f"color({prop}) used twice in formatted text", self.token, self.tokenizer)

                self.current_json["color"] = prop
                if not value:
                    raise JMCValueError(
                        f"Color({prop}) cannot be false", self.token, self.tokenizer)
                continue

            if prop.startswith(DataPack.VARIABLE_SIGN):
                if "selector" in self.current_json:
                    raise JMCValueError(
                        "selector used with score in formatted text", self.token, self.tokenizer)
                if "score" in self.current_json:
                    raise JMCValueError(
                        "score used twice in formatted text", self.token, self.tokenizer)
                self.current_json["score"] = {
                    "name": prop, "objective": self.datapack.var_name}
                if not value:
                    raise JMCValueError(
                        "Score cannot be false", self.token, self.tokenizer)
                continue

            if prop.count(":") == 1:
                if "selector" in self.current_json:
                    raise JMCValueError(
                        "selector used with score in formatted text", self.token, self.tokenizer)
                if "score" in self.current_json:
                    raise JMCValueError(
                        "score used twice in formatted text", self.token, self.tokenizer)
                objective, name = prop.split(":")
                self.current_json["score"] = {
                    "name": name, "objective": objective}
                if not value:
                    raise JMCValueError(
                        "Score cannot be false", self.token, self.tokenizer)
                continue

            if prop.startswith("@"):
                if "score" in self.current_json:
                    raise JMCValueError(
                        "score used with selector in formatted text", self.token, self.tokenizer)
                if "selector" in self.current_json:
                    raise JMCValueError(
                        "selector used with selector in formatted text", self.token, self.tokenizer)
                self.current_json["selector"] = prop
                if not value:
                    raise JMCValueError(
                        "Selector cannot be false", self.token, self.tokenizer)
                continue

            if prop.endswith(")"):
                open_paren_index = prop.find("(")
                arg = prop[open_paren_index + 1:-1].strip()
                prop_ = prop[:open_paren_index]
                if prop_ not in self.datapack.data.formatted_text_prop:
                    raise JMCValueError(
                        f"Unknown property '{prop_}'", self.token, self.tokenizer)
                key, json_body, is_local = self.datapack.data.formatted_text_prop[prop_]
                if isinstance(json_body, dict) and 'nbt' in json_body.keys():
                    self.current_json[key] = {}
                    self.current_json[key]["nbt"] = json_body["nbt"](arg)  # type: ignore # fmt: off
                    if "separator" in json_body.keys():
                        self.current_json[key]["separator"] = json_body["separator"](arg)  # type: ignore # fmt: off

                    if "entity" in json_body.keys():
                        self.current_json[key]["entity"] = json_body["entity"]  # type: ignore # fmt: off
                    if "block" in json_body.keys():
                        self.current_json[key]["block"] = json_body["block"]  # type: ignore # fmt: off
                    if "storage" in json_body.keys():
                        self.current_json[key]["storage"] = json_body["storage"]  # type: ignore # fmt: off
                elif not callable(json_body):
                    raise JMCValueError(
                        f"Custom property '{prop_}' expected no argument", self.token, self.tokenizer, suggestion="Remove '()'")
                elif not arg:
                    raise JMCValueError(
                        f"Expected value inside parenthesis of property '{prop_}' (got nothing)", self.token, self.tokenizer)
                else:
                    self.current_json[key] = json_body(arg)
                if is_local:
                    del self.datapack.data.formatted_text_prop[prop_]
                continue

            if prop not in self.datapack.data.formatted_text_prop:
                raise JMCValueError(
                    f"Unknown property '{prop}'", self.token, self.tokenizer)
            key, json_body, is_local = self.datapack.data.formatted_text_prop[prop]
            if callable(json_body):
                raise JMCValueError(
                    f"Custom property '{prop}' expected an argument (got 0)", self.token, self.tokenizer)
            self.current_json[key] = json_body
            if is_local:
                del self.datapack.data.formatted_text_prop[prop]
            continue

        if "color" not in self.current_json and self.current_color:
            self.current_json["color"] = self.current_color

        if self.datapack.version >= 19:
            for _type in {"score", "selector", "nbt", "keybind"}:
                if _type in self.current_json:
                    self.current_json["type"] = _type
            if "__private_nbt_expand__" in self.current_json and self.datapack.version >= 21:
                assert isinstance(self.current_json["__private_nbt_expand__"], dict)
                self.current_json["type"] = "nbt"
                for source in {"entity", "block", "storage"}:
                    if source in self.current_json["__private_nbt_expand__"]:
                        self.current_json["source"] = source
            elif "type" not in self.current_json:
                self.current_json["type"] = "text"

        if "score" in self.current_json or "selector" in self.current_json or "keybind" in self.current_json or "__private_nbt_expand__" in self.current_json:
            if not self.is_allow_score_selector:
                if "score" in self.current_json:
                    raise JMCValueError(
                        "score is not allowed in this context in formatted text", self.token, self.tokenizer)
                raise JMCValueError(
                    "selector is not allowed in this context in formatted text", self.token, self.tokenizer)
            del self.current_json["text"]

            if "__private_nbt_expand__" in self.current_json:
                assert isinstance(self.current_json["__private_nbt_expand__"], dict)
                self.current_json["nbt"] = self.current_json["__private_nbt_expand__"]["nbt"]
                self.current_json["interpret"] = \
                    (self.current_json["__private_nbt_expand__"]["interpret"] == "true")
                if "separator" in self.current_json["__private_nbt_expand__"].keys():
                    self.current_json["separator"] = self.current_json["__private_nbt_expand__"]["separator"]
                if "storage" in self.current_json["__private_nbt_expand__"]:
                    self.current_json["storage"] = self.current_json["__private_nbt_expand__"]["storage"]
                if "block" in self.current_json["__private_nbt_expand__"]:
                    self.current_json["block"] = self.current_json["__private_nbt_expand__"]["block"]
                if "entity" in self.current_json["__private_nbt_expand__"]:
                    self.current_json["entity"] = self.current_json["__private_nbt_expand__"]["entity"]
                del self.current_json["__private_nbt_expand__"]

            tmp_json: SIMPLE_JSON_TYPE = {"text": ""}
            for prop_, value_ in self.current_json.items():
                if prop_ in {"bold", "italic", "underlined",
                             "strikethrough", "obfuscated", "color"}:
                    tmp_json[prop_] = value_
            if "color" in self.current_json and self.current_json["color"] == "reset":
                del self.current_json["color"]
            self.result.append(self.current_json)
            self.current_json = tmp_json

    def __parse_code(self, char: str) -> None:
        """
        Parse color code

        :param char: A character in color code
        """
        prop = self.PROPS.get(char, None)
        if prop is None:
            JMCValueError(
                f"Unknown code format '{char}'", self.token, self.tokenizer)

        if prop in {
            "dark_red",
            "red",
            "gold",
            "yellow",
            "dark_green",
            "green",
            "aqua",
            "dark_aqua",
            "blue",
            "dark_blue",
            "light_purple",
            "dark_purple",
            "white",
            "gray",
            "dark_gray",
            "black",
            "reset",
        }:
            self.current_json["color"] = prop
            self.current_color = prop

        elif prop in {"bold", "italic", "underlined", "strikethrough", "obfuscated"}:
            if self.current_color:
                self.current_json["color"] = self.current_color
            self.current_json[prop] = True

    def __parse(self) -> None:
        """
        Parse raw_text
        """
        is_expect_color_code = False
        is_bracket_format = False

        for char in self.raw_text:
            if is_bracket_format:
                if char == self.CLOSE_BRACKET:
                    is_bracket_format = False
                    self.__parse_bracket()
                    continue
                self.bracket_content += char
                continue

            if is_expect_color_code:
                is_expect_color_code = False
                if char == self.SIGN:
                    if isinstance(self.current_json["text"], str):
                        self.current_json["text"] += char  # type: ignore
                        continue
                if char == self.OPEN_BRACKET:
                    self.__push()
                    is_bracket_format = True
                    continue
                self.__push()
                self.__parse_code(char)
                continue

            if char == self.SIGN:
                is_expect_color_code = True
                continue

            if isinstance(self.current_json["text"], str):
                self.current_json["text"] += char  # type: ignore

        if is_bracket_format:
            raise JMCValueError(
                "'<' was never closed in formatted text", self.token, self.tokenizer)
        self.__push()

        if is_expect_color_code:
            raise JMCValueError(
                f"Unexpected trailing '{self.SIGN}'", self.token, self.tokenizer, suggestion=f"Remove last '{self.SIGN}'")

    @classmethod
    def empty(cls, tokenizer: Tokenizer,
              datapack: DataPack) -> "FormattedText":
        """
        Generate an empty FormattedText with empty Token

        :param tokenizer: Tokenizer
        :param datapack: Datapack
        :return: FormattedText
        """
        return cls('', Token.empty(), tokenizer, datapack)

    def __bool__(self) -> bool:
        return bool(self.result) and ("text" in self.result[0])

    def __str__(self) -> str:
        if not self.result:
            return '""'

        if len(self.result) == 1 and len(self.result[0]) == 1 and "text" in self.result[0]:
            return json.dumps(self.result[0]["text"])

        if len(self.result) == 1:
            if self.is_default_no_italic and "italic" not in self.result[0]:
                self.result[0]["italic"] = False
            return json.dumps(self.result[0], separators=(",", ":"))

        return json.dumps(
            [{"text": "", "italic": False} if self.is_default_no_italic else ""] + self.result, separators=(",", ":"))

    def __repr__(self) -> str:
        return f"FormattedText(raw_text={repr(self.raw_text)}, result={repr(json.dumps(self.result))})"


ZERO_TO_Z_LENGTH = 36


def __custom_hash(text: str) -> int:
    """
    Custom hash to use for hashing string to string

    :param text: String to hash
    :return: Hashed string
    """
    hashed = 0
    for ch in text:
        hashed = (hashed * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
    return hashed


def hash_string_to_string(string: str, length: int) -> str:
    """
    Hash a string into another string with fixed length

    :param string: String to hash
    :param length: Length of the result string
    :return: Result string
    """
    number: int = __custom_hash(string) % (ZERO_TO_Z_LENGTH**length)
    if number == 0:
        digits: list[int] = [0]
    else:
        digits = []
        for _ in range(length):
            digits.append(int(number % ZERO_TO_Z_LENGTH))
            number //= ZERO_TO_Z_LENGTH
        digits = digits[::-1]

    return ''.join(str(digit) if 0 <= digit <= 9 else chr(
        digit - 10 + 97) for digit in digits)


def hardcode_parse_calc(calc_pos: int, string: str, token: Token, tokenizer: Tokenizer) -> str:
    count = 0
    expression = ''
    index = calc_pos
    if len(string) < calc_pos + 14 or string[calc_pos + 13] != "(":
        raise JMCSyntaxException(
            "Expected ( after Hardcode.calc", token, tokenizer, display_col_length=False)
    for char in string[calc_pos + 13:]:  # len('Hardcode.calc') = 13
        index += 1
        if char == "(":
            count += 1
        elif char == ")":
            count -= 1

        expression += char
        if count == 0:
            break

    if count != 0:
        raise JMCSyntaxException(
            "Invalid syntax in Hardcode.calc", token, tokenizer, display_col_length=False)

    for key, num in sorted(Header().number_macros.items(), key=lambda item: len(item[0]), reverse=True):
        expression = expression.replace(key, num)

    for char in expression:
        if char not in {"0", "1", "2", "3", "4", "5", "6", "7",
                        "8", "9", "+", "-", "*", "/", "\\", "%",
                        " ", "\t", "\n", "(", ")"}:
            raise JMCSyntaxException(
                f"Invalid character({char}) in Hardcode.calc", token, tokenizer, display_col_length=False)

    return string[:calc_pos] + \
        eval_expr(expression) + string[index + 13:]
