from ..exception import JMCTypeError
from ..datapack import DataPack
from .utils import ArgType
from .jmc_function import JMCFunction, FuncType

IF = True
UNLESS = False


class TimerIsOver(JMCFunction):
    func_type = FuncType.bool_function
    call_string = 'Timer.isOver'
    arg_type = {
        "objective": ArgType.keyword,
        "target_selector": ArgType.selector
    }
    name = 'timer_is_over'
    defaults = {
        "target_selector": "@s"
    }

    def call(self) -> tuple[str, bool]:
        return f'score {self.args["target_selector"]} {self.args["objective"]} matches 1..', UNLESS
