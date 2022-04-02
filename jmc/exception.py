from json import JSONDecodeError
from typing import TYPE_CHECKING
from .log import Logger

if TYPE_CHECKING:
    from .tokenizer import Token, Tokenizer

logger = Logger(__name__)
NEW_LINE = '\n'


def log(self: object, args: tuple):
    logger.warning(f"{self.__class__.__name__}\n{args[0]}")


def error_msg(message: str, token: "Token", tokenizer: "Tokenizer", col_length: bool, display_col_length: bool, entire_line: bool, suggestion: str) -> str:
    # if (token is None) != (tokenizer is None):
    #     raise ValueError(
    #         f"JMCSyntaxException argument error {'token' if token is None else 'tokenizer'} is not provided")
    # if token is None and tokenizer is None:
    #     return message
    col = token.col
    line = token.line
    display_line = line
    display_col = col

    if col_length:
        if '\n' in token.string:
            line += token.string.count('\n')
            col = token.length - token.string.rfind('\n')
        else:
            col += token.length

    if display_col_length:
        if '\n' in token.string:
            display_line += token.string.count('\n')
            display_col = token.length - token.string.rfind('\n')
        else:
            display_col += token.length
    if entire_line:
        msg = f"In {tokenizer.file_path}\n{message} at line {line}.\n{tokenizer.file_string.split(NEW_LINE)[display_line-1]} <-"
    else:
        msg = f"In {tokenizer.file_path}\n{message} at line {line} col {col}.\n{tokenizer.file_string.split(NEW_LINE)[display_line-1][:display_col-1]} <-"
    if suggestion is not None:
        msg += '\n'+suggestion
    return msg


class JMCSyntaxException(SyntaxError):
    def __init__(self, message: str, token: "Token", tokenizer: "Tokenizer", *, col_length: bool = False, display_col_length: bool = True, entire_line: bool = False, suggestion: str = None) -> None:
        msg = error_msg(message, token, tokenizer, col_length,
                        display_col_length, entire_line, suggestion)
        log(self, [msg])
        super().__init__(msg)


class JMCSyntaxWarning(SyntaxWarning):
    def __init__(self, message: str, token: "Token", tokenizer: "Tokenizer", *, col_length: bool = False, display_col_length: bool = True, entire_line: bool = False, suggestion: str = None) -> None:
        msg = error_msg(message, token, tokenizer, col_length,
                        display_col_length, entire_line, suggestion)
        log(self, [msg])
        super().__init__(msg)


class JMCFileNotFoundError(FileNotFoundError):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class JMCBuildError(Exception):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class JMCDecodeJSONError(ValueError):
    def __init__(self, error: JSONDecodeError, token: "Token", tokenizer: "Tokenizer") -> None:
        line = token.line + error.lineno - 1
        col = token.col + error.colno - 1 \
            if token.line == line else error.colno

        msg = f"In {tokenizer.file_path}\n{error.msg} at line {line} col {col}.\n{tokenizer.file_string.split(NEW_LINE)[line-1][:col-1]} <-"

        log(self, [msg])
        super().__init__(msg)


class JMCTypeError(TypeError):
    def __init__(self, missing_argument: str, token: "Token", tokenizer: "Tokenizer", *, suggestion: str = None) -> None:
        msg = error_msg(f"Missing required positional argument: '{missing_argument}'", token, tokenizer, col_length=False,
                        display_col_length=False, entire_line=False, suggestion=suggestion)

        log(self, [msg])
        super().__init__(msg)


class MinecraftSyntaxWarning(SyntaxError):
    def __init__(self, message: str, token: "Token", tokenizer: "Tokenizer", *, col_length: bool = False, display_col_length: bool = True, entire_line: bool = False, suggestion: str = None) -> None:
        msg = error_msg(message, token, tokenizer, col_length,
                        display_col_length, entire_line, suggestion)
        log(self, [msg])
        super().__init__(msg)
