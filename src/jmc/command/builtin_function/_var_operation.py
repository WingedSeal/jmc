"""Module containing JMCFunction subclasses for custom JMC function that returns a minecraft integer"""

from ...datapack import DataPack
from ..utils import ArgType
from ..jmc_function import JMCFunction, FuncType, func_property
from ...exception import JMCValueError


@func_property(
    func_type=FuncType.VARIABLE_OPERATION,
    call_string='Math.sqrt',
    arg_type={
        "n": ArgType.SCOREBOARD
    },
    name='math_sqrt'
)
class MathSqrt(JMCFunction):
    def call(self) -> str:
        x = '__math__.x'
        x_n = '__math__.x_n'
        x_n_sq = '__main__.x_n_sq'
        N = '__math__.N'
        diff = '__math__.different'
        var = DataPack.var_name
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
                    f"scoreboard players operation {x_n} {var} /= 2 {DataPack.int_name}",
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
                    f"scoreboard players operation {x_n} {var} /= 2 {DataPack.int_name}",
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


@func_property(
    func_type=FuncType.VARIABLE_OPERATION,
    call_string='Math.random',
    arg_type={
        "min": ArgType.SCOREBOARD_PLAYER,
        "max": ArgType.SCOREBOARD_PLAYER
    },
    name='math_random',
    defaults={
        "min": "1",
        "max": "2147483647"
    }
)
class MathRandom(JMCFunction):
    def call(self) -> str:
        seed = '__math__.seed'
        a = '__math__.rng.a'
        c = '__math__.rng.c'
        var = DataPack.var_name
        start = int(self.args["min"])
        end = int(self.args["max"])
        if end < start:
            raise JMCValueError(
                f"max cannot be less than min in {self.call_string}", self.token, self.tokenizer, suggestion="Try swapping max and min")
        if self.call_string not in self.datapack.used_command:
            self.datapack.used_command.add(self.call_string)
            self.datapack.add_private_json('loot_tables', f"{self.name}/rng", {
                "pools": [
                    {"rolls": {"min": 1, "max": 2147483647},
                        "entries": [
                            {
                                "type": "minecraft:item",
                                "name": "minecraft:stone",
                                "functions": [
                                    {
                                        "function": "minecraft:set_count",
                                        "count": 0
                                    }
                                ]
                            }
                    ]
                    }
                ]
            })
            self.datapack.loads.append(
                f"""execute unless score {seed} {var} matches -2147483648..2147483647 run {
                    self.datapack.add_raw_private_function(
                        self.name,
                        [
                            f"execute store result score {seed} {var} run loot spawn ~ ~ ~ loot {self.datapack.namespace}:{DataPack.private_name}/{self.name}/rng",
                            f"execute store result score {a} {var} run loot spawn ~ ~ ~ loot {self.datapack.namespace}:{DataPack.private_name}/{self.name}/rng",
                            f"scoreboard players operation {a} {var} *= {a} {var}",
                            f"execute store result score {c} {var} run loot spawn ~ ~ ~ loot {self.datapack.namespace}:{DataPack.private_name}/{self.name}/rng",
                            f"scoreboard players operation {c} {var} *= {c} {var}"
                        ],
                        'setup'
                    )
                }""")
            self.datapack.add_raw_private_function(
                self.name,
                [
                    f"scoreboard players operation {seed} {var} *= {a} {var}",
                    f"scoreboard players operation {seed} {var} += {c} {var}"
                ],
                'main'
            )

        mod = end - start + 1
        self.datapack.ints.add(mod)

        run = [
            self.datapack.call_func(self.name, 'main'),
            f"scoreboard players operation {self.var} {var} = {seed} {var}",
            f"scoreboard players operation {self.var} {var} %= {mod} {DataPack.int_name}",
            f"scoreboard players add {self.var} {var} {start}"
        ]

        if self.is_execute:
            count = self.datapack.get_count(self.name)
            return self.datapack.add_raw_private_function(
                self.name,
                run,
                count
            )
        return '\n'.join(run)
