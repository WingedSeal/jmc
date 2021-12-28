import logging
from typing import List, Tuple

from . import Logger, PackGlobal
from .command import Command
from .utils import replace_function_call
import re
import regex

FUNCTION_REGEX = r'function ([\w\._]+)\(([\w, ]*)\) ({(?:[^}{]+|(?3))*+})'
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
        pack_global.functions_name.add(name)
        nl = '\n'
        self.__str = f"""
    Name: {self.name}
    Parameters: {self.params}
    Contexts (Commands):\n{nl.join([str(command) for command in self.context])}
        """
        logger.debug(f"Function created:{self.__str}")

    def __str__(self) -> str:
        return self.__str


def capture_function(string: str, pack_global: PackGlobal) -> Tuple[List[Function], str]:
    """Take string of jmc and return a tuple which include list of Function object and left-over jmc string"""
    logger.info("Capturing Functions")
    jmcfunctions_match: List[re.Match] = regex.finditer(
        FUNCTION_REGEX, string, overlapped=False)
    jmcfunctions: List[Function] = []

    def get_context(match: re.Match):
        return match.groups()[0]
    for jmcfunction in jmcfunctions_match:
        groups: Tuple[str] = jmcfunction.groups()
        name = groups[0]
        params = groups[1]
        # Skip the first spacebar
        context = re.sub(r'{ (.*)}', get_context, groups[2])
        jmcfunctions.append(Function(name, params, context, pack_global))
    return jmcfunctions, regex.sub(FUNCTION_REGEX, '', string).lstrip()
    # TODO: Please fix this, it fails to capture stuff and for some reason the string was cut off before this
