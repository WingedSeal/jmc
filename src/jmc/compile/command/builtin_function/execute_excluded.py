"""Module containing JMCFunction subclasses for custom JMC function that cannot be used with `/execute`"""

from ...tokenizer import Token, Tokenizer, TokenType
from ...exception import JMCSyntaxException, JMCValueError
from ..jmc_function import JMCFunction, FuncType, func_property
from ..utils import ArgType, NumberType, find_scoreboard_player_type, hardcode_parse_calc
from .._flow_control import parse_switch


def _hardcode_process(string: str, index_string: str,
                      i: str, token: Token, tokenizer: Tokenizer) -> str:
    string = string.replace(index_string, i)
    while True:
        calc_pos = string.find("Hardcode.calc")
        if calc_pos == -1:
            break
        string = hardcode_parse_calc(calc_pos, string, token, tokenizer)
    return string


def _hardcode_processes(string: str, index_strings: list[str],
                        i_s: list[str], token: Token, tokenizer: Tokenizer) -> str:
    for i, index_string in zip(i_s, index_strings):
        string = string.replace(index_string, i)
    calc_pos = string.find("Hardcode.calc")
    if calc_pos != -1:
        string = hardcode_parse_calc(calc_pos, string, token, tokenizer)
    return string


@func_property(
    func_type=FuncType.EXECUTE_EXCLUDED,
    call_string="Hardcode.repeat",
    arg_type={
        "indexString": ArgType.STRING,
        "function": ArgType.ARROW_FUNC,
        "start": ArgType.INTEGER,
        "stop": ArgType.INTEGER,
        "step": ArgType.INTEGER
    },
    name="hardcode_repeat",
    ignore={
        "function"
    },
    defaults={
        "step": "1"
    }
)
class HardcodeRepeat(JMCFunction):
    def call(self) -> str:
        start = int(self.args["start"])
        step = int(self.args["step"])
        stop = int(self.args["stop"])
        if step == 0:
            raise JMCSyntaxException(
                "'step' must not be zero", self.raw_args["step"].token, self.tokenizer)

        commands: list[str] = []
        for i in range(start, stop, step):
            try:
                commands.extend(self.datapack.parse_function_token(
                    Token(
                        TokenType.PAREN_CURLY,
                        self.raw_args["function"].token.line,
                        self.raw_args["function"].token.col,
                        _hardcode_process(
                            self.raw_args["function"].token.string, self.args["indexString"], str(
                                i), self.token, self.tokenizer
                        )
                    ), self.tokenizer, self.prefix)
                )
            except JMCSyntaxException as error:
                error.reinit(lambda string: _hardcode_process(
                    string, self.args["indexString"], str(
                        i), self.token, self.tokenizer
                ))
                error.msg = f"WARNING: This error happens inside {self.call_string}, error position might not be accurate\n\n" + error.msg
                raise error

        return "\n".join(commands)


@func_property(
    func_type=FuncType.EXECUTE_EXCLUDED,
    call_string="Hardcode.repeatList",
    arg_type={
        "indexString": ArgType.STRING,
        "function": ArgType.ARROW_FUNC,
        "strings": ArgType.LIST
    },
    name="hardcode_repeat_list",
    ignore={
        "function"
    }
)
class HardcodeRepeatList(JMCFunction):
    def call(self) -> str:
        strings, _ = self.datapack.parse_list(
            self.raw_args["strings"].token, self.tokenizer, TokenType.STRING)
        commands: list[str] = []
        for i in strings:
            try:
                commands.extend(self.datapack.parse_function_token(
                    Token(
                        TokenType.PAREN_CURLY,
                        self.raw_args["function"].token.line,
                        self.raw_args["function"].token.col,
                        _hardcode_process(
                            self.raw_args["function"].token.string, self.args["indexString"], i, self.token, self.tokenizer
                        )
                    ), self.tokenizer, self.prefix)
                )
            except JMCSyntaxException as error:
                error.reinit(lambda string: _hardcode_process(
                    string, self.args["indexString"], i, self.token, self.tokenizer
                ))
                error.msg = f"WARNING: This error happens inside {self.call_string}, error position might not be accurate\n\n" + error.msg
                raise error

        return "\n".join(commands)


