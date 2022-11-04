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
    def call_bool(self) -> tuple[str, bool]:
        return f'score {self.args["selector"]} {self.args["objective"]} matches 1..', UNLESS
