"""Module containing JMCFunction subclasses for custom JMC function that can only be used on load function"""
from ...tokenizer import Token, TokenType
from ...exception import JMCSyntaxException, JMCMissingValueError, JMCValueError
from ...datapack_data import Item
from ...datapack import DataPack
from ..utils import ArgType, NumberType, PlayerType, ScoreboardPlayer, FormattedText
from ..jmc_function import JMCFunction, FuncType, func_property
from .._flow_control import parse_switch


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Predicate.locations",
    arg_type={
        "name": ArgType.STRING,
        "predicate": ArgType.JSON,
        "xMin": ArgType.INTEGER,
        "xMax": ArgType.INTEGER,
        "yMin": ArgType.INTEGER,
        "yMax": ArgType.INTEGER,
        "zMin": ArgType.INTEGER,
        "zMax": ArgType.INTEGER,
    },
    name="predicate_locations"
)
class PredicateLocations(JMCFunction):
    def call(self) -> str:
        predicates = []
        predicate = self.load_arg_json("predicate")
        for x in range(int(self.args["xMin"]), int(self.args["xMax"]) + 1):
            for y in range(int(self.args["yMin"]),
                           int(self.args["yMax"]) + 1):
                for z in range(int(self.args["zMin"]), int(
                        self.args["zMax"]) + 1):
                    predicates.append({
                        "condition": "minecraft:location_check",
                        "offsetX": x,
                        "offsetY": y,
                        "offsetZ": z,
                        "predicate": predicate
                    })

        self.datapack.add_json("predicate", self.args["name"], predicates)
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="RightClick.setup",
    arg_type={
        "idName": ArgType.KEYWORD,
        "functionMap": ArgType.JS_OBJECT
    },
    name="right_click_setup"
)
class RightClickSetup(JMCFunction):
    tag_id_var = "__item_id__"

    def call(self) -> str:
        self.rc_obj = "__rc__" + self.args["idName"][:10]
        func_map = self.datapack.parse_func_map(
            self.raw_args["functionMap"].token, self.tokenizer)
        is_switch = sorted(func_map) == list(range(1, len(func_map) + 1))

        id_name = self.args["idName"]
        self.datapack.add_objective(self.rc_obj, "used:carrot_on_a_stick")
        if self.is_never_used():
            self.datapack.add_tick_command(
                f"""execute as @a[scores={{{self.rc_obj}=1..}}] at @s run {self.datapack.add_raw_private_function(self.name,
                                                       [f'scoreboard players set @s {self.rc_obj} 0'], 'main')}""")

        main_func = self.get_private_function("main")

        main_count = self.datapack.get_count(self.name)
        main_func.append(
            f"execute store result score {self.tag_id_var} {DataPack.var_name} run data get entity @s SelectedItem.tag.{id_name}")

        if is_switch:
            func_contents = []
            for func, is_arrow_func in func_map.values():
                if is_arrow_func:
                    func_contents.append(
                        [func]
                    )
                else:
                    func_contents.append(
                        [f"function {self.datapack.namespace}:{func}"])

            main_func.append(
                f"""execute if score {self.tag_id_var} {DataPack.var_name} matches 1.. run {parse_switch(ScoreboardPlayer(
                    PlayerType.SCOREBOARD, (self.tag_id_var, "@s")), func_contents, self.datapack, self.name)}""")
        else:
            main_func.append(
                f"execute if score {self.tag_id_var} {DataPack.var_name} matches 1.. run {self.datapack.call_func(self.name, main_count)}")
            run = []
            for num, (func, is_arrow_func) in func_map.items():
                if is_arrow_func:
                    run.append(
                        f'execute if score {self.tag_id_var} {DataPack.var_name} matches {num} at @s run {self.datapack.add_raw_private_function(self.name, [func])}')
                else:
                    run.append(
                        f'execute if score {self.tag_id_var} {DataPack.var_name} matches {num} at @s run function {self.datapack.namespace}:{func}')

            self.datapack.add_raw_private_function(self.name, run, main_count)

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Item.create",
    arg_type={
        "itemId": ArgType.KEYWORD,
        "itemType": ArgType.KEYWORD,
        "displayName": ArgType.STRING,
        "lore": ArgType.LIST,
        "nbt": ArgType.JS_OBJECT,
        "onClick": ArgType.FUNC
    },
    name="item_create",
    defaults={
        "lore": "",
        "nbt": "",
        "onClick": ""
    }
)
class ItemCreate(JMCFunction):
    rc_obj = {
        "carrot_on_a_stick": "__item_rc_carrot",
        "warped_fungus_on_a_stick": "__item_rc_warped"
    }
    tag_id_var = "__item_id__"
    id_name = "__item_id__"

    def call(self) -> str:
        item_type = self.args["itemType"]
        on_click = self.args["onClick"]
        if on_click and item_type not in {
                "carrot_on_a_stick", "warped_fungus_on_a_stick"}:
            raise JMCValueError(
                f'on_click can only be used with carrot_on_a_stick or warped_fungus_on_a_stick or in {self.call_string}',
                self.raw_args["onClick"].token,
                self.tokenizer,
                suggestion="Change item_type to carrot_on_a_stick or warped_fungus_on_a_stick")
        name = self.args["displayName"]
        if self.args["lore"]:
            lores = self.datapack.parse_list(
                self.raw_args["lore"].token, self.tokenizer, TokenType.STRING)
        else:
            lores = []
        nbt = self.tokenizer.parse_js_obj(
            self.raw_args["nbt"].token) if self.args["nbt"] else {}

        if on_click:
            rc_obj = self.rc_obj[self.args["itemType"]]
            item_id = self.datapack.data.get_item_id()
            self.datapack.add_objective(
                rc_obj, "used:" + self.args["itemType"])
            if self.is_never_used():
                self.datapack.add_tick_command(
                    f"""execute as @a[scores={{{rc_obj}=1..}}] at @s run {self.datapack.add_raw_private_function(self.name,
                                                       [
                                                        f'scoreboard players set @s {rc_obj} 0',
                                                        f"execute store result score {self.tag_id_var} {DataPack.var_name} run data get entity @s SelectedItem.tag.{self.id_name}",
                                                        f"execute if score {self.tag_id_var} {DataPack.var_name} matches 1.. run {self.datapack.call_func(self.name, 'found')}"
                                                        ], "main")}""")
                self.datapack.add_raw_private_function(self.name, [], "found")

            found_func = self.get_private_function("found")

            func = self.args["onClick"]

            if self.raw_args["onClick"].arg_type == ArgType.ARROW_FUNC:
                found_func.append(
                    f'execute if score {self.tag_id_var} {DataPack.var_name} matches {item_id} at @s run {self.datapack.add_raw_private_function(self.name, [func])}')
            else:
                found_func.append(
                    f'execute if score {self.tag_id_var} {DataPack.var_name} matches {item_id} at @s run {func}')

            if self.id_name in nbt:
                raise JMCValueError(
                    f"{self.id_name} is already inside the nbt",
                    self.token,
                    self.tokenizer)

            nbt[self.id_name] = Token.empty(item_id)

        if "display" in nbt:
            raise JMCValueError(
                "display is already inside the nbt",
                self.token,
                self.tokenizer)

        lore_ = ",".join([repr(str(FormattedText(lore, self.raw_args["lore"].token, self.tokenizer, self.datapack, is_default_no_italic=True, is_allow_score_selector=False)))
                         for lore in lores])

        nbt["display"] = Token.empty(f"""{{Name:{repr(
            str(FormattedText(name, self.raw_args["displayName"].token, self.tokenizer, self.datapack ,is_default_no_italic=True, is_allow_score_selector=False))
            )},Lore:[{lore_}]}}""")

        self.datapack.data.item[self.args["itemId"]] = Item(
            item_type,
            self.datapack.token_dict_to_raw_js_object(nbt, self.tokenizer),
        )

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Item.createSign",
    arg_type={
        "itemId": ArgType.KEYWORD,
        "variant": ArgType.KEYWORD,
        "displayName": ArgType.STRING,
        "lore": ArgType.LIST,
        "texts": ArgType.LIST,
        "nbt": ArgType.JS_OBJECT,
        "onClick": ArgType.FUNC
    },
    name="item_create_sign",
    defaults={
        "lore": "",
        "texts": "",
        "nbt": "",
        "onClick": ""
    }
)
class ItemCreateSign(JMCFunction):
    _variants = {"oak", "spruce", "birch", "jungle",
                 "acacia", "dark_oak", "crimson", "warped"}

    def call(self) -> str:
        variant = self.args["variant"]

        if variant not in self._variants:
            raise JMCValueError(
                f"Unrecognized wood variant for sign ({variant})",
                self.raw_args["variant"].token,
                self.tokenizer,
                suggestion=f"Available variants are {' '.join(repr(i) for i in self._variants)}")

        on_click = self.args["onClick"]
        name = self.args["displayName"]
        if self.args["lore"]:
            lores = self.datapack.parse_list(
                self.raw_args["lore"].token, self.tokenizer, TokenType.STRING)
        else:
            lores = []

        if self.args["texts"]:
            texts = self.datapack.parse_list(
                self.raw_args["texts"].token, self.tokenizer, TokenType.STRING)
        else:
            texts = []

        if len(texts) > 4:
            raise JMCValueError(
                f"Sign may only have 4 lines of text (got {len(texts)})",
                self.raw_args["texts"].token,
                self.tokenizer)
        texts.extend([''] * (4 - len(texts)))

        nbt = self.tokenizer.parse_js_obj(
            self.raw_args["nbt"].token) if self.args["nbt"] else {}

        if "display" in nbt:
            raise JMCValueError(
                "display is already inside the nbt",
                self.token,
                self.tokenizer)

        lore_ = ",".join(repr(str(FormattedText(lore, self.raw_args["lore"].token, self.tokenizer, self.datapack, is_default_no_italic=True, is_allow_score_selector=False)))
                         for lore in lores)
        formatted_texts_ = [FormattedText(text, self.raw_args["texts"].token, self.tokenizer, self.datapack) if text else FormattedText.empty(self.tokenizer, self.datapack)
                            for text in texts]
        if on_click:
            formatted_texts_[0].add_key(
                "clickEvent", {
                    "action": "run_command", "value": on_click})
            if not formatted_texts_[0]:
                formatted_texts_[0].add_key("text", "")

        texts_ = [repr(str(text)) for text in formatted_texts_]

        nbt["display"] = Token.empty(f"""{{Name:{repr(
            str(FormattedText(name, self.raw_args["displayName"].token, self.tokenizer, self.datapack, is_default_no_italic=True, is_allow_score_selector=False))
            )},Lore:[{lore_}]}},BlockEntityTag:{{Text1:{texts_[0]},Text2:{texts_[1]},Text3:{texts_[2]},Text4:{texts_[3]}}}""")

        self.datapack.data.item[self.args["itemId"]] = Item(
            variant + "_sign",
            self.datapack.token_dict_to_raw_js_object(nbt, self.tokenizer),
        )

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Player.onEvent",
    arg_type={
        "objective": ArgType.KEYWORD,
        "function": ArgType.FUNC,
    },
    name="player_on_event"
)
class PlayerOnEvent(JMCFunction):
    def call(self) -> str:
        count = self.datapack.get_count(self.name)
        func = self.datapack.add_raw_private_function(
            self.name, [f"scoreboard players set @s {self.args['objective']} 0", self.args['function']], count=count)
        self.datapack.add_tick_command(
            f"execute as @a[scores={{{self.args['objective']}=1..}}] at @s run {func}")
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Trigger.setup",
    arg_type={
        "objective": ArgType.KEYWORD,
        "triggers": ArgType.JS_OBJECT
    },
    name="trigger_setup",
    ignore={
        "triggers"
    }
)
class TriggerSetup(JMCFunction):
    def call(self) -> str:
        func_map = self.datapack.parse_func_map(
            self.raw_args["triggers"].token, self.tokenizer)
        is_switch = sorted(func_map) == list(range(1, len(func_map) + 1))

        obj = self.args["objective"]
        self.datapack.add_objective(obj, "trigger")
        if self.is_never_used():
            self.datapack.add_tick_command(
                self.datapack.call_func(self.name, "main"))
            self.make_empty_private_function("main")
            self.datapack.add_load_command(
                f"execute as @a run {self.datapack.call_func(self.name, 'enable')}")
            self.make_empty_private_function("enable")

            self.datapack.add_private_json("advancements", f"{self.name}/enable", {
                "criteria": {
                    "requirement": {
                        "trigger": "minecraft:tick"
                    }
                },
                "rewards": {
                    "function": f"{self.datapack.namespace}:{DataPack.private_name}/{self.name}/enable"
                }
            })

        main_func = self.get_private_function("main")
        self.get_private_function("enable").append(
            f"scoreboard players enable @s {obj}")

        main_count = self.datapack.get_count(self.name)
        main_func.append(
            f"execute as @a[scores={{{obj}=1..}}] at @s run {self.datapack.call_func(self.name, main_count)}")

        if is_switch:
            func_contents = []
            for func, is_arrow_func in func_map.values():
                if is_arrow_func:
                    func_contents.append(
                        [func]
                    )
                else:
                    func_contents.append(
                        [f"function {self.datapack.namespace}:{func}"])
            run = [
                parse_switch(ScoreboardPlayer(
                    PlayerType.SCOREBOARD, (obj, "@s")), func_contents, self.datapack, self.name),
            ]
        else:
            run = []
            for num, (func, is_arrow_func) in func_map.items():
                if is_arrow_func:
                    run.append(
                        f'execute if score @s {obj} {DataPack.var_name} matches {num} run {self.datapack.add_raw_private_function(self.name, [func])}')
                else:
                    run.append(
                        f'execute if score @s {obj} {DataPack.var_name} matches {num} run {func}')

        run.extend([f"scoreboard players set @s {obj} 0",
                    f"scoreboard players enable @s {obj}"])
        self.datapack.add_raw_private_function(self.name, run, main_count)

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Trigger.add",
    arg_type={
        "objective": ArgType.KEYWORD,
        "function": ArgType.FUNC
    },
    name="trigger_add",
)
class TriggerAdd(JMCFunction):
    def call(self) -> str:

        obj = self.args["objective"]
        self.datapack.add_objective(obj, "trigger")
        if self.is_never_used():
            self.datapack.add_tick_command(
                self.datapack.call_func(self.name, "main"))
            self.make_empty_private_function("main")
            self.datapack.add_load_command(
                f"execute as @a run {self.datapack.call_func(self.name, 'enable')}")
            self.make_empty_private_function("enable")

            self.datapack.add_private_json("advancements", f"{self.name}/enable", {
                "criteria": {
                    "requirement": {
                        "trigger": "minecraft:tick"
                    }
                },
                "rewards": {
                    "function": f"{self.datapack.namespace}:{DataPack.private_name}/{self.name}/enable"
                }
            })

        main_func = self.get_private_function("main")
        self.get_private_function("enable").append(
            f"scoreboard players enable @s {obj}")

        func = self.args["function"]
        run = f"""execute as @a[scores={{{obj}=1..}}] at @s run {self.datapack.add_raw_private_function(self.name, [
                func,
                f"scoreboard players set @s {obj} 0",
                f"scoreboard players enable @s {obj}"
                ], obj)}"""
        main_func.append(run)

        return ""


