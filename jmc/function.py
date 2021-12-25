import logging
from typing import List, Tuple
import re

from . import Logger, LoadJson
from .command import Command

FUNCTION_REGEX = r'function (\w+)\(([\w, ]+)\) \{ ([^)(]+|\{(?:[^)(]+|\{[^)(]*\})*\})*\}'
logger = Logger(__name__, logging.DEBUG)


class Function:
    def __init__(self, name: str, params: str, context: str, load_json: LoadJson) -> None:
        self.name = name
        self.params = params.replace(' ', '').split(',')
        self.context = [Command(command, load_json) for command in context.split(
            '; ') if command]  # Remove empty string command
        load_json.functions_name.add(name)
        self.__str = f"""
        NAME: {self.name}
        PARAMS: {self.params}
        CONTEXT: {[str(command) for command in self.context]}
        """
        logger.debug(self.__str)

    def __str__(self) -> str:
        return self.__str


def capture_function(string: str, load_json: LoadJson) -> Tuple[List[Function], str]:
    """Take string of jmc and return a tuple which include list of Function object and left-over jmc string"""

    jmcfunctions_match: List[re.Match] = re.finditer(
        FUNCTION_REGEX, string)
    jmcfunctions: List[Function] = []
    for jmcfunction in jmcfunctions_match:
        jmcfunctions.append(Function(*jmcfunction.groups(), load_json))
    return jmcfunctions, re.sub(FUNCTION_REGEX, '', string)
