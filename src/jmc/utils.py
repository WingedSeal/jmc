from json import dumps
import re
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from .tokenizer import Token


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


def __parse_to_string(token: "Token") -> dict[str, Union[str, bool]]:
    return dict()


def __search_to_string(match: re.Match, token: "Token", VAR_NAME: str) -> str:
    var = match.group(1)
    properties = __parse_to_string(token)
    properties["score"] = {"name": var, "objective": VAR_NAME}
    return dumps(properties)


def search_to_string(last_str: str, token: "Token", VAR_NAME: str) -> tuple[str, bool]:
    new_str, count = re.subn(
        r'(\$[A-z0-9\-\.\_]+)\.toString$', lambda match: __search_to_string(match, token, VAR_NAME), last_str)
    if count:
        return new_str, True
    return last_str, False
