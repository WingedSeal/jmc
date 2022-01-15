

from typing import Tuple

from .utils import BracketRegex, condition
from .pack_global import PackGlobal
import regex
import re
from . import Logger
import logging

logger = Logger(__name__)

bracket_regex = BracketRegex()
IFELSE_REGEX = f"if ?{bracket_regex.match_bracket('()', 1)} ?{bracket_regex.match_bracket('{}', 2)}((?: else if ?{bracket_regex.match_bracket('()', 4)} ?{bracket_regex.match_bracket('{}', 5)})*)(?: else ?{bracket_regex.match_bracket('{}', 6)})?"


class IfElse:
    def __init__(self, groups: Tuple[str], pack_global: PackGlobal) -> None:
        from .function import Function
        logger.info('IfElse created')
        if groups[-1] is None and groups[2] == '':  # No `else`, No `else if`
            self.__output = [
                f'execute if {condition(groups[0])} run function {pack_global.namespace}:__private__/if_else/{pack_global.get_pfc("if_else")};']
            pack_global.functions[f'__private__.if_else.{pack_global.private_functions_count["if_else"]}'] = Function(
                f'__private__.if_else.{pack_global.private_functions_count["if_else"]}',
                groups[1],
                pack_global)
            return

        self.__output = [
            'scoreboard players set __tmp__ __variable__ 0;',
            f'execute if {condition(groups[0])} run function {pack_global.namespace}:__private__/if_else/{pack_global.get_pfc("if_else")};',
        ]
        pack_global.functions[f'__private__.if_else.{pack_global.private_functions_count["if_else"]}'] = Function(
            f'__private__.if_else.{pack_global.private_functions_count["if_else"]}',
            f'{groups[1]} scoreboard players set __tmp__ __variable__ 1;',
            pack_global)

        if groups[2] != '':  # There's `else if`
            else_if_chain = groups[2].split(' else if ')[1:]
            for else_if in else_if_chain:
                bracket_regex = BracketRegex()
                pattern = f"{bracket_regex.match_bracket('()', 1)} {bracket_regex.match_bracket('{}', 2)}"
                else_if_groups = bracket_regex.compile(
                    regex.match(pattern, else_if).groups())
                self.__output.append(
                    f'execute if score __tmp__ __variable__ matches 0 if {condition(else_if_groups[0])} run function {pack_global.namespace}:__private__/if_else/{pack_global.get_pfc("if_else")};')
                pack_global.functions[f'__private__.if_else.{pack_global.private_functions_count["if_else"]}'] = Function(
                    f'__private__.if_else.{pack_global.private_functions_count["if_else"]}',
                    f'{else_if_groups[1]} scoreboard players set __tmp__ __variable__ 1;',
                    pack_global)

        if groups[-1] is not None:  # There's `else`
            self.__output.append(
                f'execute if score __tmp__ __variable__ matches 0 run function {pack_global.namespace}:__private__/if_else/{pack_global.get_pfc("if_else")};')
            pack_global.functions[f'__private__.if_else.{pack_global.private_functions_count["if_else"]}'] = Function(
                f'__private__.if_else.{pack_global.private_functions_count["if_else"]}',
                f'{groups[-1]} scoreboard players set __tmp__ __variable__ 1;',
                pack_global)

    @property
    def output(self) -> str:
        return " ".join(self.__output)


def capture_if_else(string: str, pack_global: PackGlobal) -> str:
    """Take string of jmc and return leftover jmc_string, and add ifelse to pack_global"""
    logger.info("Capturing If Else")
    for jmcfunction in regex.finditer(IFELSE_REGEX, string):
        jmcfunction: re.Match
        if_else = IfElse(bracket_regex.compile(
            jmcfunction.groups()), pack_global)
        logger.debug(f'IfElse.output\n{if_else.output}\n')
        string = regex.sub(IFELSE_REGEX, f' {if_else.output} ', string)
    return string
