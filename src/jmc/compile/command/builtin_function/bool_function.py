"""Module containing JMCFunction subclasses for custom JMC function that returns a part of `/execute if` command"""

from ..utils import ArgType
from ..jmc_function import JMCFunction, FuncType, func_property
from ...exception import JMCValueError

IF = True
UNLESS = False


@func_property(
    func_type=FuncType.BOOL_FUNCTION,
    call_string="Timer.isOver",
    arg_type={
        "objective": ArgType.KEYWORD,
        "selector": ArgType.SELECTOR
    },
    name="timer_is_over",
    defaults={
        "selector": "@s"
    }
)
class TimerIsOver(JMCFunction):
    def call_bool(self) -> tuple[str, bool, list[str]]:
        return f'score {self.args["selector"]} {self.args["objective"]} matches 1..', UNLESS, [
        ]


@func_property(
    func_type=FuncType.BOOL_FUNCTION,
    call_string="String.isEqual",
    arg_type={
        "type": ArgType.KEYWORD,
        "source": ArgType.STRING,
        "path": ArgType.KEYWORD,
        "string": ArgType.STRING
    },
    name="string_is_equal"
)
class StringIsEqual(JMCFunction):
    current_object = "currentObject"

    def call_bool(self) -> tuple[str, bool, list[str]]:
        bool_result = self.datapack.data.get_current_bool_result()
        source = self.args["source"]
        if self.args["type"] not in {"storage", "block", "entity"}:
            raise JMCValueError(
                f"'type' parameter expect 'storage' or 'block' or 'entity' (got {self.args['type']})",
                self.raw_args["type"].token,
                self.tokenizer)
        if self.args["type"] == "storage" and ":" not in self.args["source"]:
            source = f"{self.datapack.namespace}:{source}"

        return f"score {bool_result} {self.datapack.var_name} matches 0", IF, [
            f"data modify storage {self.datapack.namespace}:{self.datapack.storage_name} currentObject set from {self.args['type']} {source} {self.args['path']}",
            f"execute store success score {bool_result} {self.datapack.var_name} run data modify storage {self.datapack.namespace}:{self.datapack.storage_name} {self.current_object} set value {self.args['string']}"
        ]


@func_property(
    func_type=FuncType.BOOL_FUNCTION,
    call_string="Object.isEqual",
    arg_type={
        "type1": ArgType.KEYWORD,
        "source1": ArgType.STRING,
        "path1": ArgType.KEYWORD,
        "type2": ArgType.KEYWORD,
        "source2": ArgType.STRING,
        "path2": ArgType.KEYWORD,
    },
    name="object_is_equal"
)
class ObjectIsEqual(JMCFunction):
    current_object = "currentObject"

    def call_bool(self) -> tuple[str, bool, list[str]]:
        bool_result = self.datapack.data.get_current_bool_result()
        source1 = self.args["source1"]
        source2 = self.args["source2"]
        for param in ("type1", "type2"):
            if self.args[param] not in {"storage", "block", "entity"}:
                raise JMCValueError(
                    f"'type' parameter expect 'storage' or 'block' or 'entity' (got {self.args[param]})",
                    self.raw_args[param].token,
                    self.tokenizer)
        if self.args["type1"] == "storage" and ":" not in self.args["source1"]:
            source1 = f"{self.datapack.namespace}:{source1}"
        if self.args["type2"] == "storage" and ":" not in self.args["source2"]:
            source2 = f"{self.datapack.namespace}:{source2}"

        return f"score {bool_result} {self.datapack.var_name} matches 0", IF, [
            f"data modify storage {self.datapack.namespace}:{self.datapack.storage_name} currentObject set from {self.args['type1']} {source1} {self.args['path1']}",
            f"execute store success score {bool_result} {self.datapack.var_name} run data modify storage {self.datapack.namespace}:{self.datapack.storage_name} {self.current_object} set from {self.args['type2']} {source2} {self.args['path2']}"
        ]
