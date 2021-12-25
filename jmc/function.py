import logging
from typing import List, Tuple
import re

from . import Logger

FUNCTION_REGEX = r'function (\w+)\(([\w, ]+)\) \{ ([^)(]+|\{(?:[^)(]+|\{[^)(]*\})*\})* \}'
logger = Logger(__name__, logging.DEBUG)


class Function:
    def __init__(self, name: str, params: List[str], context: str) -> None:
        pass


def capture_function(string: str) -> Tuple[List[Function], str]:
    """Take string of jmc and return a tuple which include list of Function object and left-over jmc string"""

    jmcfunctions: List[re.Match] = re.finditer(FUNCTION_REGEX, string=string)
    for jmcfunction in jmcfunctions:
        group = jmcfunction.groups()
        logger.debug(f"""
        NAME: {group[0]}
        PARAMS: {group[1]}
        CONTEXT: {group[2]}
        """)