@ func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Timer.add",
    arg_type={
        "objective": ArgType.KEYWORD,
        "mode": ArgType.KEYWORD,
        "selector": ArgType.SELECTOR,
        "function": ArgType.FUNC
    },
    name="timer_add",
    defaults={
        "function": ""
    }
)
class TimerAdd(JMCFunction):
    def call(self) -> str:
        mode = self.args["mode"]
        obj = self.args["objective"]
        selector = self.args["selector"]
        if mode not in {"runOnce", "runTick", "none"}:
            raise JMCSyntaxException(
                f"Avaliable modes for {self.call_string} are 'runOnce', 'runTick' and 'none' (got '{mode}')", self.raw_args["mode"].token, self.tokenizer, suggestion="'runOnce' run the commands once after the timer is over.\n'runTick' run the commands every tick if timer is over.\n'none' do not run any command.")

        if mode in {"runOnce",
                    "runTick"} and self.raw_args["function"] is None:
            raise JMCMissingValueError("function", self.token, self.tokenizer)
        if mode == "none" and self.raw_args["function"] is not None:
            raise JMCSyntaxException(
                f"'function' is provided in 'none' mode {self.call_string}", self.raw_args["function"].token, self.tokenizer)
        self.datapack.add_objective(obj)
        if self.is_never_used():
            self.datapack.add_tick_command(
                self.datapack.call_func(self.name, "main"))
            self.make_empty_private_function("main")

        main_func = self.get_private_function("main")
        if selector.startswith("@"):
            if_selector = f"as {selector} if score @s"
            unless_selector = f"as {selector} unless score @s"
            at_s = "@s"
            at_at_s = "at @s "
        else:
            if_selector = f"if score {selector}"
            unless_selector = f"unless score {selector}"
            at_s = selector
            at_at_s = ""
        main_func.append(
            f"execute {if_selector} {obj} matches 0.. run scoreboard players remove {at_s} {obj} 1")
        if mode == "runOnce":
            count = self.datapack.get_count(self.name)
            main_func.append(
                f"""execute {if_selector} {obj} matches 0 {at_at_s}run {self.datapack.add_raw_private_function(
                    self.name,
                    [
                        f"scoreboard players set {at_s} {obj} 0",
                        self.args["function"]
                    ],
                    count
                )}""")
        elif mode == "runTick":
            count = self.datapack.get_count(self.name)
            main_func.append(
                f"""execute {unless_selector} {obj} matches 1.. {at_at_s}run {self.datapack.add_raw_private_function(
                    self.name,
                    [self.args["function"]],
                    count
                )}""")

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Recipe.table",
    arg_type={
        "recipe": ArgType.JSON,
        "baseItem": ArgType.KEYWORD,
        "onCraft": ArgType.FUNC
    },
    name="recipe_table",
    defaults={
        "baseItem": "minecraft:knowledge_book",
        "onCraft": ""
    }
)
class RecipeTable(JMCFunction):
    def call(self) -> str:
        base_item = self.args["baseItem"]
        if not base_item.startswith("minecraft:"):
            base_item = "minecraft:" + base_item
        count = self.datapack.get_count(self.name)
        self.datapack.add_private_json('advancements', f'{self.name}/{count}', {
            "criteria": {
                "requirement": {
                    "trigger": "minecraft:recipe_unlocked",
                    "conditions": {
                        "recipe": f"{self.datapack.namespace}:{DataPack.private_name}/{self.name}/{count}"
                    }
                }
            },
            "rewards": {
                "function": f"{self.datapack.namespace}:{DataPack.private_name}/{self.name}/{count}"
            }
        })

        json = self.load_arg_json("recipe")

        # raise JMCSyntaxException("'result' key not found in recipe",
        # self.raw_args["recipe"].token, self.tokenizer,
        # display_col_length=True, suggestion="recipe json maybe invalid")
        if "result" in json:
            if "item" not in json["result"]:
                raise JMCSyntaxException("'item' key not found in 'result' in recipe",
                                         self.raw_args["recipe"].token, self.tokenizer, display_col_length=True, suggestion="recipe json maybe invalid")
            if "count" not in json["result"]:
                raise JMCSyntaxException("'count' key not found in 'result' in recipe",
                                         self.raw_args["recipe"].token, self.tokenizer, display_col_length=True, suggestion="recipe json maybe invalid")

            result_item = json["result"]["item"]
            json["result"]["item"] = base_item
            result_count = json["result"]["count"]
            json["result"]["count"] = 1
            result_command = f"give @s {result_item} {result_count}"
        else:
            result_command = ""

        self.datapack.add_private_json(
            "recipes", f"{self.name}/{count}", json)
        self.datapack.add_raw_private_function(
            self.name,
            [
                f"clear @s {base_item} 1",
                result_command,
                f"recipe take @s {self.datapack.namespace}:{DataPack.private_name}/{self.name}/{count}",
                f"advancement revoke @s only {self.datapack.namespace}:{DataPack.private_name}/{self.name}/{count}",
                self.args["onCraft"]
            ],
            count
        )
        return ""


# @ func_property(
#     func_type=FuncType.load_only,
#     call_string='Debug.track',
#     arg_type={},
#     name='debug_track'
# )
# class DebugTrack(JMCFunction):
#     pass


# @ func_property(
#     func_type=FuncType.load_only,
#     call_string='Debug.history',
#     arg_type={},
#     name='debug_history'
# )
# class DebugHistory(JMCFunction):
#     pass


# @ func_property(
#     func_type=FuncType.load_only,
#     call_string='Debug.cleanup',
#     arg_type={},
#     name='debug_cleanup'
# )
# class DebugCleanup(JMCFunction):
#     pass
