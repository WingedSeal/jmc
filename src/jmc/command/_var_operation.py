from ..exception import JMCTypeError
from ..datapack import DataPack
from .utils import ArgType
from .jmc_function import JMCFunction, FuncType


class MathSqrt(JMCFunction):
    func_type = FuncType.variable_operation
    call_string = 'Math.sqrt'
    arg_type = {
        "n": ArgType.scoreboard
    }
    name = 'mart_sqrt'

    def call(self) -> str:
        x = '__math__.x'
        x_n = '__math__.x_n'
        x_n_sq = '__main__.x_n_sq'
        N = '__math__.N'
        diff = '__math__.different'
        var = DataPack.VAR_NAME
        if self.call_string not in self.datapack.used_command:
            self.datapack.used_command.add(self.call_string)
            self.datapack.ints.add(2)
            self.datapack.add_raw_private_function(
                self.name,
                [
                    f"scoreboard players operation {x} {var} = {x_n} {var}",
                    f"scoreboard players operation {x_n} {var} = {N} {var}",
                    f"scoreboard players operation {x_n} {var} /= {x} {var}",
                    f"scoreboard players operation {x_n} {var} += {x} {var}",
                    f"scoreboard players operation {x_n} {var} /= 2 {DataPack.INT_NAME}",
                    f"scoreboard players operation {diff} {var} = {x} {var}",
                    f"scoreboard players operation {diff} {var} -= {x_n} {var}",
                    f"execute unless score {diff} {var} 0..1 run {self.datapack.call_func(self.name, 'newton_raphson')}",
                ],
                'newton_raphson'
            )
            self.datapack.add_raw_private_function(
                self.name,
                [
                    f"scoreboard players set {x_n} {var} 1225",
                    self.datapack.call_func(self.name, 'newton_raphson'),
                    f"scoreboard players operation {x_n_sq} {var} = {x_n} {var}",
                    f"scoreboard players operation {x_n_sq} {var} *= {x_n} {var}",
                    f"scoreboard players operation {x_n} {var} /= 2 {DataPack.INT_NAME}",
                    f"scoreboard players operation {diff} {var} = {x} {var}",
                    f"scoreboard players operation {diff} {var} -= {x_n} {var}",
                    f"execute if score {x_n_sq} {var} > {N} {var} run scoreboard players remove {x_n} {var} 1",
                ],
                'main'
            )

        run = [
            f"scoreboard players operation {N} {var} = {self.args['n']}",
            self.datapack.call_func(self.name, 'main'),
            f"scoreboard players operation {self.var} {var} = {x_n} {var}"
        ]

        if self.is_execute:
            count = self.datapack.get_count(self.name)
            return self.datapack.add_raw_private_function(
                self.name,
                run,
                count
            )
        return '\n'.join(run)


class MathRandom(JMCFunction):
    func_type = FuncType.variable_operation
    call_string = 'Math.random'
    arg_type = {
    }
    name = 'mart_random'