@func_property(
    func_type=FuncType.EXECUTE_EXCLUDED,
    call_string="Hardcode.repeatLists",
    arg_type={
        "indexStrings": ArgType.LIST,
        "function": ArgType.ARROW_FUNC,
        "stringLists": ArgType.LIST
    },
    name="hardcode_repeat_lists",
    ignore={
        "function"
    }
)
class HardcodeRepeatLists(JMCFunction):
    def call(self) -> str:
        index_strings, _ = self.datapack.parse_list(
            self.raw_args["indexStrings"].token, self.tokenizer, TokenType.STRING)
        string_lists, _ = self.datapack.parse_lists(
            self.raw_args["stringLists"].token, self.tokenizer, TokenType.STRING)
        if len(index_strings) != len(string_lists):
            raise JMCValueError(
                f"Size of indexStrings({len(index_strings)}) doesn't match the size of stringLists({len(string_lists)})",
                self.raw_args["indexStrings"].token,
                self.tokenizer)
        string_lists_count = [len(string_list) for string_list in string_lists]
        if string_lists_count.count(
                string_lists_count[0]) != len(string_lists_count):
            raise JMCValueError(
                "Not all of list in stringLists have equal size",
                self.raw_args["stringLists"].token,
                self.tokenizer)
        commands: list[str] = []
        for index in range(len(string_lists[0])):
            try:
                commands.extend(self.datapack.parse_function_token(
                    Token(
                        TokenType.PAREN_CURLY,
                        self.raw_args["function"].token.line,
                        self.raw_args["function"].token.col,
                        _hardcode_processes(
                            self.raw_args["function"].token.string, index_strings, [
                                string_list[index] for string_list in string_lists], self.token, self.tokenizer
                        )
                    ), self.tokenizer, self.prefix)
                )
            except JMCSyntaxException as error:
                error.reinit(lambda string: _hardcode_processes(
                    string, index_strings, [
                        string_list[index] for string_list in string_lists], self.token, self.tokenizer
                ))
                error.msg = f"WARNING: This error happens inside {self.call_string}, error position might not be accurate\n\n" + error.msg
                raise error

        return "\n".join(commands)


@func_property(
    func_type=FuncType.EXECUTE_EXCLUDED,
    call_string="Hardcode.switch",
    arg_type={
        "switch": ArgType.SCOREBOARD,
        "indexString": ArgType.STRING,
        "function": ArgType.ARROW_FUNC,
        "count": ArgType.INTEGER,
        "begin_at": ArgType.INTEGER,
    },
    name="hardcode_switch",
    ignore={
        "function",
        "switch"
    },
    number_type={
        "count": NumberType.POSITIVE
    },
    defaults={
        "begin_at": "1"
    }
)
class HardcodeSwitch(JMCFunction):
    def call(self) -> str:
        start_at = int(self.args["begin_at"])
        count = int(self.args["count"])
        func_contents: list[list[str]] = []
        scoreboard_player = find_scoreboard_player_type(
            self.raw_args["switch"].token, self.tokenizer)
        for i in range(start_at, count + 1):
            try:
                func_contents.append(self.datapack.parse_function_token(
                    Token(
                        TokenType.PAREN_CURLY,
                        self.raw_args["function"].token.line,
                        self.raw_args["function"].token.col,
                        _hardcode_process(
                            self.raw_args["function"].token.string, self.args["indexString"], str(
                                i), self.token, self.tokenizer
                        )
                    ), self.tokenizer, self.prefix)
                )
            except JMCSyntaxException as error:
                error.reinit(lambda string: _hardcode_process(
                    string, self.args["indexString"], str(
                        i), self.token, self.tokenizer
                ))
                error.msg = f"WARNING: This error happens inside {self.call_string}, error position might not be accurate\n\n" + error.msg
                raise error

        return parse_switch(scoreboard_player, func_contents,
                            self.datapack, self.name, start_at, [*range(start_at, count + 1)])


