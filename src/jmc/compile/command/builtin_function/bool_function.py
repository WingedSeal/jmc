"""Module containing JMCFunction subclasses for custom JMC function that returns a part of `/execute if` command"""

from ..utils import ArgType
from ..jmc_function import JMCFunction, FuncType, func_property
from ...exception import JMCValueError
import re

IF = True
UNLESS = False


def is_uuid(source: str) -> bool:
    """
    Tells whether source of the data is minecraft UUID or not

    :param source: Source of the data
    :return: Whether the source is in a minecraft UUID format
    """
    parts = source.split("-")
    return len(parts) == 5 and all(
        len(part) in (8, 4, 4, 4, 12) and part.isalnum() for part in parts
    )


MINECRAFT_POSITION_REGEX = (
    r"^[~\^]?-?\d*(\.\d+)?\s+[~\^]?-?\d*(\.\d+)?\s+[~\^]?-?\d*(\.\d+)?[~\^]?$"
)


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
        "nbt1": ArgType.STRING,
        "nbt2": ArgType.STRING,
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
