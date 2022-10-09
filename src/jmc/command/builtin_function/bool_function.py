"""Module containing JMCFunction subclasses for custom JMC function that returns a part of `/execute if` command"""

from ..utils import ArgType
from ..jmc_function import JMCFunction, FuncType

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

    def call_bool(self) -> tuple[str, bool]:
        return f'score {self.args["target_selector"]} {self.args["objective"]} matches 1..', UNLESS
