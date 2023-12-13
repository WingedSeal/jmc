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
    """
    A class that represents a data source and provides methods to get the type of data.
    """
    def __init__(self: str, source: str):
        """Initializes a new instance of the NbtSource class.

        Args:
            source (str): The source of the data.
        """
        self.source = source

    def is_uuid(source: str) -> bool:
        """Checks if the given string is a UUID.

        Args:
            source (str): The string to check.

        Returns:
            bool: True if the string is a UUID; otherwise, False.
        """
        parts = source.split('-')
        return len(parts) == 5 and all(len(part) in (8, 4, 4, 4, 12) and part.isalnum() for part in parts)
    
    def get_type(self) -> str:
        """Gets the type of data based on the data source.

        Returns:
            str: The type of data.
        """
        if self.source.startswith("@") or NbtSource.is_uuid(self.source):
            return "entity"
        elif re.match(r'^[~\^]?-?\d*(\.\d+)?\s[~\^]?-?\d*(\.\d+)?\s[~\^]?-?\d*(\.\d+)?[~\^]?$', self.source): # checks if the string is block coord with regex
            return "block"
        return "storage"
    
    def __str__(self):
        """Returns a string representation of the NbtSource object."""
        return f"{self.source}"


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
    