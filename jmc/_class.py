import logging
from typing import List, Tuple

from . import Logger
from .function import FUNCTION_REGEX
import re
import regex

CLASS_REGEX = r'class ([\w\._]+) ({(?:(?:(["\'])(?:(?=(\\?))\4.)*?\3|[^}{])+|(?2))*+})'
logger = Logger(__name__)


def replace_class(string: str) -> str:
    logger.info(f"Replacing classes")

    def handle_class(match: re.Match) -> str:
        """Split class into class_name and class_context and then parse class_context
        returns parsed string"""
        groups = match.groups()
        class_name = groups[0]
        logger.debug(f"Class_name: {class_name}")

        def strip_bracket(match: re.Match) -> str:
            return match.groups()[0]
        string = re.sub(r'{ (.*) }', strip_bracket, groups[1])

        def replace_function(match: re.Match) -> str:
            """Replace function_name with class_name.function_name"""
            groups = match.groups()
            return f'function {class_name}.{groups[0]}({groups[1]}) {groups[2]}'
        string = regex.sub(FUNCTION_REGEX, replace_function, string)

        # def replace_variable(match: re.Match) -> str:
        #     """Replace $varname with $class_name.varname"""
        #     return f'${class_name}.{groups()[0]}'
        # string = regex.sub(r'$([\w\._]+)', replace_variable, string)
        return string
    string = regex.sub(CLASS_REGEX, handle_class, string)
    logger.debug(f"Returns\n{string}")
    return string
