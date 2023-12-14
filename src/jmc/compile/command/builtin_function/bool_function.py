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
    :return: True | False
    """
    parts = source.split('-')
    return len(parts) == 5 and all(len(part) in (8, 4, 4, 4, 12) and part.isalnum() for part in parts)
    
def get_nbt_type(source: str) -> str:
    """
    Gets the type of data based on the data source.

    :param source: Source of the data
    :return: A string representing the type of NBT data
    """
    if source.startswith("@") or is_uuid(source):
        return "entity"
    elif re.match(r'^[~\^]?-?\d*(\.\d+)?\s[~\^]?-?\d*(\.\d+)?\s[~\^]?-?\d*(\.\d+)?[~\^]?$', source): # checks if the string is block coord with regex
        return "block"
    return "storage"


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
        source_type = get_nbt_type()
        if source_type == "storage" and ":" not in self.args["source"]:
            source = f"{self.datapack.namespace}:{source}"

        return f"score {bool_result} {self.datapack.var_name} matches 0", IF, [
            f"data modify storage {self.datapack.namespace}:{self.datapack.storage_name} currentObject set from {source_type} {source} {self.args['path']}",
            f"execute store success score {bool_result} {self.datapack.var_name} run data modify storage {self.datapack.namespace}:{self.datapack.storage_name} {self.current_object} set value {self.args['string']}"
        ]


@func_property(
    func_type=FuncType.BOOL_FUNCTION,
    call_string="Object.isEqual",
    arg_type={
        "source1": ArgType.STRING,
        "path1": ArgType.KEYWORD,
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
        type1 = get_nbt_type(source1)
        type2 = get_nbt_type(source2)
        if type1 == "storage" and ":" not in self.args["source1"]:
            source1 = f"{self.datapack.namespace}:{source1}"
        if type2 == "storage" and ":" not in self.args["source2"]:
            source2 = f"{self.datapack.namespace}:{source2}"

        return f"score {bool_result} {self.datapack.var_name} matches 0", IF, [
            f"data modify storage {self.datapack.namespace}:{self.datapack.storage_name} currentObject set from {type1} {source1} {self.args['path1']}",  # noqa
            f"execute store success score {bool_result} {self.datapack.var_name} run data modify storage {self.datapack.namespace}:{self.datapack.storage_name} {self.current_object} set from {type2} {source2} {self.args['path2']}"  # noqa
        ]
