import logging
from typing import List, Tuple

from . import Logger
from . import function
from .utils import BracketRegex
import re
import regex

bracket_regex = BracketRegex()
CLASS_REGEX = r'class ([\w\._]+) ' + bracket_regex.match_bracket('{}', 2)
logger = Logger(__name__)


def replace_class(string: str) -> str:
    logger.info(f"Replacing classes")

    def handle_class(match: re.Match) -> str:
        """Split class into class_name and class_context and then parse class_context
        returns parsed string"""
        groups = bracket_regex.compile(match.groups())
        class_name = groups[0]
        logger.debug(f"Class_name: {class_name}")

        def replace_function(match: re.Match) -> str:
            """Replace function_name with class_name.function_name"""
            groups = function.bracket_regex.compile(match.groups())
            return f'function {class_name}.{groups[0]}() {{{groups[1]}}}'
        string = regex.sub(function.FUNCTION_REGEX,
                           replace_function, groups[1])

        return string

    string = regex.sub(CLASS_REGEX, handle_class, string)
    logger.debug(f"Returns\n{string}")
    return string
