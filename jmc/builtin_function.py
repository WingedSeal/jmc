import regex
import re
from typing import TYPE_CHECKING

from .utils import BracketRegex, Re, split, eval_expr
from .flow_control.function_ import Function
from ast import literal_eval
from . import Logger

if TYPE_CHECKING:
    from . import DataPack
    from .command import Command

logger = Logger(__name__)

def built_in_functions(self: "Command") -> None:
    

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
        f'{Re.var}\\.toString{bracket_regex.match_bracket("()", 2)}', lambda match: to_string(match, bracket_regex), self.command)
    

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
            match: re.Match = regex.match(r'(\d+)\s*:\s*\(\s*\)\s*=>\s*' + bracket_regex.match_bracket('{}', 2), func)
            id_, content = bracket_regex.compile(match.groups())
            
            __commands = self.datapack.process_function_content(content)
            if len(__commands) == 1:
                commands += f" execute if score __item_id__ __variable__ matches {id_} run {__commands[0].command};"
            else:
                count = self.datapack.get_pfc("rc_detection")
                self.datapack.private_functions["rc_detection"][count] = Function(__commands)
                commands += f" execute if score __item_id__ __variable__ matches {id_} run function {self.datapack.namespace}:__private__/rc_detection/{count};"

        self.datapack.private_functions["rc_detection"]["main"].commands.extend(
            self.datapack.process_function_content(commands)
        )
        return ""

    self.command = regex.sub(
        f'RightClick\\.setup{bracket_regex.match_bracket("()", 1)}', lambda match: rightclick_setup(match, bracket_regex), self.command)


    bracket_regex = BracketRegex()
    def player_first_join(match: re.Match, bracket_regex: BracketRegex) -> str:
        content = bracket_regex.compile(match.groups())[0]
        count = self.datapack.get_pfc("player_first_join")
        self.datapack.news["advancements"][f"__private__/player_first_join/{count}"] = {
            "criteria": {
                "requirement": {
                "trigger": "minecraft:tick"
                }
            },
            "rewards": {
                "function": f"{self.datapack.namespace}:__private__/player_first_join/{count}"
            }
        }
        self.datapack.private_functions["player_first_join"][count] = Function(self.datapack.process_function_content(content))
        return ""
        
    self.command = regex.sub(
        r'Player.firstJoin\(\s*\(\s*\)\s*=>\s*'+f'{bracket_regex.match_bracket("{}", 1)}\\s*\\)', lambda match: player_first_join(match, bracket_regex), self.command
    )
        
    bracket_regex = BracketRegex()
    def player_rejoin(match: re.Match, bracket_regex: BracketRegex) -> str:
        content = bracket_regex.compile(match.groups())[0]
        if not self.datapack.booleans["player_rejoin"]:
            self.datapack.booleans["player_rejoin"] = True
            self.datapack.loads.append('scoreboard objectives add __rejoin__ minecraft.custom:minecraft.leave_game')
            self.datapack.ticks.append(f'execute as @a[scores={{__rejoin__=1..}}] at @s run function {self.datapack.namespace}:__private__/player_rejoin/main')
            self.datapack.private_functions["player_rejoin"]["main"] = Function(self.datapack.process_function_content("scoreboard players reset @s __rejoin__;"))

        commands = self.datapack.process_function_content(content)
        if len(commands) == 1:
            self.datapack.private_functions["player_rejoin"]["main"].commands.extend(commands)
        else:
            count = self.datapack.get_pfc("player_rejoin")
            self.datapack.private_functions["player_rejoin"][count] = Function(commands)
            self.datapack.private_functions["player_rejoin"]["main"].commands.extend(self.datapack.process_function_content(f"function {self.datapack.namespace}:__private__/player_rejoin/{count}"))
        return ""

    self.command = regex.sub(
        r'Player.rejoin\(\s*\(\s*\)\s*=>\s*'+f'{bracket_regex.match_bracket("{}", 1)}\\s*\\)', lambda match: player_rejoin(match, bracket_regex), self.command
    )

    def math_sqrt(match: re.Match) -> str:
        groups = match.groups()
        if not self.datapack.booleans["math_sqrt"]:
            self.datapack.booleans["math_sqrt"] = True
            self.datapack.ints.add(2)
            self.datapack.private_functions["math"]["sqrt_newton_raphson"] = Function(self.datapack.process_function_content(f"""
                scoreboard players operation __math__.x __variable__ = __math__.x_n __variable__;
                scoreboard players operation __math__.x_n __variable__ = __math__.N __variable__;
                scoreboard players operation __math__.x_n __variable__ /= __math__.x __variable__;
                scoreboard players operation __math__.x_n __variable__ += __math__.x __variable__;
                scoreboard players operation __math__.x_n __variable__ /= 2 __int__;
                scoreboard players operation __math__.different __variable__ = __math__.x __variable__;
                scoreboard players operation __math__.different __variable__ -= __math__.x_n __variable__;
                execute unless score __math__.different __variable__ matches 0..1 run function {self.datapack.namespace}:__private__/math/sqrt_newton_raphson;
            """))
            self.datapack.private_functions["math"]["sqrt"] = Function(self.datapack.process_function_content(f"""
                scoreboard players set __math__.x_n __variable__ 1225;
                function {self.datapack.namespace}:__private__/math/sqrt_newton_raphson;
                scoreboard players operation __math__.x_n_sq __variable__ = __math__.x_n __variable__;
                scoreboard players operation __math__.x_n_sq __variable__ *= __math__.x_n __variable__;
                execute if score __math__.x_n_sq __variable__ > __math__.N __variable__ run scoreboard players remove __math__.x_n __variable__ 1;
            """))

        return f"""scoreboard players operation __math__.N __variable__ = {groups[1]} __variable__
function {self.datapack.namespace}:__private__/math/sqrt
scoreboard players operation {groups[0]} __variable__ = __math__.x_n __variable__"""
    self.command = regex.sub(
        f'{Re.var}\\s*=\\s*Math\\.sqrt\\({Re.var}\\)', math_sqrt, self.command)


    bracket_regex = BracketRegex()
    def hard_code_repeat(match: re.Match, bracket_regex: BracketRegex) -> str:
        index_str, func, start, stop, step = split(bracket_regex.compile(match.groups())[0])
        func_content = re.sub(r'\(\s*\)\s*=>\s*{(.*)}', r'\1', func.strip())
        commands: list[Command] = []
        calc_bracket_regex = BracketRegex()
        calc_regex = f'Hardcode.calc{calc_bracket_regex.match_bracket("()",1)}'

        def hard_code_calc(match: re.Match) -> str:
            formula = calc_bracket_regex.compile(match.groups())[0]
            print(formula)
            return eval_expr(formula)

        for i in range(*[int(arg.split('=')[1]) for arg in (start, stop, step)]):
            content = func_content.replace(str(literal_eval(index_str)), str(i))
            content = regex.sub(calc_regex, hard_code_calc, content)
            commands.extend(self.datapack.process_function_content(content))
        return "\n".join([command.command for command in commands])
        
    self.command = regex.sub(
        f'Hardcode.repeat{bracket_regex.match_bracket("()", 1)}', lambda match: hard_code_repeat(match, bracket_regex), self.command)