from json import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING
from .log import Logger

if TYPE_CHECKING:
    from .tokenizer import Token, Tokenizer

logger = Logger(__name__)
NEW_LINE = '\n'


def log(self: object, args: tuple):
    """
    Log the exception as warning

    :param self: Exception itself
    :param args: Exception's arguments (Starting with message)
    """
    logger.warning(f"{self.__class__.__name__}\n{args[0]}")


def error_msg(message: str, token: "Token|None", tokenizer: "Tokenizer", col_length: bool,
              display_col_length: bool, entire_line: bool, suggestion: str | None) -> str:
    """
    Generate error message

    :param message: Main message at the front of the error
    :param token: A token/tokenizer where the error happens
    :param tokenizer: token's tokenizer
    :param col_length: Whether to add token's length to column count
    :param display_col_length: Whether to display the code until the end of the token
    :param entire_line: Whether to display the entire line of code
    :param suggestion: A suggestion message at the end of the error message
    :return: Error message
    """

    if token is None:
        string = ""
        length = 1
        col = tokenizer.col
        line = tokenizer.line
    else:
        string = token.string
        length = token.length
        col = token.col
        line = token.line

    display_line = line
    display_col = col

    if col_length:
        if '\n' in string:
            line += string.count('\n')
            col = length - string.rfind('\n')
        else:
            col += length

    if display_col_length:
        if '\n' in string:
            display_line += string.count('\n')
            display_col = length - string.rfind('\n')
        else:
            display_col += length
    if entire_line:
        msg = f"In {tokenizer.file_path}\n{message} at line {line}.\n{tokenizer.file_string.split(NEW_LINE)[display_line-1]} <-"
    else:
        msg = f"In {tokenizer.file_path}\n{message} at line {line} col {col}.\n{tokenizer.file_string.split(NEW_LINE)[display_line-1][:display_col-1]} <-"
    if suggestion is not None:
        msg += '\n' + suggestion
    return msg


class HeaderFileNotFoundError(FileNotFoundError):
    """Header file not found"""

    def __init__(self, path: Path):
        msg = f"Header file not found: {path.as_posix()}"
        log(self, (msg, ))
        super().__init__(msg)


class HeaderDuplicatedMacro(ValueError):
    """Define same macro twice"""

    def __init__(self, message: str, file_name: str, line: int, line_str: str):
        msg = f"In {file_name}\n{message} at line {line}\n{line_str}"
        log(self, (msg, ))
        super().__init__(msg)


class HeaderSyntaxException(SyntaxError):
    """Invalid syntax for header"""

    def __init__(self, message: str, file_name: str, line: int, line_str: str):
        msg = f"In {file_name}\n{message} at line {line}\n{line_str}"
        log(self, (message, ))
        super().__init__(msg)


class JMCSyntaxException(SyntaxError):
    """Invalid syntax for JMC"""

    def __init__(self, message: str, token: "Token|None", tokenizer: "Tokenizer", *, col_length: bool = False,
                 display_col_length: bool = True, entire_line: bool = False, suggestion: str | None = None) -> None:
        msg = error_msg(message, token, tokenizer, col_length,
                        display_col_length, entire_line, suggestion)
        log(self, (msg, ))
        super().__init__(msg)


class JMCValueError(ValueError):
    """Invalid syntax for JMC"""

    def __init__(self, message: str, token: "Token|None", tokenizer: "Tokenizer", *, col_length: bool = False,
                 display_col_length: bool = True, entire_line: bool = False, suggestion: str | None = None) -> None:
        msg = error_msg(message, token, tokenizer, col_length,
                        display_col_length, entire_line, suggestion)
        log(self, (msg, ))
        super().__init__(msg)


class JMCSyntaxWarning(SyntaxWarning):
    """Warnings about dubious JMC syntax"""

    def __init__(self, message: str, token: "Token|None", tokenizer: "Tokenizer", *, col_length: bool = False,
                 display_col_length: bool = True, entire_line: bool = False, suggestion: str | None = None) -> None:
        msg = error_msg(message, token, tokenizer, col_length,
                        display_col_length, entire_line, suggestion)
        log(self, (msg, ))
        super().__init__(msg)


class JMCFileNotFoundError(FileNotFoundError):
    """JMC file not found"""

    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class JMCBuildError(Exception):
    """Cannot build the datapack"""

    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class JMCDecodeJSONError(ValueError):
    """Invalid syntax for JSON"""

    def __init__(self, error: JSONDecodeError, token: "Token",
                 tokenizer: "Tokenizer") -> None:
        line = token.line + error.lineno - 1
        col = token.col + error.colno - 1 \
            if token.line == line else error.colno

        msg = f"In {tokenizer.file_path}\n{error.msg} at line {line} col {col}.\n{tokenizer.file_string.split(NEW_LINE)[line-1][:col-1]} <-"

        log(self, (msg, ))
        super().__init__(msg)


class JMCMissingValueError(ValueError):
    """Missing required positional argument"""

    def __init__(self, missing_argument: str, token: "Token",
                 tokenizer: "Tokenizer", *, suggestion: str | None = None) -> None:
        msg = error_msg(f"Missing required positional argument: '{missing_argument}'", token, tokenizer, col_length=False,
                        display_col_length=False, entire_line=False, suggestion=suggestion)

        log(self, (msg, ))
        super().__init__(msg)


class MinecraftSyntaxWarning(SyntaxError):
    """Warnings about dubious Minecraft syntax"""

    def __init__(self, message: str, token: "Token", tokenizer: "Tokenizer", *, col_length: bool = False,
                 display_col_length: bool = True, entire_line: bool = False, suggestion: str | None = None) -> None:
        msg = error_msg(message, token, tokenizer, col_length,
                        display_col_length, entire_line, suggestion)
        log(self, (msg, ))
        super().__init__(msg)
