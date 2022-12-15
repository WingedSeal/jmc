"""Module containing JMCFunction subclasses for custom JMC function that returns a part of `/execute if` command"""

from ..utils import ArgType
from ..jmc_function import JMCFunction, FuncType, func_property

IF = True
UNLESS = False


@func_property(
    func_type=FuncType.BOOL_FUNCTION,
    call_string='Timer.isOver',
    arg_type={
        "objective": ArgType.KEYWORD,
        "selector": ArgType.SELECTOR
    },
    name='timer_is_over',
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
    call_string='String.isEqual',
    arg_type={
        "storage": ArgType.KEYWORD,
        "path": ArgType.KEYWORD,
        "string": ArgType.STRING
    },
    name='string_is_equal'
)
class StringIsEqual(JMCFunction):
    current_object = "currentObject"

    def call_bool(self) -> tuple[str, bool, list[str]]:
        bool_result = self.datapack.data.get_current_bool_result()
        return f'score {bool_result} {self.datapack.var_name} matches 0', IF, [
            f"data modify storage {self.datapack.namespace}:{self.datapack.storage_name} currentObject set from storage {self.datapack.namespace}:{self.args['storage']} {self.args['path']}",
            f"execute store result score {bool_result} {self.datapack.var_name} run data modify storage {self.datapack.namespace}:{self.datapack.storage_name} {self.current_object} set value {self.args['string']}"
        ]
