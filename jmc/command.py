import regex
import re
from typing import TYPE_CHECKING

from .utils import BracketRegex, Re, split
from .flow_control.function_ import Function
from .flow_control.condition import Condition
from . import Logger

if TYPE_CHECKING:
    from . import DataPack

logger = Logger(__name__)


class Command:
    from .builtin_function import built_in_functions
    def __init__(self, command: str, datapack: "DataPack") -> None:
        self.datapack = datapack
        logger.debug(f"Command - Input: {command}")
        if command.startswith('say'):
            self.command = command

        else:
            say_command = split(command, 'say')
            def replace_whitespace(match: re.Match) -> str:
                groups = match.groups()
                if groups[2] is None:
                    return match.group(0)
                return " "
            self.command = re.sub(r"(\\*[\"'])((?:\\{2})*|(?:.*?[^\\](?:\\{2})*))\1|(\s+)", replace_whitespace, say_command[0])
            if len(say_command) > 1:
                self.command += f' say {say_command[1]}'

        logger.debug(f"Command - Delete whitespaces: {command}")
        self.function_call()
        self.do_while_loop()
        self.built_in_functions()
        self.custom_syntax()

        logger.debug(f"Command created:\nText: {self.command}")

    def __repr__(self) -> str:
        return self.command


    def function_call(self) -> str:
        def call(match: re.Match) -> str:
            groups = match.groups()
            return f'{groups[0]}function {self.datapack.namespace}:{groups[1].replace(".", "/").lower()}'
        self.command = re.sub(Re.function_call, call, self.command)

    def do_while_loop(self) -> str:
        def loop(match: re.Match, bracket_regex: BracketRegex) -> str:
            groups = bracket_regex.compile(match.groups())
            condition = Condition(groups[1])
            count = self.datapack.get_pfc("do_while_loop")
            self.datapack.private_functions["do_while_loop"][count] = Function(self.datapack.process_function_content(
                f"{groups[0]} {condition.pre_commands}execute{condition} run function {self.datapack.namespace}:__private__/do_while_loop/{count};"
            ))
            return f'function {self.datapack.namespace}:__private__/do_while_loop/{count}'
        
        bracket_regex = BracketRegex()
        do_while_regex = f"do\\s*{bracket_regex.match_bracket('{}', 1)}\\s*while\\s*{bracket_regex.match_bracket('()', 2)}"
        self.command = regex.sub(do_while_regex, lambda match: loop(match, bracket_regex), self.command)

    def custom_syntax(self) -> None:
        def increment(match: re.Match) -> str:
            groups = match.groups()
            return f'scoreboard players add {groups[0]} __variable__ 1'
        self.command = re.sub(
            f'{Re.start_var}\+\+', increment, self.command)

        def decrement(match: re.Match) -> str:
            groups = match.groups()
            return f'scoreboard players remove {groups[0]} __variable__ 1'
        self.command = re.sub(
            f'{Re.start_var}--', decrement, self.command)

        def equal_int(match: re.Match) -> str:
            groups = match.groups()
            return f'scoreboard players set {groups[0]} __variable__ {int(groups[1])}'
        self.command = re.sub(
            f'{Re.start_var}\s*=\s*{Re.integer}', equal_int, self.command)

        def add_int(match: re.Match) -> str:
            groups = match.groups()
            return f'scoreboard players add {groups[0]} __variable__ {groups[1]}'
        self.command = re.sub(f'{Re.start_var}\s*\+=\s*{Re.integer}',
                              add_int, self.command)
        
        def remove_int(match: re.Match) -> str:
            groups = match.groups()
            return f'scoreboard players remove {groups[0]} __variable__ {groups[1]}'
        self.command = re.sub(f'{Re.start_var}\s*\-=\s*{Re.integer}',
                              remove_int, self.command)

        def operator_int(match: re.Match) -> str:
            groups = match.groups()
            self.datapack.ints.add(int(groups[2]))
            return f'scoreboard players operation {groups[0]} __variable__ {groups[1]} {groups[2]} __int__'
        self.command = re.sub(f'{Re.start_var}\s*{Re.operator_int}\s*{Re.integer}',
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

        def anonymous_function(match: re.Match, bracket_regex: BracketRegex) -> str:
            content = bracket_regex.compile(match.groups())[0]
            count = self.datapack.get_pfc("anonymous_function")
            self.datapack.private_functions["anonymous_function"][count] = Function(self.datapack.process_function_content(content))
            return f'run function {self.datapack.namespace}:__private__/anonymous_function/{count}'
        
        bracket_regex = BracketRegex()
        self.command = regex.sub(f'run {bracket_regex.match_bracket("{}", 1)}', lambda match: anonymous_function(match, bracket_regex), self.command)

    def __str__(self) -> str:
        return self.command