@func_property(
    func_type=FuncType.EXECUTE_EXCLUDED,
    call_string="Raycast.simple",
    arg_type={
        "onHit": ArgType.FUNC,
        "onStep": ArgType.FUNC,
        "onBeforeStep": ArgType.FUNC,
        "interval": ArgType.FLOAT,
        "maxIter": ArgType.SCOREBOARD_INT,
        "boxSize": ArgType.FLOAT,
        "target": ArgType.SELECTOR,
        "startAtEye": ArgType.KEYWORD,
        "stopAtEntity": ArgType.KEYWORD,
        "stopAtBlock": ArgType.KEYWORD,
        "runAtEnd": ArgType.KEYWORD,
        "casterTag": ArgType.KEYWORD,
        "removeCasterTag": ArgType.KEYWORD,
        "modifyExecuteBeforeStep": ArgType.STRING,
        "modifyExecuteAfterStep": ArgType.STRING,
        "overideString": ArgType.STRING,
        "overideRecursion": ArgType.ARROW_FUNC
    },
    name="raycast_simple",
    defaults={
        "onStep": "",
        "onBeforeStep": "",
        "interval": "0.1",
        "maxIter": "1000",
        "boxSize": "0.1",
        "target": "@e",
        "startAtEye": "true",
        "stopAtEntity": "true",
        "stopAtBlock": "true",
        "runAtEnd": "false",
        "casterTag": "__self__",
        "removeCasterTag": "true",
        "modifyExecuteBeforeStep": "",
        "modifyExecuteAfterStep": "",
        "overideString": "",
        "overideRecursion": ""
    },
    ignore={
        "overideRecursion"
    },
    number_type={
        "interval": NumberType.POSITIVE,
        "maxIter": NumberType.POSITIVE,
        "boxSize": NumberType.ZERO_POSITIVE
    }
)
class RaycastSimple(JMCFunction):
    current_iter = "__current_iter_raycast__"

    def call(self) -> str:
        current_iter = self.current_iter + \
            self.datapack.get_count(f"{self.name}/current_iter")
        caster_tag = self.args["casterTag"]
        box_size = float(self.args["boxSize"])
        dx = "0" if box_size < 1 else str(box_size - 1)

        if self.args["target"].endswith("]"):
            target = f'{self.args["target"][:-1]},dx={dx},tag=!{caster_tag}]'
        else:
            target = f'{self.args["target"]}[dx={dx},tag=!{caster_tag}]'

        count = self.datapack.get_count(f"{self.name}/loop")
        raycast_loop = self.datapack.call_func(
            f"{self.name}/loop", count)[9:]  # len("function ") = 9

        is_stop_entity = self.check_bool("stopAtEntity")
        is_stop_block = self.check_bool("stopAtBlock")
        is_run_end = self.check_bool("runAtEnd")
        is_remove_tag = self.check_bool("removeCasterTag")
        is_start_eye = self.check_bool("startAtEye")

        if is_stop_block:
            self.datapack.add_private_json("tags/blocks", f"{self.name}/default_raycast_pass", {
                "values": [
                    "minecraft:air",
                    "minecraft:void_air",
                    "minecraft:cave_air",
                    "minecraft:water",
                    "minecraft:lava",
                    "minecraft:grass",
                    "#minecraft:small_flowers",
                    "#minecraft:tall_flowers",
                    "#minecraft:small_dripleaf_placeable",
                    "minecraft:fern",
                    "minecraft:fire",
                    "minecraft:tall_grass",
                    "minecraft:large_fern",
                    "minecraft:vine",
                    "minecraft:twisting_vines",
                    "minecraft:twisting_vines_plant",
                    "minecraft:weeping_vines",
                    "minecraft:weeping_vines_plant",
                    "#minecraft:crops",
                    "#minecraft:saplings",
                    "#minecraft:signs",
                    "minecraft:attached_melon_stem",
                    "minecraft:attached_pumpkin_stem",
                    "minecraft:nether_wart",
                    "minecraft:sweet_berry_bush",
                    "minecraft:cocoa",
                    "minecraft:sugar_cane",
                    "minecraft:seagrass",
                    "minecraft:tall_seagrass",
                    "minecraft:redstone_wire",
                    "minecraft:rail",
                    "minecraft:powered_rail",
                    "minecraft:activator_rail",
                    "minecraft:detector_rail",
                    "minecraft:torch",
                    "minecraft:soul_torch",
                    "minecraft:redstone_torch",
                    "minecraft:glow_lichen"
                ]
            })

        if is_stop_entity:
            collide = self.datapack.add_raw_private_function(
                f"{self.name}/collide", [
                    f"scoreboard players set {current_iter} {self.datapack.var_name} -1",
                    self.args["onHit"]
                ])
        else:
            collide = self.args["onHit"]

        if box_size == 0:
            check_colide = f"execute as {target} positioned ~-1 ~-1 ~-1 if entity @s[dx=0] run {collide}"
        elif box_size <= 0.01:
            check_colide = f"execute as {target} positioned ~-{1-box_size} ~-{1-box_size} ~-{1-box_size} if entity @s[dx=0] positioned ~{1-box_size} ~{1-box_size} ~{1-box_size} run {collide}"
        elif box_size < 1:
            check_colide = f"execute positioned ~-{(1-box_size/2)} ~-{(1-box_size/2)} ~-{(1-box_size/2)} as {target} positioned ~{1-box_size} ~{1-box_size} ~{1-box_size} if entity @s[dx=0] positioned ~{box_size/2} ~{box_size/2} ~{box_size/2} run {collide}"
        else:
            check_colide = f"execute positioned ~-{box_size/2} ~-{box_size/2} ~-{box_size/2} as {target} positioned ~{box_size/2} ~{box_size/2} ~{box_size/2} run {collide}"

        loop_commands = [
            check_colide,
            f"execute if score {current_iter} {self.datapack.var_name} matches 1.. run scoreboard players remove {current_iter} {self.datapack.var_name} 1"
        ]
        if is_stop_block:
            loop_commands.append(
                f"execute unless block ~ ~ ~ #{self.datapack.namespace}:{self.datapack.private_name}/{self.name}/default_raycast_pass run scoreboard players set {current_iter} {self.datapack.var_name} 0")
        if is_run_end:
            loop_commands.append(
                f"execute if score {current_iter} {self.datapack.var_name} matches 0 run {collide}")
        loop_commands.append(self.args["onStep"])

        if "overideRecursion" in self.raw_args:
            if not self.args["overideString"]:
                raise JMCValueError(
                    "'overideString' missing for overideRecursion",
                    self.raw_args["overideString"].token,
                    self.tokenizer)
            try:
                recursion_commands = self.datapack.parse_function_token(
                    Token(
                        TokenType.PAREN_CURLY,
                        self.raw_args["overideRecursion"].token.line,
                        self.raw_args["overideRecursion"].token.col,
                        self.raw_args["overideRecursion"].token.string.replace(
                            self.args["overideString"], raycast_loop),
                    ), self.tokenizer, self.prefix)
            except JMCSyntaxException as error:
                error.reinit(
                    lambda string: string.replace(
                        self.args["overideString"],
                        raycast_loop))
                error.msg = f"WARNING: This error happens inside {self.call_string}, error position might not be accurate\n\n" + error.msg
                raise error
        else:
            modify_execute_before_step = self.args["modifyExecuteBeforeStep"] + \
                " " if self.args["modifyExecuteBeforeStep"] else ""
            modify_execute_after_step = self.args["modifyExecuteAfterStep"] + \
                " " if self.args["modifyExecuteAfterStep"] else ""
            recursion_commands = [
                f"execute if score {current_iter} {self.datapack.var_name} matches 1.. {modify_execute_before_step}positioned ^ ^ ^{self.args['interval']} {modify_execute_after_step}run function {raycast_loop}"]

        loop_commands.extend(recursion_commands)

        self.datapack.add_raw_private_function(
            f"{self.name}/loop",
            loop_commands,
            count=count)

        if "maxIter" not in self.raw_args or self.raw_args["maxIter"].arg_type == ArgType.INTEGER:
            set_iter_command = f"scoreboard players set {current_iter} {self.datapack.var_name} {self.args['maxIter']}"
        else:
            set_iter_command = f"scoreboard players operation {current_iter} {self.datapack.var_name} = {self.args['maxIter']}"

        return_command = f"""tag @s add {caster_tag}
{set_iter_command}
{f"execute anchored eyes positioned ^ ^ ^{self.args['interval']} run " if is_start_eye else ""}function {raycast_loop}"""
        if is_remove_tag:
            return_command += f"\ntag @s remove {caster_tag}"
        return return_command


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Tag.update",
    arg_type={
        "selector": ArgType.SELECTOR,
        "tag": ArgType.KEYWORD,
        "removeFrom": ArgType.SELECTOR
    },
    defaults={
        "removeFrom": "@e",
    },
    name="tag_update"
)
class TagUpdate(JMCFunction):
    def call(self) -> str:
        selector = self.args["selector"]
        tag = self.args["tag"]
        remove_from = self.args["removeFrom"]
        return (f"tag {remove_from} remove {tag}\n" +
                f"tag {selector} add {tag}")
