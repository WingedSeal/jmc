import re
import regex
from . import Logger, PackGlobal
import logging
from .utils import BracketRegex, Re, parse_split

logger = Logger(__name__)


class Command:
    """Datapack function command"""

    def __init__(self, text: str, pack_global: PackGlobal) -> None:
        logger.debug(f"Command - Input: {text}")

        self.string = text.strip()
        self.function_call(pack_global)
        self.built_in_functions()
        self.custom_syntax(pack_global)

        logger.debug(f"Command created:\nText: {self.string}")

    def built_in_functions(self) -> None:
        bracket_regex = BracketRegex()

        def to_string(match: re.Match) -> str:
            groups = bracket_regex.compile(match.groups())
            var = groups[0]
            arguments = parse_split(groups[1])
            raw_json = ""
            for argument in arguments:
                key, value = parse_split(argument, '=')
                raw_json += f',"{key}":{value}'
            return f'{{"score":{{"name":"{var}","objective":"__variable__"}}{raw_json}}}'

        self.string = regex.sub(
            f'{Re.var}.toString{bracket_regex.match_bracket("()", 2)}', to_string, self.string)

    def function_call(self, pack_global: PackGlobal) -> str:
        def call(match: re.Match) -> str:
            groups = match.groups()
            return f'function {pack_global.namespace}:{groups[0].replace(".", "/").lower()}'
        self.string = re.sub(Re.function_call, call, self.string)

    def custom_syntax(self, pack_global: PackGlobal) -> None:
        def increment(match: re.Match) -> str:
            groups = match.groups()
            return f'{groups[0]}+=1'
        self.string = re.sub(
            f'{Re.var}\+\+', increment, self.string)

        def decrement(match: re.Match) -> str:
            groups = match.groups()
            return f'{groups[0]}-=1'
        self.string = re.sub(
            f'{Re.var}--', decrement, self.string)

        def equal_int(match: re.Match) -> str:
            groups = match.groups()
            return f'scoreboard players set {groups[0]} __variable__ {int(groups[1])}'
        self.string = re.sub(
            f'{Re.var} ?= ?{Re.integer}', equal_int, self.string)

        def operator_int(match: re.Match) -> str:
            groups = match.groups()
            pack_global.ints.add(int(groups[2]))
            return f'scoreboard players operation {groups[0]} __variable__ {groups[1]} {groups[2]} __int__'
        self.string = re.sub(f'{Re.var} ?{Re.operator_noequal} ?{Re.integer}',
                             operator_int, self.string)

        def operator_var(match: re.Match) -> str:
            groups = match.groups()
            pack_global.ints.add(int(groups[2]))
            return f'scoreboard players operation {groups[0]} __variable__ {groups[1]} {groups[2]} __variable__'
        self.string = re.sub(f'{Re.var} ?{Re.operator_equal} ?{Re.var}',
                             operator_var, self.string)

        def var_declare(match: re.Match) -> str:
            groups = match.groups()
            return f'scoreboard players add {groups[0]} __variable__ 0'
        self.string = re.sub(f'let ?{Re.var}', var_declare, self.string)

    def __str__(self) -> str:
        return self.string
