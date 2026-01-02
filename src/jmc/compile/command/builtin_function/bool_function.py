"""Module containing JMCFunction subclasses for custom JMC function that returns a part of `/execute if` command"""

from ..utils import ArgType
from ..jmc_function import JMCFunction, FuncType, func_property
from ...exception import JMCValueError
import re

IF = True
UNLESS = False


@func_property(
    func_type=FuncType.BOOL_FUNCTION,
    call_string="Timer.isOver",
    arg_type={"objective": ArgType.KEYWORD, "selector": ArgType.SELECTOR},
    name="timer_is_over",
    defaults={"selector": "@s"},
)
class TimerIsOver(JMCFunction):
    def call_bool(self) -> tuple[str, bool, list[str]]:
        return (
            f'score {self.args["selector"]} {self.args["objective"]} matches 1..',
            UNLESS,
            [],
        )


@func_property(
    func_type=FuncType.BOOL_FUNCTION,
    call_string="String.isEqual",
    arg_type={
        "nbt": ArgType.NBT,
        "string": ArgType.STRING,
    },
    name="string_is_equal",
)
class StringIsEqual(JMCFunction):
    current_object = "currentObject"

    def call_bool(self) -> tuple[str, bool, list[str]]:
        bool_result = self.datapack.data.get_current_bool_result()
        nbt = self.args["nbt"]

        return (
            f"score {bool_result} {self.datapack.var_name} matches 0",
            IF,
            [
                f"data modify storage {self.datapack.namespace}:{self.datapack.storage_name} currentObject set from {nbt}",
                f"execute store success score {bool_result} {self.datapack.var_name} run data modify storage {self.datapack.namespace}:{self.datapack.storage_name} {self.current_object} set value {self.args['string']}",
            ],
        )


@func_property(
    func_type=FuncType.BOOL_FUNCTION,
    call_string="Object.isEqual",
    arg_type={
        "nbt1": ArgType.NBT,
        "nbt2": ArgType.NBT,
    },
    name="object_is_equal",
)
class ObjectIsEqual(JMCFunction):
    current_object = "currentObject"

    def call_bool(self) -> tuple[str, bool, list[str]]:
        bool_result = self.datapack.data.get_current_bool_result()
        nbt1 = self.args["nbt1"]
        nbt2 = self.args["nbt2"]

        return (
            f"score {bool_result} {self.datapack.var_name} matches 0",
            IF,
            [
                f"data modify storage {self.datapack.namespace}:{self.datapack.storage_name} currentObject set from {nbt1}",
                f"execute store success score {bool_result} {self.datapack.var_name} run data modify storage {self.datapack.namespace}:{self.datapack.storage_name} {self.current_object} set from {nbt2}",
            ],
        )
