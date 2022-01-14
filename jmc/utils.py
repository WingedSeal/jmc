import logging
import re
from typing import Tuple
import regex

from . import Logger, PackGlobal

logger = Logger(__name__)


def clean_whitespace(string: str) -> str:
    """Replace whitespaces with space and return it"""
    logger.info("Cleaning whitespace")
    return re.sub(r"\s+", " ", string + ' ')


def clean_comments(string: str) -> str:
    """Delete everything that starts with # or // until the end of the line"""
    logger.info("Cleaning comments")
    return re.sub(r"#.*|\/\/.*", "", string)


class BracketRegex:
    """Store groups data and process it for later use 
    Throw away unused groups of match_bracket with method 'compile'
    """
    match_bracket_count = 0

    def __init__(self) -> None:
        self.remove_list = []

    def compile(self, strings: Tuple[str]) -> Tuple[str]:
        """Process tuple from groups()
        Example:
        ```
        groups = bracket_regex.compile(regex.search(pattern, string).groups())
        ```
        Args:
            strings (Tuple[str]): re.Match.groups()

        Returns:
            Tuple[str]: Delete all unused string in tuple
        """
        strings = list(strings)
        logger.debug(f'BracketRegex - strings - {strings}')
        logger.debug(f'BracketRegex - indexes - {self.remove_list}')
        for index in sorted(self.remove_list, reverse=True):
            del strings[index-1]
        return tuple(strings)

    def match_bracket(self, bracket: str, start_group: int) -> str:
        """Generate regex for matching bracket, need to be used with BracketRegex
        Example:
        ```
        pattern = '(group1)' + bracket_regex.match_bracket('()', 2) + '(group3)' + bracket_regex.match_bracket('{}', 4)
        ```

        Args:
            bracket (str): A string with length of 2, containing openning and closing of that bracket type. For example `{}`
            start_group (int): A group(start at 1) which match_bracket should be. (Assuming 1 match_bracket use up 1 group)

        Returns:
            str: Regex pattern for matching brackets
        """
        start_group += self.match_bracket_count * 3
        self.match_bracket_count += 1
        self.remove_list += [start_group, start_group+2, start_group+3]
        return f'(\\{bracket[0]}((?:(?:(["\'])(?:(?=(\\\\?))\\{start_group+3}.)*?\\{start_group+2}|[^{bracket[1]}{bracket[0]}])+|(?{start_group}))*+)\\{bracket[1]})'
