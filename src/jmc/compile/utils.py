"""Utility for compiling"""

from copy import deepcopy
import functools
from random import Random
import re
from json import JSONEncoder, dumps
from typing import TYPE_CHECKING, Any, Callable


from .exception import JMCSyntaxException, MinecraftSyntaxWarning

if TYPE_CHECKING:
    from .tokenizer import Token, Tokenizer, TokenType


class SingleTonMeta(type):
    """
    Metaclass for singleton
    """

    _instances: dict["SingleTonMeta", Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SingleTon(metaclass=SingleTonMeta):
    """
    Super class for a singleton class

    :raises TypeError: Instantiated directly
    """

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if cls is SingleTon:
            raise TypeError(f"Only children of '{cls.__name__}' may be instantiated")
        return super().__new__(cls, *args, **kwargs)


def is_number(string: str) -> bool:
    """Whether string can be converted to integer"""
    try:
        int(string)
    except ValueError:
        return False
    else:
        return True


def is_float(string: str) -> bool:
    """Whether string can be converted to integer"""
    try:
        float(string)
    except ValueError:
        return False
    else:
        return True


def is_connected(current_token: "Token", previous_token: "Token") -> bool:
    """Whether 2 tokens are next to each other"""
    if not previous_token._macro_length:
        return (
            previous_token.line == current_token.line
            and previous_token.col + previous_token.length == current_token.col
        )
    return previous_token.line == current_token.line and current_token.col in {
        previous_token.col + previous_token.length,
        previous_token.col + previous_token._macro_length,
    }


def __parse_to_string(
    token: "Token", tokenizer: "Tokenizer"
) -> dict[str, str | bool | dict[str, str]]:
    """
    Parse `toString` in JMC

    :param token: paren_round token (arguments of `toString`)
    :param tokenizer: token's tokenizer
    :return: Dictionary of key(key) and value(string or boolean)
    """
    json: dict[str, str | bool | dict[str, str]] = {}
    if token.string == "()":
        return json

    for kwargs in token.string[1:-1].split(","):
        if "=" not in kwargs:
            raise JMCSyntaxException(
                "'=' not found in .toString argument", token, tokenizer
            )
        key, value, *extras = kwargs.split("=")
        key = key.strip()
        if extras:
            raise JMCSyntaxException(
                f"Too many '=' found in .toString argument (got {len(extras) + 1})",
                token,
                tokenizer,
            )
        if value in {'""', "''"}:
            raise JMCSyntaxException(
                ".toString function accepts keyword as arguments, not string",
                token,
                tokenizer,
                suggestion="Do not use empty string as argument",
            )
        if value[0] in {'"', "'"}:
            raise JMCSyntaxException(
                ".toString function accepts keyword as arguments, not string",
                token,
                tokenizer,
                suggestion=f"Use '{value[1:-1]}' instead of '{value}'",
            )
        if value[0] in {"{", "(", "["}:
            raise JMCSyntaxException(
                "Brackets are not supported in .toString",
                token,
                tokenizer,
                suggestion="clickEvent and hoverEvent are not supported, use normal minecraft JSON instead.",
            )

        if key in {"font", "color"}:
            json[key] = value
        elif key in {"bold", "italic", "underlined", "strikethrough", "obfuscated"}:
            if value not in {"true", "false"}:
                raise JMCSyntaxException(
                    f"value of {key} .toString must be either 'true' or 'false'",
                    token,
                    tokenizer,
                )
            json[key] = value == "true"
        elif key in {"clickEvent", "hoverEvent"}:
            raise JMCSyntaxException(
                "clickEvent and hoverEvent are not supported in .toString",
                token,
                tokenizer,
                suggestion="Use normal minecraft JSON instead",
            )
        elif key == "text":
            raise JMCSyntaxException(
                "'text' key is incompatible with 'score' in .toString", token, tokenizer
            )
        else:
            raise JMCSyntaxException(
                f"Unrecognized key in .toString (got {key})",
                token,
                tokenizer,
                suggestion="Avaliable keys are 'font', 'color', 'bold', 'italic', 'underlined', 'strikethrough', 'obfuscated'",
            )
    return json


class JSONUniversalEncoder(JSONEncoder):
    """
    JSONEncoder that can encode everything, used for displaying results
    """

    def default(self, o):
        try:
            iterator = iter(o)
        except TypeError:
            pass
        else:
            return list(iterator)

        return repr(o)


def monitor_results(func):
    """
    Decorator to monitor a function for debugging

    :param func: Function for decorator
    :return: Wrapper function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return_value = func(*args, **kwargs)
        print(
            f"""Function call {func.__name__}(
args={dumps(args, indent=4, cls=JSONUniversalEncoder)},
kwargs={dumps(kwargs, indent=4, cls=JSONUniversalEncoder)}
) returns {dumps(return_value, indent=4, cls=JSONUniversalEncoder)}
"""
        )
        return return_value

    return wrapper


def convention_jmc_to_mc(
    token: "Token",
    tokenizer: "Tokenizer",
    prefix: str,
    is_make_lower: bool = True,
    substr: tuple[int, int] | None = None,
    custom_string: str | None = None,
) -> str:
    """
    Turns JMC function/predicate name syntax to vanilla's syntax

    .. example::
    >>> convention_jmc_to_mc(Token.empty("hello.World"))
    "hello_world"

    :param token: keyword token
    :param tokenizer: token's tokenizer
    """
    if custom_string is None:
        string = token.string
    else:
        string = custom_string
    if substr is not None:
        string = string[substr[0] : substr[1]]
    if string.startswith("."):
        raise JMCSyntaxException("Name started with '.'", token, tokenizer)
    if string.endswith("."):
        raise JMCSyntaxException("Name ended with '.'", token, tokenizer)
    if is_make_lower:
        string = string.lower()

    if prefix and string.startswith("this."):
        string = string.replace("this.", prefix.replace("/", "."), 1)

    if re.match("^[a-z0-9_\\.]+$", string) is None:
        parens_hint: str | None = None
        if string.endswith("()"):
            parens_hint = (
                f"If {string} is meant to be a function name, remove the parentheses"
            )
        raise MinecraftSyntaxWarning(
            f"Invalid character detected in '{string}'",
            token,
            tokenizer,
            suggestion=parens_hint,
        )
    return string.replace(".", "/")


def get_mc_uuid(seed: Any) -> str:
    """
    Generate UUID in minecraft syntax

    :param seed: Seed for randomization
    :return: UUID in minecraft syntax (`[I;...]`)
    """
    random_instance = Random(seed)

    def rand_java_int() -> int:
        return random_instance.randint(-2147483648, 2147483647)

    return (
        f"[I;{rand_java_int()},{rand_java_int()},{rand_java_int()},{rand_java_int()}]"
    )


def is_decorator(string: str) -> bool:
    return len(string) > 2 and string.startswith("@")


def deep_merge(first: dict, second: dict) -> dict:
    """
    Recursively merges two dictionaries together.
    (i.e. it also merges any dicts inside of them)

    :param first: The dictionary to merge stuff to
    :param second: The dictionary being merged into the first
    :return: A new dict that is the merger of both inputs
    """
    output = deepcopy(first)
    for key in second:
        if (
            key in output
            and isinstance(output[key], dict)
            and isinstance(second[key], dict)
        ):
            output[key] = deep_merge(output[key], second[key])
        else:
            output[key] = second[key]
    return output


def clean_up_paren_token(
    token: "Token",
    tokenizer: "Tokenizer",
    is_nbt: bool = True,
    keyword_token_callback: Callable[["Token"], str] = lambda token: token.string,
) -> str:
    """
    Turn a paren token into a clean string

    :param token: paren token
    :param tokenizer: token's Tokenizer
    :param is_nbt: Whether the token is in form of minecraft nbt, defaults to True
    :param keyword_token_callback: A special function to modify any keyword token
    :return: Clean string representing paren token for output
    """
    if len(token.string) == 2:
        return token.string
    open_ = token.string[0]
    close = token.string[-1]
    TokenType = type(token.token_type)
    tokenizer = type(tokenizer)(
        token.string[1:-1],
        tokenizer.file_path,
        token.line,
        token.col + 1,
        tokenizer.file_string,
        expect_semicolon=False,
        allow_semicolon=token.token_type == TokenType.PAREN_SQUARE,
    )
    string = ""
    if open_ == "{" and tokenizer.programs[0][0].token_type == TokenType.STRING:
        is_nbt = False

    for token_ in tokenizer.programs[0]:
        if token_.token_type in {
            TokenType.PAREN_CURLY,
            TokenType.PAREN_SQUARE,
            TokenType.PAREN_ROUND,
        }:
            _string = clean_up_paren_token(
                token_, tokenizer, is_nbt, keyword_token_callback
            )
        elif token_.token_type == TokenType.STRING:
            if is_nbt:
                _string = repr(token_.string)
                if '"' not in _string:
                    _string = f'"{_string[1:-1]}"'
            else:
                _string = dumps(token_.string)
        elif token_.token_type == TokenType.KEYWORD:
            _string = keyword_token_callback(token_)
        else:
            _string = token_.string
        string += _string
    return open_ + string + close


def merge_dicts(dict1: dict[Any, Any], dict2: dict[Any, Any]) -> dict[Any, Any]:
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result
