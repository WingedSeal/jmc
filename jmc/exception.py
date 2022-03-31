from json import JSONDecodeError
from typing import TYPE_CHECKING
from .log import Logger

if TYPE_CHECKING:
    from .tokenizer import Token, Tokenizer

logger = Logger(__name__)
NEW_LINE = '\n'


def log(self: object, args: tuple):
    logger.warning(f"{self.__class__.__name__}\n{args[0]}")


class JMCSyntaxException(SyntaxError):
    def __init__(self, message: str, token: "Token", tokenizer: "Tokenizer", *, col_length: bool = False, display_col_length: bool = True, entire_line: bool = False, suggestion: str = None) -> None:
        col = token.col
        display_col = token.col
        if col_length:
            col += token.length-1
        if display_col_length:
            display_col += token.length
        if entire_line:
            msg = f"In {tokenizer.file_path}\n{message} at line {token.line}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1]} <-"
        else:
            msg = f"In {tokenizer.file_path}\n{message} at line {token.line} col {col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:display_col-1]} <-"
        if suggestion is not None:
            msg += '\n'+suggestion
        log(self, [msg])
        super().__init__(msg)


class JMCSyntaxWarning(SyntaxWarning):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class JMCFileNotFoundError(FileNotFoundError):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class JMCBuildError(Exception):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class JMCDecodeJSONError(ValueError):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class MinecraftSyntaxWarning(SyntaxError):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)
