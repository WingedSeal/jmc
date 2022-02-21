import regex
import re
from typing import TYPE_CHECKING

from .utils import BracketRegex, Re, split, eval_expr
from .flow_control.function_ import Function
from .args_parse import args_parse, parse_func_json
from ast import  literal_eval
from json import loads, dumps
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
            if len(__commands) == 1 and '\n' not in __commands[0].command:
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
        f'RightClick\\.setup{bracket_regex.match_bracket("()", 1)}$', lambda match: rightclick_setup(match, bracket_regex), self.command)


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
        
    self.command = regex.sub(r'Player.firstJoin\(\s*\(\s*\)\s*=>\s*'+f'{bracket_regex.match_bracket("{}", 1)}\\s*\\)$', 
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

    self.command = regex.sub(r'Player.rejoin\(\s*\(\s*\)\s*=>\s*'+f'{bracket_regex.match_bracket("{}", 1)}\\s*\\)$', 
        lambda match: player_rejoin(match, bracket_regex), self.command)


    bracket_regex = BracketRegex()
    def player_die(match: re.Match, bracket_regex: BracketRegex) -> str:
        args = args_parse(bracket_regex.compile(match.groups())[0], {"onDeath":"", "onRespawn":""})
        on_death = args["onDeath"]
        on_respawn = args["onRespawn"]
        if not self.datapack.booleans["player_die"]:
            self.datapack.booleans["player_die"] = True
            self.datapack.loads.append('scoreboard objectives add __die__ deathCount')
            self.datapack.ticks.append(f'execute as @a[scores={{__die__=1..}}] at @s run function {self.datapack.namespace}:__private__/player_die/on_death')
            self.datapack.ticks.append(f'execute as @e[type=player,scores={{__die__=2..}}] at @s run function {self.datapack.namespace}:__private__/player_die/on_respawn')
            self.datapack.private_functions["player_die"]["on_death"] = Function(self.datapack.process_function_content("scoreboard players set @s __die__ 2;"))
            self.datapack.private_functions["player_die"]["on_respawn"] = Function(self.datapack.process_function_content("scoreboard players reset @s __die__;"))

        if on_death != "":
            commands = self.datapack.process_function_content(on_death)
            if len(commands) == 1:
                self.datapack.private_functions["player_die"]["on_death"].commands.extend(commands)
            else:
                count = self.datapack.get_pfc("player_die")
                self.datapack.private_functions["player_die"][count] = Function(commands)
                self.datapack.private_functions["player_die"]["on_death"].commands.extend(self.datapack.process_function_content(f"function {self.datapack.namespace}:__private__/player_die/{count}"))

        if on_respawn != "":
            commands = self.datapack.process_function_content(on_respawn)
            if len(commands) == 1:
                self.datapack.private_functions["player_die"]["on_respawn"].commands.extend(commands)
            else:
                count = self.datapack.get_pfc("player_die")
                self.datapack.private_functions["player_die"][count] = Function(commands)
                self.datapack.private_functions["player_die"]["on_respawn"].commands.extend(self.datapack.process_function_content(f"function {self.datapack.namespace}:__private__/player_die/{count}"))

        return ""

    self.command = regex.sub(f'Player.die{bracket_regex.match_bracket("()", 1)}$',
        lambda match: player_die(match, bracket_regex), self.command)

    bracket_regex = BracketRegex()
    def player_on_event(match: re.Match, bracket_regex: BracketRegex) -> str:
        args = args_parse(bracket_regex.compile(match.groups())[0], {"obj":"", "func":""})
        obj = args["obj"]
        content = args["func"]
        base_count = self.datapack.get_pfc("on_event")
        self.datapack.ticks.append(f'execute as @a[scores={{{obj}=1..}}] at @s run function {self.datapack.namespace}:__private__/on_event/{base_count}')
        self.datapack.private_functions["on_event"][base_count] = Function(self.datapack.process_function_content(f"scoreboard players reset @s {obj};"))

        commands = self.datapack.process_function_content(content)
        if len(commands) == 1:
            self.datapack.private_functions["on_event"][base_count].commands.extend(commands)
        else:
            count = self.datapack.get_pfc("on_event")
            self.datapack.private_functions["on_event"][count] = Function(commands)
            self.datapack.private_functions["on_event"][base_count].commands.extend(self.datapack.process_function_content(f"function {self.datapack.namespace}:__private__/on_event/{count}"))
        return ""

    self.command = regex.sub(r'Player.onEvent'+f'{bracket_regex.match_bracket("()", 1)}$', 
        lambda match: player_on_event(match, bracket_regex), self.command)

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
    self.command = regex.sub(f'{Re.var}\\s*=\\s*Math\\.sqrt\\({Re.var}\\)$', 
        math_sqrt, self.command)

    bracket_regex = BracketRegex()
    def math_random(match: re.Match, bracket_regex: BracketRegex) -> str:
        groups = bracket_regex.compile(match.groups())
        target_var = groups[0]
        args = args_parse(groups[1], {"min":"1", "max":"2147483647"})
        start = int(args["min"])
        end = int(args["max"])
        if not self.datapack.booleans["math_random"]:
            self.datapack.booleans["math_random"] = True
            self.datapack.news["predicates"][f"__private__/math/random_0.5"] = {
                    "condition": "minecraft:random_chance",
                    "chance": 0.5
                }
            for i in range(1,31):
                self.datapack.ints.add(2**i)
            self.datapack.private_functions["math"]["random_seed"] = Function(self.datapack.process_function_content(f"execute store success score __math__.seed __variable__ if predicate {self.datapack.namespace}:__private__/math/random_0.5;" + "".join([f"""execute store success score __math__.random_tmp __variable__ if predicate {self.datapack.namespace}:__private__/math/random_0.5;
scoreboard players operation __math__.random_tmp __variable__ *= {2**i} __int__;
scoreboard players operation __math__.seed __variable__ += __math__.random_tmp __variable__;""" for i in range(1,31)])))
            self.datapack.private_functions["math"]["random_setup"] = Function(self.datapack.process_function_content(
f"""function {self.datapack.namespace}:__private__/math/random_seed;
scoreboard players operation __math__.random_a __variable__ = __math__.seed __variable__;
scoreboard players operation __math__.random_c __variable__ = __math__.seed __variable__;
scoreboard players operation __math__.random_c __variable__ *= __math__.seed __variable__;"""))
            self.datapack.loads.append(f'execute unless score __math__.seed __variable__ matches -2147483648..2147483647 run function {self.datapack.namespace}:__private__/math/random_setup')
            self.datapack.private_functions["math"]["random"] = Function(self.datapack.process_function_content(
f"""scoreboard players operation __math__.seed __variable__ *= __math__.random_a __variable__;
scoreboard players operation __math__.seed __variable__ += __math__.random_c __variable__;"""))

        mod = end-start+1
        self.datapack.ints.add(mod)
        self.datapack.ints.add(start)
        return f"""function {self.datapack.namespace}:__private__/math/random
scoreboard players operation {target_var} __variable__ = __math__.seed __variable__
scoreboard players operation {target_var} __variable__ %= {mod} __int__
scoreboard players operation {target_var} __variable__ += {start} __int__
"""

    self.command = regex.sub(f'{Re.var}\\s*=\\s*Math\\.random{bracket_regex.match_bracket("()", 2)}$',
        lambda match: math_random(match, bracket_regex), self.command)



    bracket_regex = BracketRegex()
    def hard_code_repeat(match: re.Match, bracket_regex: BracketRegex) -> str:
        args = args_parse(bracket_regex.compile(match.groups())[0], {"index_string":"index", "func":"","start":"","stop":"","step":"1"})
        index_str, func, start, stop, step = args.values()
        func_content = re.sub(r'\(\s*\)\s*=>\s*{(.*)}', r'\1', func)
        contents: str = ""
        calc_bracket_regex = BracketRegex()
        calc_regex = f'Hardcode.calc{calc_bracket_regex.match_bracket("()",1)}'

        def hard_code_calc(match: re.Match) -> str:
            formula = calc_bracket_regex.compile(match.groups())[0]
            return eval_expr(formula)

        for i in range(int(start), int(stop), int(step)):
            content = func_content.replace(str(literal_eval(index_str)), str(i))
            content = regex.sub(calc_regex, hard_code_calc, content)
            contents += content

        commands = self.datapack.process_function_content(content)
        return "\n".join([command.command for command in commands])
        
    self.command = regex.sub(f'Hardcode.repeat{bracket_regex.match_bracket("()", 1)}$', 
        lambda match: hard_code_repeat(match, bracket_regex), self.command)

    bracket_regex = BracketRegex()
    def hard_code_switch(match: re.Match, bracket_regex: BracketRegex) -> str:
        args = args_parse(bracket_regex.compile(match.groups())[0], {"var":"", "index_string":"index", "func":"", "count":""})
        var, index_str, func, stop = args.values()
        func_content = re.sub(r'\(\s*\)\s*=>\s*{(.*)}', r'\1', func)
        contents: str = ""
        calc_bracket_regex = BracketRegex()
        calc_regex = f'Hardcode.calc{calc_bracket_regex.match_bracket("()",1)}'

        def hard_code_calc(match: re.Match) -> str:
            formula = calc_bracket_regex.compile(match.groups())[0]
            return eval_expr(formula)

        for i in range(1, int(stop)+1, 1):
            content = func_content.replace(str(literal_eval(index_str)), str(i))
            content = regex.sub(calc_regex, hard_code_calc, content)
            contents += f"case {i}: {content}"

        count = self.datapack.get_pfc("hard_code_switch")
        self.datapack.private_functions["hard_code_switch"][count] = Function(self.datapack.process_function_content(
            f"switch ({var}) {{{contents}}}"))
        return f"function {self.datapack.namespace}:__private__/hard_code_switch/{count}"
        
    self.command = regex.sub(f'Hardcode.switch{bracket_regex.match_bracket("()", 1)}$', 
        lambda match: hard_code_switch(match, bracket_regex), self.command)

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
            if len(__commands) == 1 and '\n' not in __commands[0].command:
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

    self.command = regex.sub(f'Trigger\\.setup{bracket_regex.match_bracket("()", 1)}$',
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

    self.command = regex.sub(f'Timer\\.add{bracket_regex.match_bracket("()", 1)}$',
        lambda match: timer_add(match, bracket_regex), self.command)


    bracket_regex = BracketRegex()
    def timer_set(match: re.Match, bracket_regex: BracketRegex) -> str:
        objective, target_selector, tick = args_parse(bracket_regex.compile(match.groups())[0], {"objective":"__timer__", "target_selector":"@s", "tick":"1"}).values()
        if re.match(Re.var, tick):
            return f"scoreboard players operation {target_selector} {objective} = {tick} __variable__"
        return f"scoreboard players set {target_selector} {objective} {tick}"

    self.command = regex.sub(f'Timer\\.set{bracket_regex.match_bracket("()", 1)}$',
        lambda match: timer_set(match, bracket_regex), self.command)

    self.command = re.sub(r'Timer\.isOver\((.+?)\)$', r'score @s \1 matches ', self.command)


    bracket_regex = BracketRegex()
    def recipe_table(match: re.Match, bracket_regex: BracketRegex) -> str:
        json_str, base_item, func = args_parse(bracket_regex.compile(match.groups())[0], {"json":"{}", "baseItem":"minecraft:knowledge_book", "onCraft":""}).values()
        json: dict = loads(json_str)
        result_item = json["result"]["item"]
        result_count = json["result"]["count"]
        json["result"]["item"] = base_item if base_item.startswith("minecraft:") else f"minecraft:{base_item}"
        json["result"]["count"] = 1

        count = self.datapack.get_pfc("recipe_table")
        self.datapack.news["recipes"][f"__private__/recipe_table/{count}"] = json
        self.datapack.news["advancements"][f"__private__/recipe_table/{count}"] = {
            "criteria": {
                "requirement": {
                "trigger": "minecraft:recipe_unlocked",
                "conditions": {
                    "recipe": f"{self.datapack.namespace}:__private__/recipe_table/{count}"
                }
                }
            },
            "rewards": {
                "function": f"{self.datapack.namespace}:__private__/recipe_table/{count}"
            }
        }
        self.datapack.private_functions["recipe_table"][count] = Function(
            self.datapack.process_function_content(f"clear @s {base_item} 1; give @s {result_item} {result_count}; recipe take @s {self.datapack.namespace}:__private__/recipe_table/{count}; advancement revoke @s only {self.datapack.namespace}:__private__/recipe_table/{count}; {func}")
        )
        
        return ""

    self.command = regex.sub(f'Recipe\\.table{bracket_regex.match_bracket("()", 1)}$',
        lambda match: recipe_table(match, bracket_regex), self.command)

    bracket_regex = BracketRegex()
    def debug_track(match: re.Match, bracket_regex: BracketRegex) -> str:
        scores = split(bracket_regex.compile(match.groups())[0][1:-2])
        tracks = [score.split(':') for score in scores]
        if not self.datapack.booleans["debug_track"]:
            self.datapack.booleans["debug_track"] = True
            self.datapack.loads.append('scoreboard objectives add __debug__.track dummy {"text":"Tracking Scores", "color":"gold", "bold":true}')
            self.datapack.loads.append('scoreboard players reset * __debug__.track')
            self.datapack.ticks.append(f'function {self.datapack.namespace}:__private__/debug_track/main')
        self.datapack.private_functions["debug_track"]["main"] = Function(
            self.datapack.process_function_content("\n".join([
                f"execute unless score {score} {obj} matches -2147483648..2147483647 run scoreboard players operation {obj}:{score} __debug__.track = {score} {obj};" for obj, score in tracks
                ]))
        )
        return ""

    self.command = regex.sub(f'Debug\\.track\\({bracket_regex.match_bracket("[]", 1)}\\)$',
        lambda match: debug_track(match, bracket_regex), self.command)


    self.command = regex.sub(f'Debug\\.showTrack\\(\\)',
        'scoreboard objectives setdisplay sidebar __debug__.track', self.command)


    bracket_regex = BracketRegex()
    def debug_history(match: re.Match, bracket_regex: BracketRegex) -> str:
        args = args_parse(bracket_regex.compile(match.groups())[0], {"score":"", "cache":"3"})
        obj, score = args['score'].split(':')
        cache = int(args['cache'])
        if cache > 20:
            raise ValueError("Do not use Debug.History with more than 20 cache")
        if not self.datapack.booleans["debug_history"]:
            self.datapack.booleans["debug_history"] = True
            self.datapack.loads.append(f'function {self.datapack.namespace}:__private__/debug_history/setup')
            self.datapack.ticks.append(f'function {self.datapack.namespace}:__private__/debug_history/main')

        self.datapack.private_functions["debug_history"]["setup"] = Function(
            self.datapack.process_function_content(
                f"""scoreboard objectives add __debug__.histor dummy;
scoreboard objectives modify __debug__.histor displayname {{"text":"History of {obj}:{score}", "color":"gold", "bold":true}};"""))

        self.datapack.private_functions["debug_history"]["main"] = Function(
            self.datapack.process_function_content(
        f"""scoreboard players operation __debug__.current __variable__ = {score} {obj};
execute unless score __debug__.current __variable__ = __debug__.tmp __variable__ run function {self.datapack.namespace}:__private__/debug_history/record;
scoreboard players operation __debug__.tmp __variable__ = __debug__.current __variable__;"""
        ))

        self.datapack.private_functions["debug_history"]["record"] = Function(
            self.datapack.process_function_content(
        ''.join([
            f"scoreboard players operation [{i+1}] __debug__.histor = [{i}] __debug__.histor;"
            for i in range(cache-1,0,-1)])
        +
        "scoreboard players operation [1] __debug__.histor = [CURRENT] __debug__.histor;"
        +
        "scoreboard players operation [CURRENT] __debug__.histor = __debug__.current __variable__;"
        ))


        return ""

    self.command = regex.sub(f'Debug\\.history{bracket_regex.match_bracket("()", 1)}$',
        lambda match: debug_history(match, bracket_regex), self.command)


    self.command = regex.sub(f'Debug\\.showHistory\\(\\)$',
        'scoreboard objectives setdisplay sidebar __debug__.histor', self.command)

    self.command = regex.sub(f'Debug\\.cleanup\\(\\)$',
        'scoreboard objectives remove __debug__.histor\nscoreboard objectives remove __debug__.track', self.command)