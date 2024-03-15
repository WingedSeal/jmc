"""Module containing all jmc exceptions"""
from json import JSONDecodeError
import os
from pathlib import Path
from typing import TYPE_CHECKING, Callable
from .log import Logger

if TYPE_CHECKING:
    from .tokenizer import Token, Tokenizer

logger = Logger(__name__)
NEW_LINE = "\n"
TAB = "\t"


def relative_file_name(file_name: str, line: int |
                       None = None, col: int | None = None) -> str:
    file_path = Path(file_name)
    if not file_path.is_relative_to(os.getcwd()):
        return file_name
    file_name = file_path.relative_to(os.getcwd()).as_posix()
    if line is not None:
        file_name += f":{line}"
    if col is not None:
        file_name += f":{col}"
    return file_name


def log(self: object, args: tuple):
    """
    Log the exception as warning

    :param self: Exception itself
    :param args: Exception's arguments (Starting with message)
    """
    logger.warning(f"{self.__class__.__name__}\n{args[0]}")


def error_msg(message: str, token: "Token|None", tokenizer: "Tokenizer", col_length: bool,
              display_col_length: bool, entire_line: bool, suggestion: str | None, overide_file_str: Callable[[str], str] = lambda string: string) -> str:
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
        string = token.get_full_string()
        length = token.length
        col = token.col
        line = token.line

    display_line = line
    display_col = col

    if col_length:
        if "\n" in string:
            line += string.count("\n")
            col = length - string.rfind("\n")
        else:
            col += length
        display_col += 1

    if display_col_length:
        if "\n" in string:
            display_line += string.count("\n")
            display_col = length - string.rfind("\n") + 1
        else:
            display_col += length
    else:
        display_col += 1
    try:
        msgs_ = tokenizer.file_string.split(NEW_LINE)
        max_space = len(str(display_line + 1))
        line_ = overide_file_str(msgs_[display_line - 1])
        if entire_line:
            tab_count = line_.count(TAB)
            msg = f"""In {relative_file_name(tokenizer.file_path, line)}
{message} at line {line}.
{display_line-1}{" "*(max_space-len(str(display_line - 1)))} |{msgs_[display_line-2].replace(TAB, "    ") if display_line > 1 else ""}
{display_line}{" "*(max_space-len(str(display_line)))} |{line_.replace(TAB, "    ")}
{" "*(col+max_space+3*tab_count+1)}{"^"*(len(line_)-col+1)}
{display_line+1} |{msgs_[display_line].replace(TAB, "    ") if display_line < len(msgs_) else ""}"""
        else:
            tab_count = line_[:col - 1].count(TAB)
            msg = f"""In {relative_file_name(tokenizer.file_path, line, col)}
{message} at line {line} col {col}.
{display_line-1}{" "*(max_space-len(str(display_line - 1)))} |{msgs_[display_line-2].replace(TAB, "    ") if display_line > 1 else ""}
{display_line}{" "*(max_space-len(str(display_line)))} |{line_.replace(TAB, "    ")}
{" "*(col+max_space+3*tab_count+1)}{"^"*(display_col-col)}
{display_line+1} |{msgs_[display_line].replace(TAB, "    ") if display_line < len(msgs_) else ""}"""
    except ValueError as error:
        logger.critical(
            f"Error happens at wrong file: {tokenizer.file_path=}, {line=}, {col=}")
        raise error
    if suggestion is not None:
        msg += "\n" + suggestion
    return msg


class EvaluationException(FileNotFoundError):
    """Header file not found"""

    def __init__(self, string: str):
        msg = f"Unable to evaluate expression '{string}'"
        log(self, (msg, ))
        super().__init__(msg)


class HeaderFileNotFoundError(FileNotFoundError):
    """Header file not found"""

    def __init__(self, path: Path):
        msg = f"Header file not found: {path.as_posix()}"
        log(self, (msg, ))
        super().__init__(msg)


class HeaderDuplicatedMacro(ValueError):
    """Define same macro twice"""

    def __init__(self, message: str, file_name: str, line: int, line_str: str):
        msg = f"In {relative_file_name(file_name, line)}\n{message} at line {line}\n{line_str}"
        log(self, (msg, ))
        super().__init__(msg)


class HeaderSyntaxException(SyntaxError):
    """Invalid syntax for header"""

    def __init__(self, message: str, file_name: str, line: int,
                 line_str: str, suggestion: str | None = None):
        msg = f"In {relative_file_name(file_name, line)}\n{message} at line {line}\n{line_str}"
        if suggestion is not None:
            msg += "\n" + suggestion
        log(self, (message, ))
        super().__init__(msg)


class JMCSyntaxException(SyntaxError):
    """Invalid syntax for JMC"""

    def __init__(self, message: str, token: "Token | None", tokenizer: "Tokenizer", *, col_length: bool = False,
                 display_col_length: bool = True, entire_line: bool = False, suggestion: str | None = None) -> None:
        self.message = message
        self.token = token
        self.tokenizer = tokenizer
        self.col_length = col_length
        self.display_col_length = display_col_length
        self.entire_line = entire_line
        self.suggestion = suggestion
        msg = error_msg(message, token, tokenizer, col_length,
                        display_col_length, entire_line, suggestion)
        log(self, (msg, ))
        super().__init__(msg)

    def reinit(self, overide_file_str: Callable[[str], str]):
        """
        Overide initialization
        """
        self.msg = error_msg(self.message, self.token, self.tokenizer, self.col_length,
                             self.display_col_length, self.entire_line, self.suggestion, overide_file_str)
        logger.warning("Overiding file string")
        log(self, (self.msg, ))


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


class MinecraftVersionTooLow(Exception):
    """Pack format is too outdated"""

    def __init__(self, pack_format: int, token: "Token|None", tokenizer: "Tokenizer",
                 *, suggestion: str | None = None) -> None:
        msg = error_msg(f"Datapack's pack_format is too outdated for this feature. Expected pack_format of {pack_format} or higher", token, tokenizer, col_length=False,
                        display_col_length=True, entire_line=False, suggestion=suggestion)
        log(self, (msg, ))
        super().__init__(msg)


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


EXCEPTIONS = (
    HeaderDuplicatedMacro,
    HeaderFileNotFoundError,
    HeaderSyntaxException,
    JMCDecodeJSONError,
    JMCFileNotFoundError,
    JMCMissingValueError,
    JMCSyntaxException,
    JMCSyntaxWarning,
    JMCValueError,
    MinecraftSyntaxWarning,
    JMCBuildError,
    MinecraftVersionTooLow,
    EvaluationException
)
