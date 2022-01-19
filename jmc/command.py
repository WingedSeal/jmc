import regex
import re
from typing import TYPE_CHECKING

from .utils import BracketRegex, Re, split
from . import Logger

if TYPE_CHECKING:
    from . import DataPack

logger = Logger(__name__)


class Command:
    def __init__(self, command: str, datapack: "DataPack") -> None:
        self.datapack = datapack
        logger.debug(f"Command - Input: {command}")
        if command.startswith('say'):
            self.command = command

        else:
            say_command = split(command, 'say')
            self.command = " ".join(split(say_command[0], ' '))
            if len(say_command) > 1:
                self.command += f' say {say_command[1]}'

        logger.debug(f"Command - Delete whitespaces: {command}")
        self.function_call()
        self.built_in_functions()
        self.custom_syntax()

        logger.debug(f"Command created:\nText: {self.command}")

    def __repr__(self) -> str:
        return self.command

    def built_in_functions(self) -> None:
        bracket_regex = BracketRegex()

        def to_string(match: re.Match) -> str:
            groups = bracket_regex.compile(match.groups())
            var = groups[0]
            arguments = split(groups[1])
            raw_json = ""
            for argument in arguments:
                key, value = split(argument, '=')
                raw_json += f',"{key}":{value}'
            return f'{{"score":{{"name":"{var}","objective":"__variable__"}}{raw_json}}}'

        self.command = regex.sub(
            f'{Re.var}.toString{bracket_regex.match_bracket("()", 2)}', to_string, self.command)

    def function_call(self) -> str:
        def call(match: re.Match) -> str:
            groups = match.groups()
            return f'{groups[0]}function {self.datapack.namespace}:{groups[1].replace(".", "/").lower()}'
        self.command = re.sub(Re.function_call, call, self.command)

    def custom_syntax(self) -> None:
        def increment(match: re.Match) -> str:
            groups = match.groups()
            return f'{groups[0]}+=1'
        self.command = re.sub(
            f'{Re.start_var}\+\+', increment, self.command)

        def decrement(match: re.Match) -> str:
            groups = match.groups()
            return f'{groups[0]}-=1'
        self.command = re.sub(
            f'{Re.start_var}--', decrement, self.command)

        def equal_int(match: re.Match) -> str:
            groups = match.groups()
            return f'scoreboard players set {groups[0]} __variable__ {int(groups[1])}'
        self.command = re.sub(
            f'{Re.start_var}\s*=\s*{Re.integer}', equal_int, self.command)

        def operator_int(match: re.Match) -> str:
            groups = match.groups()
            self.datapack.ints.add(int(groups[2]))
            return f'scoreboard players operation {groups[0]} __variable__ {groups[1]} {groups[2]} __int__'
        self.command = re.sub(f'{Re.start_var}\s*{Re.operator_noequal}\s*{Re.integer}',
                              operator_int, self.command)

        def operator_var(match: re.Match) -> str:
            groups = match.groups()
            return f'scoreboard players operation {groups[0]} __variable__ {groups[1]} {groups[2]} __variable__'
        self.command = re.sub(f'{Re.start_var}\s*{Re.operator_equal}\s*{Re.var}',
                              operator_var, self.command)

        def var_declare(match: re.Match) -> str:
            groups = match.groups()
            return f'{groups[0]}scoreboard players add {groups[1]} __variable__ 0'
        self.command = re.sub(
            f'{Re.start_cmd}let\s*{Re.var}', var_declare, self.command)

    def __str__(self) -> str:
        return self.command
