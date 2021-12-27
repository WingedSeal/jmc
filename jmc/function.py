import logging
from typing import List, Tuple
import re

from . import Logger, PackGlobal
from .command import Command

FUNCTION_REGEX = r'function (\w+)\(([\w, ]*)\) \{ ([^}{(]+|\{(?:[^}{(]+|\{[^}{}]*\})*\})*\}'
logger = Logger(__name__, logging.INFO)


class Function:
    def __init__(self, name: str, params: str, context: str, pack_global: PackGlobal) -> None:
        self.name = name
        self.params = [param for param in params.replace(
            ' ', '').split(',') if param]  # Remove empty string param
        self.context = [Command(command, pack_global) for command in context.split(
            '; ') if command]  # Remove empty string command
        pack_global.functions_name.add(name)
        nl = '\n'
        self.__str = f"""
        Name: {self.name}
        Parameters: {self.params}
        Contexts (Commands): 
        {nl.join([str(command) for command in self.context])}
        """
        logger.debug(f"Function created:{self.__str}")

    def __str__(self) -> str:
        return self.__str


def capture_function(string: str, pack_global: PackGlobal) -> Tuple[List[Function], str]:
    """Take string of jmc and return a tuple which include list of Function object and left-over jmc string"""

    jmcfunctions_match: List[re.Match] = re.finditer(
        FUNCTION_REGEX, string)
    jmcfunctions: List[Function] = []
    for jmcfunction in jmcfunctions_match:
        jmcfunctions.append(Function(*jmcfunction.groups(), pack_global))
    return jmcfunctions, re.sub(FUNCTION_REGEX, '', string).lstrip()
