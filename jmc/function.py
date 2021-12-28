import logging
from typing import List, Tuple

from . import Logger, PackGlobal
from .command import Command
import re
import regex

FUNCTION_REGEX = r'function ([\w\._]+)\(([\w, ]*)\) { ((?:[^}{}]+|(?R))*+)}'
logger = Logger(__name__, logging.INFO)


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
    Contexts (Commands): 
    {nl.join([str(command) for command in self.context])}
        """
        logger.debug(f"Function created:{self.__str}")

    def __str__(self) -> str:
        return self.__str


def capture_function(string: str, pack_global: PackGlobal) -> Tuple[List[Function], str]:
    """Take string of jmc and return a tuple which include list of Function object and left-over jmc string"""
    logger.info("Capturing Functions")
    logger.debug('\n\n\n\n'+string+'\n\n\n\n')
    jmcfunctions_match: List[re.Match] = regex.finditer(
        FUNCTION_REGEX, string)
    jmcfunctions: List[Function] = []
    for jmcfunction in jmcfunctions_match:
        logger.debug(f"Function found: {jmcfunction.groups()[0]}")
        jmcfunctions.append(Function(*jmcfunction.groups(), pack_global))
    return jmcfunctions, regex.sub(FUNCTION_REGEX, '', string).lstrip()
    # TODO: Please fix this, it fails to capture stuff and for some reason the string was cut off before this


def replace_function_call(string: str, pack_global: PackGlobal) -> str:
    """Replace `<functionName>()` with `function <namespace>:<functionName>`"""
    def mcfunction(match: re.Match) -> str:
        return f'function {pack_global.namespace}:{match.groups()[0].replace(".", "/")}'
    string = re.sub(
        r'([\w\.]+)\(\)', mcfunction, string)
    return string
