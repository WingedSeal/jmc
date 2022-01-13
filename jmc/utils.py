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


def custom_syntax(string: str, pack_global: PackGlobal) -> str:
    """Replace jmc syntax with mcfunction and return it"""
    logger.info("Handling custom syntax")

    def capture_var_assign(match: re.Match) -> str:
        """$<variable> = <integer>;

        Args:
            match (re.Match)

        Returns:
            str: 'scoreboard players set <variable> __variable__ <integer>'
        """
        groups = match.groups()
        rv = f'scoreboard players set {groups[0]} __variable__ {int(groups[1])}'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = re.sub(r'(\$\w+) = ([-+]?[0-9]+)', capture_var_assign, string)

    def capture_var_declare(match: re.Match) -> str:
        """$<variable>;

        Args:
            match (re.Match)

        Returns:
            str: 'scoreboard players add $<variable> __variable__ 0'
        """
        groups = match.groups()
        rv = f'scoreboard players add {groups[0]} __variable__ 0;'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = re.sub(r'(\$\w+);', capture_var_declare, string)

    def capture_var_operation(match: re.Match) -> str:
        """$<variable: target> <operations> <integer>;
        operations: +=, -=, *=, /=, %=

        Args:
            match (re.Match)

        Returns:
            str: 'scoreboard players operations <target> __variable__ <operations> <integer> __int__'
        """
        groups = match.groups()
        pack_global.ints.add(int(groups[2]))
        rv = f'scoreboard players operation {groups[0]} __variable__ {groups[1]}= {groups[2]} __int__'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = re.sub(r'(\$\w+) ([+\-\*/%])= ([-+]?[0-9]+)',
                    capture_var_operation, string)

    def capture_var_equal(match: re.Match) -> str:
        """$<variable> = $<variable>;

        Args:
            match (re.Match)

        Returns:
            str: scoreboard players operations <target> __variable__ = <source> __variable__
        """
        groups = match.groups()
        rv = f'scoreboard players operation {groups[0]} __variable__ = {groups[1]}'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = re.sub(r'(\$\w+) = (\$\w+)', capture_var_equal, string)

    def capture_var_operation_var(match: re.Match) -> str:
        """$<target: variable> <operations> $<source: variable>;

        Args:
            match (re.Match)

        Returns:
            str: 'scoreboard players operations <target> __variable__ <operations> <source> __variable__'
        """
        groups = match.groups()
        rv = f'scoreboard players operation {groups[0]} __variable__ {groups[1]}= {groups[2]} __variable__'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = re.sub(r'(\$\w+) ([+\-\*/%])= (\$\w+)',
                    capture_var_operation_var, string)

    def capture_to_string(match: re.Match) -> str:
        """$<variable>.toString([<key>=(<value>|"<value>")])

        Args:
            match (re.Match)

        Returns:
            str: `{"score":{"name":"$<variable>","objective":"__variable__"},"key":(<value>|"<value>")}`
        """
        groups = match.groups()
        if groups[1] != "":
            styles = groups[1].replace(' ', '').split(',')
            for i, style in enumerate(styles):
                style = style.split('=')
                styles[i] = f'"{style[0]}":{style[1]}'
            styles = ', '.join(['']+styles)
        else:
            styles = ''
        styles: str
        rv = f'{{"score":{{"name":"{groups[0]}","objective":"variable"}}{styles}}}'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = regex.sub(r'(\$\w+)\.toString\(((?:[^)(]+|(?R))*+)\)',
                       capture_to_string, string)

    return string


def replace_function_call(command_text: str, pack_global: PackGlobal) -> str:
    """Replace `<functionName>()` with `function <namespace>:<functionName>` in command"""
    def mcfunction(match: re.Match) -> str:
        return f'function {pack_global.namespace}:{match.groups()[0].replace(".", "/").lower()}'
    command_text = re.sub(
        r'([\w\.]+)\(\)', mcfunction, command_text)
    return command_text


class BracketRegex:
    """Store groups data and process it for later use 
    Throw away unused groups of match_bracket with method 'compile'
    """
    match_bracket_count = 0
    remove_list = []

    def __init__(self) -> None:
        pass

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
