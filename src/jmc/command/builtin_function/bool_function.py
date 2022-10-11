"""Module containing JMCFunction subclasses for custom JMC function that returns a part of `/execute if` command"""

from ..utils import ArgType
from ..jmc_function import JMCFunction, FuncType, func_property

IF = True
UNLESS = False


@func_property(
    func_type=FuncType.bool_function,
    call_string='Timer.isOver',
    arg_type={
        "objective": ArgType.keyword,
        "target_selector": ArgType.selector
    },
    name='timer_is_over',
    defaults={
        "target_selector": "@s"
    }
)
class TimerIsOver(JMCFunction):
    def call_bool(self) -> tuple[str, bool]:
        return f'score {self.args["target_selector"]} {self.args["objective"]} matches 1..', UNLESS
