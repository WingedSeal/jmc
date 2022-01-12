import logging
from typing import List, Tuple

from . import Logger, PackGlobal
from .command import Command
from .utils import replace_function_call, clean_whitespace
import re
import regex

FUNCTION_REGEX = r'function ([\w\._]+)\(\) ({(?:(?:(["\'])(?:(?=(\\?))\4.)*?\3|[^}{])+|(?2))*+})'
logger = Logger(__name__)


class Function:
    def __init__(self, name: str, context: str, pack_global: PackGlobal) -> None:
        self.name = name
        context = replace_function_call(context, pack_global)
        self.context = [
            Command(command, pack_global)
            for command
            in context.split('; ')
            if command
        ]  # Remove empty string command
        nl = '\n'
        self.__str = f"""
    Name: {self.name}
    Contexts (Commands):\n{nl.join([str(command) for command in self.context])}
        """
        logger.debug(f"Function created:{self.__str}")

    def __str__(self) -> str:
        return self.__str


def capture_function(string: str, pack_global: PackGlobal) -> str:
    """Take string of jmc and return leftover jmc_string, and add functions to pack_global"""
    logger.info("Capturing Functions")
    jmcfunctions_match: List[re.Match] = regex.finditer(
        FUNCTION_REGEX, string, overlapped=False)

    def get_context(match: re.Match):
        return match.groups()[0]
    for jmcfunction in jmcfunctions_match:
        groups: Tuple[str] = jmcfunction.groups()
        name = groups[0]
        # Skip the first spacebar
        context = re.sub(r'{ (.*)}', get_context, groups[1])
        pack_global.functions[name] = Function(
            name, context, pack_global)
    return clean_whitespace(regex.sub(FUNCTION_REGEX, '', string))
