import logging
from typing import List, Tuple
import re

from . import Logger, LoadJson

FUNCTION_REGEX = r'function (\w+)\(([\w, ]+)\) \{ ([^)(]+|\{(?:[^)(]+|\{[^)(]*\})*\})*\}'
logger = Logger(__name__, logging.DEBUG)


class Function:
    def __init__(self, name: str, params: str, context: str, load_json: LoadJson) -> None:
        self.name = name
        self.params = params.replace(' ', '').split(',')
        self.context = [command for command in context.split(
            '; ') if command]  # Remove empty command

        logger.debug(f"""Function created:
        NAME: {self.name}
        PARAMS: {self.params}
        CONTEXT: {self.context}""")

    def __str__(self) -> str:
        return f"""
        NAME: {self.name}
        PARAMS: {self.params}
        CONTEXT: {self.context}
        """


def capture_function(string: str, load_json: LoadJson) -> Tuple[List[Function], str]:
    """Take string of jmc and return a tuple which include list of Function object and left-over jmc string"""

    jmcfunctions_match: List[re.Match] = re.finditer(
        FUNCTION_REGEX, string)
    jmcfunctions: List[Function] = []
    for jmcfunction in jmcfunctions_match:
        jmcfunctions.append(Function(*jmcfunction.groups(), load_json))
        load_json.scoreboards.add('TEST')  # TODO: Remove Later
