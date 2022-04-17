from ..utils import ArgType
from ..jmc_function import JMCFunction, FuncType, func_property


@func_property(
    func_type=FuncType.jmc_command,
    call_string='Timer.set',
    arg_type={
        "objective": ArgType.keyword,
        "target_selector": ArgType.selector,
        "tick": ArgType.scoreboard_player
    },
    name='timer_set'
)
class TimerSet(JMCFunction):
    def call(self) -> str:
        if self.args_Args["tick"].arg_type == ArgType.integer:
            return f'scoreboard players set {self.args["target_selector"]} {self.args["objective"]} {self.args["tick"]}'
        else:
            return f'scoreboard players operations {self.args["target_selector"]} {self.args["objective"]} = {self.args["tick"]}'
