import logging
from typing import List, Tuple

from . import Logger, PackGlobal
from .command import Command
from .utils import replace_function_call, clean_whitespace
import re
import regex

FUNCTION_REGEX = r'function ([\w\._]+)\(([\w, ]*)\) ({(?:(?:(["\'])(?:(?=(\\?))\5.)*?\4|[^}{])+|(?3))*+})'
logger = Logger(__name__)


class Function:
    def __init__(self, name: str, params: str, context: str, pack_global: PackGlobal) -> None:
        self.name = name
        self.params = [param for param in params.replace(
            ' ', '').split(',') if param]  # Remove empty string param
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
    Parameters: {self.params}
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
        params = groups[1]
        # Skip the first spacebar
        context = re.sub(r'{ (.*)}', get_context, groups[2])
        pack_global.functions.append(
            Function(name, params, context, pack_global))
    return clean_whitespace(regex.sub(FUNCTION_REGEX, '', string))
