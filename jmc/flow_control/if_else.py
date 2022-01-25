import regex
import re
from typing import TYPE_CHECKING

from ..utils import BracketRegex, split
from .condition import Condition
from .function_ import Function
from .. import Logger

if TYPE_CHECKING:
    from ..datapack import DataPack

logger = Logger(__name__)

bracket_regex = BracketRegex()
IFELSE_REGEX = f"if\\s*{bracket_regex.match_bracket('()', 1)}\\s*{bracket_regex.match_bracket('{}', 2)}((?:\\s*else\\s+if\\s*{bracket_regex.match_bracket('()', 4)}\\s*{bracket_regex.match_bracket('{}', 5)})*)(?:\\s*else\\s*{bracket_regex.match_bracket('{}', 6)})?"


def capture_if_else(self: "DataPack", line: str) -> tuple[str, bool]:

    line = line.strip()

    def if_else_found(match: re.Match):
        logger.debug("If/Else found")
        groups = bracket_regex.compile(match.groups())
        return handle_if_else(self, groups)
    line, success = regex.subn(IFELSE_REGEX, if_else_found, line, count=1)

    return line, success


def handle_if_else(datapack: "DataPack", groups: tuple[str]) -> str:
    logger.debug("Handling If/Else")
    condition = Condition(groups[0])
    if groups[-1] is None and groups[2] == '':  # No `else`, No `else if`
        commands = datapack.process_function_content(groups[1])
        if len(commands) == 1:
            return f'{condition.pre_commands}execute{condition} run {commands[0]};'
        else:
            count = datapack.get_pfc("if_else")
            datapack.private_functions["if_else"][count] = Function(commands)
            return f'{condition.pre_commands}execute{condition} run function {datapack.namespace}:__private__/if_else/{count};'

    count = datapack.get_pfc("if_else")
    outputs = [
        'scoreboard players set __tmp__ __variable__ 0;',
        f'{condition.pre_commands}execute{condition} run function {datapack.namespace}:__private__/if_else/{count};',
    ]

    datapack.private_functions["if_else"][count] = Function(datapack.process_function_content(
        f"{groups[1]} scoreboard players set __tmp__ __variable__ 1;"))

    if groups[2] != '':  # There's `else if`
        else_if_chain = split(groups, r'else\s*if')[2][1:]
        for else_if in else_if_chain:
            bracket_regex = BracketRegex()
            pattern = f"{bracket_regex.match_bracket('()', 1)} {bracket_regex.match_bracket('{}', 2)}"
            else_if_groups = bracket_regex.compile(
                regex.match(pattern, else_if).groups())
            count = datapack.get_pfc("if_else")
            condition = Condition(else_if_groups[0])
            outputs.append(
                f'{condition.pre_commands}execute if score __tmp__ __variable__ matches 0{condition} run function {datapack.namespace}:__private__/if_else/{count};')
            datapack.private_functions["if_else"][count] = Function(datapack.process_function_content(
                f"{groups[1]} scoreboard players set __tmp__ __variable__ 1;"))

    if groups[-1] is not None:  # There's `else`
        count = datapack.get_pfc("if_else")
        outputs.append(
            f'execute if score __tmp__ __variable__ matches 0 run function {datapack.namespace}:__private__/if_else/{count};')
        datapack.private_functions["if_else"][count] = Function(datapack.process_function_content(
            f"{groups[-1]} scoreboard players set __tmp__ __variable__ 1;"))

    return "; ".join(outputs) + ';'
