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

class NbtSource: 
    def __init__(self, source: str):
        self.source = source

    def is_uuid(source: str) -> bool:
        parts = source.split('-')
        return len(parts) == 5 and all(len(part) in (8, 4, 4, 4, 12) and part.isalnum() for part in parts)
    
    def get_type(source: str) -> str:
        if source.startswith("@") or NbtSource.is_uuid(source):
            return "entity"
        elif re.match(r'^[~\^]?-?\d*(\.\d+)?\s[~\^]?-?\d*(\.\d+)?\s[~\^]?-?\d*(\.\d+)?[~\^]?$', source): # checks if the string is block coord with regex
            return "block"
        return "storage"
    

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
        # source = self.args["source"]
        source = NbtSource(self.args["source"])
        source_type = source.get_type()
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
        source1 = NbtSource(self.args["source1"])
        source2 = NbtSource(self.args["source2"])
        type1 = source1.get_type()
        type2 = source2.get_type()
        if type1 == "storage" and ":" not in self.args["source1"]:
            source1 = f"{self.datapack.namespace}:{source1}"
        if type2 == "storage" and ":" not in self.args["source2"]:
            source2 = f"{self.datapack.namespace}:{source2}"

        return f"score {bool_result} {self.datapack.var_name} matches 0", IF, [
            f"data modify storage {self.datapack.namespace}:{self.datapack.storage_name} currentObject set from {type1} {source1} {self.args['path1']}",
            f"execute store success score {bool_result} {self.datapack.var_name} run data modify storage {self.datapack.namespace}:{self.datapack.storage_name} {self.current_object} set from {type2} {source2} {self.args['path2']}"
        ]
    