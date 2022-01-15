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


def condition(string: str) -> str:
    """Turn variable conditions into `if score`"""
    def equal_int(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ matches {groups[1]}'
    string, success = re.subn(
        f'^{Re.var} ?(?:==|=) ?{Re.integer}$', equal_int, string)
    if success:
        return string

    def equal_range(match: re.Match) -> str:
        groups = match.groups()
        start = groups[1] if groups[1] is not None else ''
        end = groups[2] if groups[2] is not None else ''
        return f'score {groups[0]} __variable__ matches {start}..{end}'
    string, success = re.subn(
        f'^{Re.var} ?(?:==|=) ?{Re.match_range}$', equal_range, string)
    if success:
        return string

    def more_than_int(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ matches {int(groups[1])+1}..'
    string, success = re.subn(
        f'^{Re.var} ?> ?{Re.integer}$', more_than_int, string)
    if success:
        return string

    def less_than_int(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ matches ..{int(groups[1])-1}'
    string, success = re.subn(
        f'^{Re.var} ?< ?{Re.integer}$', less_than_int, string)
    if success:
        return string

    def more_than_eq_int(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ matches {groups[1]}..'
    string, success = re.subn(
        f'^{Re.var} ?>= ?{Re.integer}$', more_than_eq_int, string)
    if success:
        return string

    def less_than_eq_int(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ matches ..{groups[1]}'
    string, success = re.subn(
        f'^{Re.var} ?<= ?{Re.integer}$', less_than_eq_int, string)
    if success:
        return string

    def operation_var(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ {groups[1]} {groups[2]} __variable__'
    string, success = re.subn(
        f'^{Re.var} ?(<|<=|=|>=|>) ?{Re.var}$', operation_var, string)
    if success:
        return string

    def equal_var(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ = {groups[1]} __variable__'
    string, success = re.subn(
        f'^{Re.var} ?== ?{Re.var}$', equal_var, string)
    if success:
        return string

    return string


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


class Re:
    integer = r'([-+]?[0-9]+)'
    match_range = r'([-+]?[0-9]+)?..([-+]?[0-9]+)?'
    var = r'(\$[a-zA-Z._]+)'
    var_nosigncap = r'\$([a-zA-Z._]+)'
    operator_noequal = r'([+\-*\/%]=)'
    operator_equal = r'([+\-*\/%]?=)'
    function_call = r'([\w\.]+)\(\)'
    condition_operator = r'(<|<=|=|>=|>)'
