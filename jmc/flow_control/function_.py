import regex
import re
from typing import TYPE_CHECKING

from ..utils import BracketRegex
from .. import Logger

if TYPE_CHECKING:
    from ..datapack import DataPack
    from ..command import Command

logger = Logger(__name__)

bracket_regex = BracketRegex()
FUNCTION_REGEX = r'^function\s*([\w\._]+)\(\)\s*' + bracket_regex.match_bracket('{}', 2)  # noqa


def capture_function(self: "DataPack", line: str, prefix: str):
    logger.debug("Searching for Function")
    line = line.strip()
    logger.debug(line)

    def function_found(match: re.Match):
        func_name, func_content = bracket_regex.compile(match.groups())
        logger.debug(f"Function found - {prefix}{func_name}")
        commands = self.process_function_content(func_content)
        self.functions[f'{prefix}{func_name}'.lower().replace(
            '.', '/')] = Function(commands)
        return ""
    line, success = regex.subn(FUNCTION_REGEX, function_found, line, count=1)

    if success:
        logger.debug(f"Recursing capture()")
        line = self.capture(line, prefix)
    else:
        logger.debug("No Function found")

    return line


class Function:
    def __init__(self, commands: list["Command"]) -> None:
        self.commands = commands
        pass

    def __repr__(self) -> str:
        return repr(self.commands)
