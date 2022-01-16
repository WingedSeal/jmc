

from typing import Tuple

from .utils import BracketRegex, condition
from .pack_global import PackGlobal
import regex
import re
from . import Logger
import logging

logger = Logger(__name__)

bracket_regex = BracketRegex()
WHILE_REGEX = f"while ?{bracket_regex.match_bracket('()', 1)} ?{bracket_regex.match_bracket('{}', 2)}"


class While:
    def __init__(self, groups: Tuple[str], pack_global: PackGlobal) -> None:
        from .function import Function
        logger.info('While created')

        _condition = condition(groups[0])
        counter = pack_global.get_pfc("while_loop")
        self.output = f'execute if {_condition} run function {pack_global.namespace}:__private__/while_loop/{counter};'
        pack_global.functions[f'__private__.while_loop.{counter}'] = Function(
            f'__private__.while_loop.{counter}',
            f'{groups[1]} execute if {_condition} run function {pack_global.namespace}:__private__/while_loop/{counter};',
            pack_global)


def capture_while_loop(string: str, pack_global: PackGlobal) -> str:
    """Take string of jmc and return leftover jmc_string, and add while to pack_global"""
    logger.info("Capturing While loop")
    for jmcfunction in regex.finditer(WHILE_REGEX, string):
        jmcfunction: re.Match
        _while = While(bracket_regex.compile(
            jmcfunction.groups()), pack_global)
        logger.debug(f'While.output\n{_while.output}')
        string = regex.sub(WHILE_REGEX, f' {_while.output} ', string, count=1)
    return string
