import regex
import re
from typing import TYPE_CHECKING

from .utils import BracketRegex, Re, split, eval_expr
from .flow_control.function_ import Function
from .args_parse import args_parse, parse_func_json
from ast import arg, literal_eval
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
    self.command = regex.sub(f'{Re.var}\\.toString{bracket_regex.match_bracket("()", 2)}', 
        lambda match: to_string(match, bracket_regex), self.command)
    

    bracket_regex = BracketRegex()
    def rightclick_setup(match: re.Match, bracket_regex: BracketRegex) -> str:
        args = args_parse(bracket_regex.compile(match.groups())[0], {"id_name":"id", "func_json":""})
        id_name = args["id_name"]
        func_json = args["func_json"]
        if not self.datapack.booleans["rc_detection"]:
            self.datapack.booleans["rc_detection"] = True
            self.datapack.loads.append('scoreboard objectives add __rc__ minecraft.used:minecraft.carrot_on_a_stick')
            self.datapack.ticks.append(f'execute as @a[scores={{__rc__=1..}}] at @s run function {self.datapack.namespace}:__private__/rc_detection/main')
            self.datapack.private_functions["rc_detection"]["main"] = Function(self.datapack.process_function_content("scoreboard players reset @s __rc__;"))
        
        commands = f"execute store result score __item_id__ __variable__ run data get entity @s SelectedItem.tag.{id_name};"

        for id_, content in parse_func_json(func_json):
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
        
    self.command = regex.sub(r'Player.firstJoin\(\s*\(\s*\)\s*=>\s*'+f'{bracket_regex.match_bracket("{}", 1)}\\s*\\)', 
        lambda match: player_first_join(match, bracket_regex), self.command)
        
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

    self.command = regex.sub(r'Player.rejoin\(\s*\(\s*\)\s*=>\s*'+f'{bracket_regex.match_bracket("{}", 1)}\\s*\\)',
        lambda match: player_rejoin(match, bracket_regex), self.command)

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
    self.command = regex.sub(f'{Re.var}\\s*=\\s*Math\\.sqrt\\({Re.var}\\)', 
        math_sqrt, self.command)


    bracket_regex = BracketRegex()
    def hard_code_repeat(match: re.Match, bracket_regex: BracketRegex) -> str:
        args = args_parse(bracket_regex.compile(match.groups())[0], {"index_string":"index", "func":"","start":"","stop":"","step":"1"})
        index_str, func, start, stop, step = args.values()
        func_content = re.sub(r'\(\s*\)\s*=>\s*{(.*)}', r'\1', func)
        commands: list[Command] = []
        calc_bracket_regex = BracketRegex()
        calc_regex = f'Hardcode.calc{calc_bracket_regex.match_bracket("()",1)}'

        def hard_code_calc(match: re.Match) -> str:
            formula = calc_bracket_regex.compile(match.groups())[0]
            return eval_expr(formula)

        for i in range(*[int(arg.split('=')[1]) for arg in (start, stop, step)]):
            content = func_content.replace(str(literal_eval(index_str)), str(i))
            content = regex.sub(calc_regex, hard_code_calc, content)
            commands.extend(self.datapack.process_function_content(content))
        return "\n".join([command.command for command in commands])
        
    self.command = regex.sub(f'Hardcode.repeat{bracket_regex.match_bracket("()", 1)}', 
        lambda match: hard_code_repeat(match, bracket_regex), self.command)

    bracket_regex = BracketRegex()
    def trigger_setup(match: re.Match, bracket_regex: BracketRegex) -> str:
        args = args_parse(bracket_regex.compile(match.groups())[0], {"objective":"__trigger__", "func_json":""})
        objective = args["objective"]
        func_json = args["func_json"]
        if not self.datapack.booleans["trigger"]:
            self.datapack.booleans["trigger"] = True
            self.datapack.private_functions["trigger"]["main"] = Function([])
            self.datapack.ticks.append(f'function {self.datapack.namespace}:__private__/trigger/main')
            # Setup enable
            self.datapack.news["advancements"][f"__private__/trigger/enable"] = {
                    "criteria": {
                        "requirement": {
                        "trigger": "minecraft:tick"
                        }
                    },
                    "rewards": {
                        "function": f"{self.datapack.namespace}:__private__/trigger/enable"
                    }
                }
            self.datapack.private_functions["trigger"]["enable"] = Function([])

        self.datapack.loads.extend([f'scoreboard objectives add {objective} trigger',
            f'scoreboard players enable @a {objective}'])

        trigger_count = self.datapack.get_pfc("trigger")
        commands = ""
        for id_, content in parse_func_json(func_json):
            __commands = self.datapack.process_function_content(content)
            if len(__commands) == 1:
                commands += f" execute if score @s {objective} matches {id_} at @s run {__commands[0].command};"
            else:
                count = self.datapack.get_pfc("trigger")
                self.datapack.private_functions["trigger"][count] = Function(__commands)
                commands += f" execute if score @s {objective} matches {id_} at @s run function {self.datapack.namespace}:__private__/trigger/{count};"

        commands += f"scoreboard players reset @s {objective}; scoreboard players enable @s {objective};"
        self.datapack.private_functions["trigger"][trigger_count] = Function(self.datapack.process_function_content(commands))

        self.datapack.private_functions["trigger"]["main"].commands.extend(
            self.datapack.process_function_content(f"execute as @a[scores={{{objective}=1..}}] run function {self.datapack.namespace}:__private__/trigger/{trigger_count};")
        )
        self.datapack.private_functions["trigger"]["enable"].commands.extend(
            self.datapack.process_function_content(f"scoreboard players enable @s {objective};")
        )
        return ""

    self.command = regex.sub(f'Trigger\\.setup{bracket_regex.match_bracket("()", 1)}',
        lambda match: trigger_setup(match, bracket_regex), self.command)


    bracket_regex = BracketRegex()
    def timer_add(match: re.Match, bracket_regex: BracketRegex) -> str:
        args = args_parse(bracket_regex.compile(match.groups())[0], {"objective":"__timer__", "runMode":"none", "func":"", "target_selector":"@a"})
        objective = args["objective"]
        run_mode = args["runMode"]
        target_selector = list(args.values())[-1]
        func = args["func"]

        self.datapack.scoreboards.add(objective)
        if not self.datapack.booleans["timer_add"]:
            self.datapack.booleans["timer_add"] = True
            self.datapack.private_functions["timer_add"]["main"] = Function([])
            self.datapack.ticks.append(f'function {self.datapack.namespace}:__private__/timer_add/main')
        
        self.datapack.private_functions["timer_add"]["main"].commands.extend(
            self.datapack.process_function_content(f"execute as {target_selector} if score @s {objective} matches 1.. run scoreboard players remove @s {objective} 1;")
            )
            
        if run_mode == "runOnce":
            content = re.sub(r'\(\s*\)\s*=>\s*{(.*)}', r'\1', func)
            count = self.datapack.get_pfc("timer_add")
            self.datapack.private_functions["timer_add"][count] = Function(
                self.datapack.process_function_content(f"scoreboard players reset @s {objective}; {content}")
                )
            self.datapack.private_functions["timer_add"]["main"].commands.extend(
                self.datapack.process_function_content(
                    f"execute as {target_selector} if score @s {objective} matches 0 run function {self.datapack.namespace}:__private__/timer_add/{count}"
                    )
                )
        if run_mode == "runTick":
            content = re.sub(r'\(\s*\)\s*=>\s*{(.*)}', r'\1', func)
            commands = self.datapack.process_function_content(content)
            if len(commands) == 1:
                self.datapack.private_functions["timer_add"]["main"].commands.append(f"execute as {target_selector} unless score @s {objective} matches 1.. run {commands[0]}")
            else:
                count = self.datapack.get_pfc("timer_add")
                self.datapack.private_functions["timer_add"][count] = Function(commands)
                self.datapack.private_functions["timer_add"]["main"].commands.append(f"execute as {target_selector} unless score @s {objective} matches 1.. run function {self.datapack.namespace}:__private__/timer_add/{count}")
        return ""

    self.command = regex.sub(f'Timer\\.add{bracket_regex.match_bracket("()", 1)}',
        lambda match: timer_add(match, bracket_regex), self.command)


    bracket_regex = BracketRegex()
    def timer_set(match: re.Match, bracket_regex: BracketRegex) -> str:
        objective, target_selector, tick = args_parse(bracket_regex.compile(match.groups())[0], {"objective":"__timer__", "target_selector":"@s", "tick":"1"}).values()
        if re.match(Re.var, tick):
            return f"scoreboard players operation {target_selector} {objective} = {tick} __variable__"
        return f"scoreboard players set {target_selector} {objective} {tick}"

    self.command = regex.sub(f'Timer\\.set{bracket_regex.match_bracket("()", 1)}',
        lambda match: timer_set(match, bracket_regex), self.command)

    self.command = re.sub(r'Timer\.isOver\((.+?)\)', r'score @s \1 matches ', self.command)

    