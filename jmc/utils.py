from typing import TYPE_CHECKING
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
