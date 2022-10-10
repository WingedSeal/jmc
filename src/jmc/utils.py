import functools
import re
from json import JSONEncoder, dumps
from typing import TYPE_CHECKING, Any

from .exception import JMCSyntaxException

if TYPE_CHECKING:
    from .tokenizer import Token, Tokenizer

class __SingleTonMeta(type):
    """
    Metaclass for singleton
    """
    _instances: dict["__SingleTonMeta", Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class SingleTon(metaclass=__SingleTonMeta):
    """
    Super class for a singleton class

    :raises TypeError: Instantiated directly
    """
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


def is_connected(current_token: "Token", previous_token: "Token") -> bool:
    """Whether 2 tokens are next to each other"""
    return (
        previous_token.line == current_token.line and
        previous_token.col +
        previous_token.length == current_token.col
    )


def __parse_to_string(token: "Token", tokenizer: "Tokenizer") -> dict[str, str | bool | dict[str, str]]:
    """
    Parse `toString` in JMC

    :param token: paren_round token (arguments of `toString`)
    :param tokenizer: token's tokenizer
    :return: Dictionary of key(key) and value(string or boolean)
    """
    json: dict[str, str | bool | dict[str, str]] = {}
    if token.string == '()':
        return json

    for kwargs in token.string[1:-1].split(','):
        if '=' not in kwargs:
            raise JMCSyntaxException(
                "'=' not found in .toString argument", token, tokenizer)
        key, value, *extras = kwargs.split('=')
        if extras:
            raise JMCSyntaxException(
                f"Too many '=' found in .toString argument (got {len(extras)+1})", token, tokenizer)
        if value in {'""', "''"}:
            raise JMCSyntaxException(
                ".toString function accepts keyword as arguments, not string", token, tokenizer, suggestion=f"Do not use empty string as argument")
        if value[0] in {'"', "'"}:
            raise JMCSyntaxException(
                ".toString function accepts keyword as arguments, not string", token, tokenizer, suggestion=f"Use '{value[1:-1]}' instead of '{value}'")
        if value[0] in {'{', '(', '['}:
            raise JMCSyntaxException(
                "Brackets are not supported in .toString", token, tokenizer, suggestion="clickEvent and hoverEvent are not supported, use vanila JSON instead.")

        if key in {'font', 'color'}:
            json[key] = value
        elif key in {'bold', 'italic', 'underlined', 'strikethrough', 'obfuscated'}:
            if value not in {'true', 'false'}:
                raise JMCSyntaxException(
                    f"value of {key} .toString must be either 'true' or 'false'", token, tokenizer)
            json[key] = value == 'true'
        elif key in {'clickEvent', 'hoverEvent'}:
            raise JMCSyntaxException(
                f"clickEvent and hoverEvent are not supported in .toString", token, tokenizer, suggestion="Use vanila JSON instead")
        elif key == 'text':
            raise JMCSyntaxException(
                f"'text' key is incompatible with 'score' in .toString", token, tokenizer)
        else:
            raise JMCSyntaxException(
                f"Unrecognized key in .toString (got {key})", token, tokenizer, suggestion="Avaliable keys are 'font', 'color', 'bold', 'italic', 'underlined', 'strikethrough', 'obfuscated'")
    return json


def __search_to_string(match: re.Match, token: "Token", VAR_NAME: str, tokenizer: "Tokenizer") -> str:
    """
    Function for regex.subn

    :param match: Match object
    :param token: Token to search for `toString`
    :param VAR_NAME: `DataPack.VARNAME`
    :param tokenizer: token's tokenizer
    :return: JSON formatted string
    """
    var: str = match.group(1)
    properties = __parse_to_string(token, tokenizer)
    properties["score"] = {"name": var, "objective": VAR_NAME}
    return dumps(properties)


def search_to_string(last_str: str, token: "Token", VAR_NAME: str, tokenizer: "Tokenizer") -> tuple[str, bool]:
    """
    Find `toString` in a last_str

    :param last_str: Last string before this token
    :param token: paren_round token (Arguments of `toString`)
    :param VAR_NAME: `DataPack.VARNAME``
    :param tokenizer: token's tokenizer
    :return: Tuple of New string and Whether `toString` is found
    """
    new_str, count = re.subn(
        r'(\$[A-z0-9\-\.\_]+)\.toString$', lambda match: __search_to_string(match, token, VAR_NAME, tokenizer), last_str)
    if count:
        return new_str, True
    return last_str, False

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
        return_value = func(*args,**kwargs)
        print(f"""Function call {func.__name__}(
args={dumps(args, indent=2, cls=JSONUniversalEncoder)}, 
kwargs={dumps(kwargs, indent=2, cls=JSONUniversalEncoder)}
) returns {dumps(return_value, indent=2, cls=JSONUniversalEncoder)}
""")
        return return_value
    return wrapper