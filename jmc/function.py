import logging
from typing import List, Tuple

from . import Logger, PackGlobal
from .command import Command
from .utils import replace_function_call, clean_whitespace, BracketRegex
import re
import regex

# FUNCTION_REGEX = r'function ([\w\._]+)\(\) ({(?:(?:(["\'])(?:(?=(\\?))\4.)*?\3|[^}{])+|(?2))*+})'
bracket_regex = BracketRegex()
FUNCTION_REGEX = r'function ([\w\._]+)\(\) ' + bracket_regex.match_bracket('{}', 2)  # noqa
logger = Logger(__name__)


class Function:
    def __init__(self, name: str, context: str, pack_global: PackGlobal) -> None:
        self.name = str(name)
        context = replace_function_call(context, pack_global)
        self.context = [
            Command(command.strip(), pack_global)
            for command
            in context.split(';')
            if command  # Remove empty string command
        ]
        nl = '\n'
        self.__str = f"""
    Name: {self.name}
    Contexts (Commands):\n{nl.join([str(command) for command in self.context])}
        """
        logger.debug(f"Function created:{self.__str}")

    def __str__(self) -> str:
        return self.__str

    def __repr__(self) -> str:
        return self.__str


def capture_function(string: str, pack_global: PackGlobal) -> str:
    """Take string of jmc and return leftover jmc_string, and add functions to pack_global"""
    logger.info("Capturing Functions")
    for jmcfunction in regex.finditer(FUNCTION_REGEX, string, overlapped=False):
        jmcfunction: re.Match
        groups: Tuple[str] = bracket_regex.compile(jmcfunction.groups())
        name = groups[0]
        context = groups[1]
        pack_global.functions[name] = Function(
            name, context, pack_global)
    return regex.sub(FUNCTION_REGEX, '', string)
