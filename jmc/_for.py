

from typing import Tuple

from jmc.function import Function
from .utils import BracketRegex, condition, Re
from .pack_global import PackGlobal
import regex
import re
from . import Logger
import logging

logger = Logger(__name__)

bracket_regex = BracketRegex()
FOR_REGEX = f"for ?{bracket_regex.match_bracket('()', 1)} ?{bracket_regex.match_bracket('{}', 2)}"


class For:
    def __init__(self, groups: Tuple[str], pack_global: PackGlobal) -> None:
        logger.info('For created')
        arguments = [argument.strip() for argument in groups[0].split(';')]
        arguments[0] = regex.match(
            f'let {Re.var_nosigncap} ?= ?{Re.integer}', arguments[0]).groups()
        arguments[1] = condition(arguments[1].replace(
            f'${arguments[0][0]}', f'$__private__.{arguments[0][0]}'))
        context = groups[1].replace(
            f'${arguments[0][0]}', f'$__private__.{arguments[0][0]}')
        self.__output = [
            f'scoreboard players set $__private__.{arguments[0][0]} __variable__ {arguments[0][1]};',
            f'execute if {arguments[1]} run function {pack_global.namespace}:__private__/for_loop/{pack_global.get_pfc("for_loop")};'
        ]
        pack_global.functions[f'__private__.for_loop.{pack_global.private_functions_count["for_loop"]}'] = Function(
            f'__private__.for_loop.{pack_global.private_functions_count["for_loop"]}',
            f'{groups[1]} execute if {arguments[1]} run function {pack_global.namespace}:__private__/for_loop/{pack_global.private_functions_count["for_loop"]}; {arguments[2]};',
            pack_global)

    @property
    def output(self) -> str:
        return ' '.join(self.__output)


def capture_for_loop(string: str, pack_global: PackGlobal) -> str:
    """Take string of jmc and return leftover jmc_string, and add while to pack_global"""
    logger.info("Capturing For loop")
    for jmcfunction in regex.finditer(FOR_REGEX, string):
        jmcfunction: re.Match
        _for = For(bracket_regex.compile(
            jmcfunction.groups()), pack_global)
        logger.debug(f'For.output\n{_for.output}')
        string = regex.sub(FOR_REGEX, f' {_for.output} ', string, count=1)
    return string
