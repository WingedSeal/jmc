"""Module containing JMCFunction subclasses for custom JMC function that returns a minecraft integer to a scoreboard variable"""

from ...datapack import DataPack
from ..utils import ArgType
from ..jmc_function import JMCFunction, FuncType, func_property
from ...exception import JMCValueError


@func_property(
    func_type=FuncType.VARIABLE_OPERATION,
    call_string="Math.sqrt",
    arg_type={
        "n": ArgType.SCOREBOARD
    },
    name="math_sqrt"
)
class MathSqrt(JMCFunction):
    def call(self) -> str:
        x = "__math__.x"
        x_n = "__math__.x_n"
        x_n_sq = "__main__.x_n_sq"
        N = "__math__.N"
        diff = "__math__.different"
        var = DataPack.var_name
        if self.is_never_used():
            self.datapack.add_int(2)
            self.datapack.add_raw_private_function(
                self.name,
                [
                    f"scoreboard players operation {x} {var} = {x_n} {var}",
                    f"scoreboard players operation {x_n} {var} = {N} {var}",
                    f"scoreboard players operation {x_n} {var} /= {x} {var}",
                    f"scoreboard players operation {x_n} {var} += {x} {var}",
                    f"scoreboard players operation {x_n} {var} /= 2 {DataPack.int_name}",
                    f"scoreboard players operation {diff} {var} = {x} {var}",
                    f"scoreboard players operation {diff} {var} -= {x_n} {var}",
                    f"execute unless score {diff} {var} matches 0..1 run {self.datapack.call_func(self.name, 'newton_raphson')}",
                ],
                "newton_raphson"
            )
            self.datapack.add_raw_private_function(
                self.name,
                [
                    f"scoreboard players set {x_n} {var} 1225",
                    self.datapack.call_func(self.name, "newton_raphson"),
                    f"scoreboard players operation {x_n_sq} {var} = {x_n} {var}",
                    f"scoreboard players operation {x_n_sq} {var} *= {x_n} {var}",
                    f"execute if score {x_n_sq} {var} > {N} {var} run scoreboard players remove {x_n} {var} 1",
                ],
                "main"
            )

        run = [
            f"scoreboard players operation {N} {var} = {self.args['n']}",
            self.datapack.call_func(self.name, "main"),
            f"scoreboard players operation {self.var} {var} = {x_n} {var}"
        ]

        if self.is_execute:
            count = self.datapack.get_count(self.name)
            return self.datapack.add_raw_private_function(
                self.name,
                run,
                count
            )
        return "\n".join(run)


@func_property(
    func_type=FuncType.VARIABLE_OPERATION,
    call_string="Math.random",
    arg_type={
        "min": ArgType.INTEGER,
        "max": ArgType.INTEGER
    },
    name="math_random",
    defaults={
        "min": "1",
        "max": "2147483647"
    }
)
class MathRandom(JMCFunction):
    def call(self) -> str:
        seed = "__math__.seed"
        result = "__math__.rng.result"
        a = "__math__.rng.a"
        c = "__math__.rng.c"
        bound = "__math__.rng.bound"
        tmp = "__math__.tmp"
        var = DataPack.var_name
        start = int(self.args["min"])
        end = int(self.args["max"])
        if end < start:
            raise JMCValueError(
                f"max cannot be less than min in {self.call_string}", self.token, self.tokenizer, suggestion="Try swapping max and min")
        if self.is_never_used():
            self.datapack.add_load_command(
                f"""execute unless score {seed} {var} matches -2147483648..2147483647 run {
                    self.datapack.add_raw_private_function(
                        self.name,
                        [
                            f'summon area_effect_cloud ~ ~ ~ {{Tags:["{self.datapack.private_name}.{self.name}"]}}',
                            f"execute store result score {seed} {var} run data get entity @e[limit=1,type=area_effect_cloud,tag={self.datapack.private_name}.{self.name}] UUID[0] 1",
                            f"kill @e[type=area_effect_cloud,tag={self.datapack.private_name}.{self.name}]",
                            f"scoreboard players set {a} {var} 656891",
                            f"scoreboard players set {c} {var} 875773"
                        ],
                        "setup"
                    )
                }""")
            self.datapack.add_raw_private_function(
                self.name,
                [
                    # f"execute if score {seed} {var} matches ..0 run scoreboard players add {seed} {var} 2147483647",
                    f"scoreboard players operation {seed} {var} *= {a} {var}",
                    f"scoreboard players operation {seed} {var} += {c} {var}",
                    f"scoreboard players operation {result} {var} = {seed} {var}",

                    f"scoreboard players operation {tmp} {var} = {result} {var}",
                    f"scoreboard players operation {result} {var} %= {bound} {var}",
                    f"scoreboard players operation {tmp} {var} -= {result} {var}",
                    # m = bound - 1
                    f"scoreboard players operation {tmp} {var} += {bound} {var}",
                    # tmp = result - (result % bound) + bound
                    f"execute if score {tmp} {var} matches ..0 run " +
                    self.datapack.call_func(self.name, "main")
                ],
                "main"
            )

        run = [
            f"scoreboard players set {bound} {var} {end - start + 1}",
            self.datapack.call_func(self.name, "main"),
            f"scoreboard players operation {self.var} {var} = {result} {var}",
        ]

        if start:
            run.append(f"scoreboard players add {self.var} {var} {start}")

        if self.is_execute:
            count = self.datapack.get_count(self.name)
            return self.datapack.add_raw_private_function(
                self.name,
                run,
                count
            )
        return "\n".join(run)
