from ..exception import JMCTypeError
from ..datapack import DataPack
from .utils import ArgType
from .jmc_function import JMCFunction, FuncType


class TimerSet(JMCFunction):
    func_type = FuncType.jmc_command
    call_string = 'Timer.set'
    arg_type = {
        "objective": ArgType.keyword,
        "target_selector": ArgType.selector,
        "tick": ArgType.scoreboard_player
    }
    name = 'timer_set'

    def call(self) -> str:
        if self._args["tick"].arg_type == ArgType.integer:
            return f'scoreboard players set {self.args["target_selector"]} {self.args["objective"]} {self.args["tick"]}'
        else:
            return f'scoreboard players operations {self.args["target_selector"]} {self.args["objective"]} = {self.args["tick"]}'
