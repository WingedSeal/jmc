from tokenize import group
import regex
import re
from typing import TYPE_CHECKING

from .utils import BracketRegex, Re, split
from .flow_control.function_ import Function
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
        self.built_in_functions()
        self.custom_syntax()

        logger.debug(f"Command created:\nText: {self.command}")

    def __repr__(self) -> str:
        return self.command

    def built_in_functions(self) -> None:
        
        bracket_regex = BracketRegex()
        def to_string(match: re.Match, bracket_regex: BracketRegex) -> str:
            groups = bracket_regex.compile(match.groups())
            var = groups[0]
            arguments = split(groups[1])
            raw_json = ""
            for argument in arguments:
                key, value = split(argument, '=')
                raw_json += f',"{key}":{value}'
            return f'{{"score":{{"name":"{var}","objective":"__variable__"}}{raw_json}}}'
        self.command = regex.sub(
            f'{Re.var}.toString{bracket_regex.match_bracket("()", 2)}', lambda match: to_string(match, bracket_regex), self.command)
        
        bracket_regex = BracketRegex()
        def rightclick_setup(match: re.Match, bracket_regex: BracketRegex) -> str:
            id_name, func_json = split(bracket_regex.compile(match.groups())[0])
            if not self.datapack.booleans["rc_detection"]:
                self.datapack.booleans["rc_detection"] = True
                self.datapack.loads.append('scoreboard objectives add __rc__ minecraft.used:minecraft.carrot_on_a_stick')
                self.datapack.ticks.append(f'execute as @a[scores={{__rc__=1..}}] at @s run function {self.datapack.namespace}:__private__/rc_detection/main')
                self.datapack.private_functions["rc_detection"]["main"] = Function(self.datapack.process_function_content("scoreboard players reset @s __rc__;"))
            
            commands = f"execute store result score __item_id__ __variable__ run data get entity @s SelectedItem.tag.{id_name};"

            funcs = split(re.sub(r'{(.*)}', r'\1', func_json))
            for func in funcs:
                bracket_regex = BracketRegex()
                match: re.Match = regex.match(r'(\d+)\s*:\s*\(\)\s*=>\s*' + bracket_regex.match_bracket('{}', 2), func)
                id_, content = bracket_regex.compile(match.groups())
                count = self.datapack.get_pfc("rc_detection")
                self.datapack.private_functions["rc_detection"][count] = Function(self.datapack.process_function_content(content))
                commands += f" execute if score __item_id__ __variable__ matches {id_} run function {self.datapack.namespace}:__private__/rc_detection/{count};"

            self.datapack.private_functions["rc_detection"]["main"].commands.extend(
                self.datapack.process_function_content(commands)
            )
            return ""

        self.command = regex.sub(
            f'RightClick.setup{bracket_regex.match_bracket("()", 1)}', lambda match: rightclick_setup(match, bracket_regex), self.command)


    def function_call(self) -> str:
        def call(match: re.Match) -> str:
            groups = match.groups()
            return f'{groups[0]}function {self.datapack.namespace}:{groups[1].replace(".", "/").lower()}'
        self.command = re.sub(Re.function_call, call, self.command)

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
        print(f'{Re.start_var}\s*+=\s*{Re.integer}')
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
