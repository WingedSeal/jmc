from json import JSONDecodeError, loads
from ..exception import JMCDecodeJSONError, JMCSyntaxException, JMCTypeError
from ..datapack import DataPack, Function
from .utils import ArgType
from .jmc_function import JMCFunction, FuncType, func_property


@func_property(
    func_type=FuncType.load_only,
    call_string='RightClick.setup',
    arg_type={
    },
    name='right_click_setup'
)
class RightClickSetup(JMCFunction):
    pass


@func_property(
    func_type=FuncType.load_only,
    call_string='Player.onEvent',
    arg_type={
        "objective": ArgType.keyword,
        "function": ArgType.func,
    },
    name='player_on_event'
)
class PlayerOnEvent(JMCFunction):
    def call(self) -> str:
        count = self.datapack.get_count(self.name)
        func = self.datapack.add_raw_private_function(
            self.name, [f"scoreboard players reset @s {self.args['objective']}", self.args['function']], count=count)
        self.datapack.ticks.append(
            f"execute as @a[scores={{{self.args['objective']}=1..}}] at @s run {func}")
        return ""


@func_property(
    func_type=FuncType.load_only,
    call_string='Trigger.setup',
    arg_type={
        "objective": ArgType.keyword,
        "triggers": ArgType.js_object
    },
    name='trigger_setup'
)
class TriggerSetup(JMCFunction):
    pass


@func_property(
    func_type=FuncType.load_only,
    call_string='Timer.add',
    arg_type={
        "objective": ArgType.keyword,
        "mode": ArgType.keyword,
        "selector": ArgType.selector,
        "function": ArgType.func
    },
    name='timer_add',
    defaults={
        "function": ""
    }
)
class TimerAdd(JMCFunction):
    def call(self) -> str:
        mode = self.args["mode"]
        obj = self.args["objective"]
        selector = self.args["selector"]
        if mode not in {'runOnce', 'runTick', 'none'}:
            raise JMCSyntaxException(
                f"Avaliable modes for Timer.add are 'runOnce', 'runTick' and 'none' (got '{mode}')", self._args["mode"].token, self.tokenizer, suggestion="'runOnce' run the commands once after the timer is over.\n'runTick' run the commands every tick if timer is over.\n'none' do not run any command.")

        if mode in {'runOnce', 'runTick'} and self._args["function"] is None:
            raise JMCTypeError("function", self.token, self.tokenizer)
        if mode == 'none' and self._args["function"] is not None:
            raise JMCSyntaxException(
                "'function' is provided in 'none' mode Timer.add", self._args["function"], self.tokenizer)
        self.datapack.add_objective('dummy', obj)
        if 'Timer.add' not in self.datapack.used_command:
            self.datapack.used_command.add('Timer.add')
            self.datapack.ticks.append(
                self.datapack.call_func(self.name, 'main'))
            self.datapack.private_functions[self.name]['main'] = Function()

        main_func = self.datapack.private_functions[self.name]['main']
        main_func.append(
            f"execute as {selector} if score @s {obj} matches 1.. run scoreboard players remove @s {obj} 1")
        if mode == 'runOnce':
            count = self.datapack.get_count(self.name)
            main_func.append(
                f"""execute as {selector} if score @s {obj} matches 0 run {self.datapack.add_raw_private_function(
                    self.name,
                    [
                        f"scoreboard players reset @s {obj}",
                        self.args["function"]
                    ],
                    count
                )}""")
        elif mode == 'runTick':
            main_func.append(
                f"""execute as {selector} unless score @s {obj} matches 1.. run {self.datapack.add_raw_private_function(
                    self.name,
                    [self.args["function"]],
                    count
                )}""")

        return ""


@func_property(
    func_type=FuncType.load_only,
    call_string='Recipe.table',
    arg_type={
        "recipe": ArgType.json,
        "baseItem": ArgType.keyword,
        "onCraft": ArgType.func
    },
    name='recipe_table',
    defaults={
        "baseItem": "minecraft:knowledge_book",
        "onCraft": ""
    }
)
class RecipeTable(JMCFunction):
    def call(self) -> str:
        base_item = self.args["baseItem"]
        if not base_item.startswith("minecraft:"):
            base_item = 'minecraft:'+base_item
        count = self.datapack.get_count(self.name)
        self.datapack.add_private_json('advancements', f'{self.name}/{count}', {
            "criteria": {
                "requirement": {
                    "trigger": "minecraft:recipe_unlocked",
                    "conditions": {
                        "recipe": f"{self.datapack.namespace}:{DataPack.PRIVATE_NAME}/{self.name}/{count}"
                    }
                }
            },
            "rewards": {
                "function": f"{self.datapack.namespace}:{DataPack.PRIVATE_NAME}/{self.name}/{count}"
            }
        })

        try:
            json = loads(self.args["recipe"])
        except JSONDecodeError as error:
            raise JMCDecodeJSONError(
                error, self._args["recipe"].token, self.tokenizer)

        if "result" not in json:
            raise JMCSyntaxException("'result' key not found in recipe",
                                     self._args["recipe"].token, self.tokenizer, display_col_length=True, suggestion="recipe json maybe invalid")
        if "item" not in json["result"]:
            raise JMCSyntaxException("'item' key not found in 'result' in recipe",
                                     self._args["recipe"].token, self.tokenizer, display_col_length=True, suggestion="recipe json maybe invalid")
        if "count" not in json["result"]:
            raise JMCSyntaxException("'count' key not found in 'result' in recipe",
                                     self._args["recipe"].token, self.tokenizer, display_col_length=True, suggestion="recipe json maybe invalid")

        result_item = json["result"]["item"]
        json["result"]["item"] = base_item
        result_count = json["result"]["count"]
        json["result"]["count"] = 1

        self.datapack.add_private_json(
            'recipes', f'{self.name}/{count}', json)
        self.datapack.add_raw_private_function(
            self.name,
            [
                f"clear @s {base_item} 1",
                f"give @s {result_item} {result_count}",
                f"recipe take @s {self.datapack.namespace}:{DataPack.PRIVATE_NAME}/{self.name}/{count}",
                f"advancement revoke @s only {self.datapack.namespace}:{DataPack.PRIVATE_NAME}/{self.name}/{count}",
                self.args["onCraft"]
            ],
            count
        )
        return ""


@func_property(
    func_type=FuncType.load_only,
    call_string='Debug.track',
    arg_type={},
    name='debug_track'
)
class DebugTrack(JMCFunction):
    pass


@func_property(
    func_type=FuncType.load_only,
    call_string='Debug.history',
    arg_type={},
    name='debug_history'
)
class DebugHistory(JMCFunction):
    pass


@func_property(
    func_type=FuncType.load_only,
    call_string='Debug.cleanup',
    arg_type={},
    name='debug_cleanup'
)
class DebugCleanup(JMCFunction):
    pass
