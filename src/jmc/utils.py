import re
from json import dumps
from typing import TYPE_CHECKING, Union

from .exception import JMCSyntaxException

if TYPE_CHECKING:
    from .tokenizer import Token, Tokenizer


def is_number(string: str) -> bool:
    try:
        int(string)
    except ValueError:
        return False
    else:
        return True


def is_connected(current_token: "Token", previous_token: "Token") -> bool:
    return (
        previous_token.line == current_token.line and
        previous_token.col +
        previous_token.length == current_token.col
    )


def __parse_to_string(token: "Token", tokenizer: "Tokenizer") -> dict[str, Union[str, bool]]:
    json = dict()
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
    var = match.group(1)
    properties = __parse_to_string(token, tokenizer)
    properties["score"] = {"name": var, "objective": VAR_NAME}
    return dumps(properties)


def search_to_string(last_str: str, token: "Token", VAR_NAME: str, tokenizer: "Tokenizer") -> tuple[str, bool]:
    new_str, count = re.subn(
        r'(\$[A-z0-9\-\.\_]+)\.toString$', lambda match: __search_to_string(match, token, VAR_NAME, tokenizer), last_str)
    if count:
        return new_str, True
    return last_str, False
