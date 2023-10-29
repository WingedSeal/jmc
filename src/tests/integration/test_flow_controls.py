import sys  # noqa
sys.path.append("./src")  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.compile.test_compile import JMCTestPack


class TestIfElse(unittest.TestCase):

    def test_if(self):
        pack = JMCTestPack().set_jmc_file("""
if (entity condition) {
    say "Hello World";
}
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
execute if entity condition run say Hello World
            """)
        )

    def test_if_else(self):
        pack = JMCTestPack().set_jmc_file("""
if (entity condition) {
    say "TRUE";
} else {
    say "FALSE";
}
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard players set __if_else__ __variable__ 0
execute if entity condition run function TEST:__private__/if_else/0
execute if score __if_else__ __variable__ matches 0 run function TEST:__private__/if_else/1
> VIRTUAL/data/TEST/functions/__private__/if_else/0.mcfunction
say TRUE
scoreboard players set __if_else__ __variable__ 1
> VIRTUAL/data/TEST/functions/__private__/if_else/1.mcfunction
say FALSE
            """)
        )

    def test_if_elif(self):
        pack = JMCTestPack().set_jmc_file("""
if (entity condition) {
    say "CONDITION1";
} else if (entity condition2) {
    say "CONDITION2";
}
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard players set __if_else__ __variable__ 0
execute if entity condition run function TEST:__private__/if_else/0
execute if score __if_else__ __variable__ matches 0 run function TEST:__private__/if_else/1
> VIRTUAL/data/TEST/functions/__private__/if_else/0.mcfunction
say CONDITION1
scoreboard players set __if_else__ __variable__ 1
> VIRTUAL/data/TEST/functions/__private__/if_else/1.mcfunction
execute if entity condition2 run function TEST:__private__/if_else/2
> VIRTUAL/data/TEST/functions/__private__/if_else/2.mcfunction
say CONDITION2
scoreboard players set __if_else__ __variable__ 1
            """)
        )


class TestDoWhile(unittest.TestCase):

    def test_while(self):
        pack = JMCTestPack().set_jmc_file("""
while (entity condition) {
    say "Hello World";
}
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
execute if entity condition run function TEST:__private__/while_loop/0
> VIRTUAL/data/TEST/functions/__private__/while_loop/0.mcfunction
say Hello World
execute if entity condition run function TEST:__private__/while_loop/0
            """)
        )

    def test_do_while(self):
        pack = JMCTestPack().set_jmc_file("""
do {
    say "Hello World";
} while (entity condition);
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
function TEST:__private__/while_loop/0
> VIRTUAL/data/TEST/functions/__private__/while_loop/0.mcfunction
say Hello World
execute if entity condition run function TEST:__private__/while_loop/0
            """)
        )


class TestCondition(unittest.TestCase):
    def test_eq(self):
        pack = JMCTestPack().set_jmc_file("""
if ($i==1) {
    say "Hello World";
}
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
execute if score $i __variable__ matches 1 run say Hello World
            """)
        )

    def test_logic_gate(self):
        pack = JMCTestPack().set_jmc_file("""
if (!entity @s[type=skeleton] || (entity @s[type=zombie] && $deathCount>5)) {
    say "Hello World";
}
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard players set __logic__0 __variable__ 0
execute unless entity @s[type=skeleton] run scoreboard players set __logic__0 __variable__ 1
execute unless score __logic__0 __variable__ matches 1 if entity @s[type=zombie] if score $deathCount __variable__ matches 6.. run scoreboard players set __logic__0 __variable__ 1
execute if score __logic__0 __variable__ matches 1 run say Hello World
            """)
        )


class TestFor(unittest.TestCase):
    def test_for(self):
        pack = JMCTestPack().set_jmc_file("""
for ($i=0;$i<10;$i++) {
    say "Hello World";
}
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard players set $i __variable__ 0
execute if score $i __variable__ matches ..9 run function TEST:__private__/for_loop/0
> VIRTUAL/data/TEST/functions/__private__/for_loop/0.mcfunction
say Hello World
scoreboard players add $i __variable__ 1
execute if score $i __variable__ matches ..9 run function TEST:__private__/for_loop/0
            """)
        )


class TestSwitchCase(unittest.TestCase):
    def test_switch_case(self):
        pack = JMCTestPack().set_jmc_file("""
function askJob() {
    scoreboard players operation $job_id __variable__ = @s job_id;
    switch($job_id) {
        case 1:
            tellraw @s "You are a lumberjack.";
        case 2:
            tellraw @s "You are a policeman.";
        case 3:
            tellraw @s "You are a soldier.";
        case 4:
            tellraw @s "You are a doctor.";
        case 5:
            tellraw @s "You are a pilot.";
        case 6:
            tellraw @s "You are a god?";
    }
}
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/functions/askjob.mcfunction
scoreboard players operation $job_id __variable__ = @s job_id
scoreboard players operation __switch__0 __variable__ = $job_id __variable__
function TEST:__private__/switch_case/0
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
> VIRTUAL/data/TEST/functions/__private__/switch_case/0.mcfunction
execute if score __switch__0 __variable__ matches 1..3 run function TEST:__private__/switch_case/1
execute if score __switch__0 __variable__ matches 4..6 run function TEST:__private__/switch_case/2
> VIRTUAL/data/TEST/functions/__private__/switch_case/1.mcfunction
execute if score __switch__0 __variable__ matches 1 run function TEST:__private__/switch_case/3
execute if score __switch__0 __variable__ matches 2..3 run function TEST:__private__/switch_case/4
> VIRTUAL/data/TEST/functions/__private__/switch_case/3.mcfunction
tellraw @s "You are a lumberjack."
> VIRTUAL/data/TEST/functions/__private__/switch_case/4.mcfunction
execute if score __switch__0 __variable__ matches 2 run function TEST:__private__/switch_case/5
execute if score __switch__0 __variable__ matches 3 run function TEST:__private__/switch_case/6
> VIRTUAL/data/TEST/functions/__private__/switch_case/5.mcfunction
tellraw @s "You are a policeman."
> VIRTUAL/data/TEST/functions/__private__/switch_case/6.mcfunction
tellraw @s "You are a soldier."
> VIRTUAL/data/TEST/functions/__private__/switch_case/2.mcfunction
execute if score __switch__0 __variable__ matches 4 run function TEST:__private__/switch_case/7
execute if score __switch__0 __variable__ matches 5..6 run function TEST:__private__/switch_case/8
> VIRTUAL/data/TEST/functions/__private__/switch_case/7.mcfunction
tellraw @s "You are a doctor."
> VIRTUAL/data/TEST/functions/__private__/switch_case/8.mcfunction
execute if score __switch__0 __variable__ matches 5 run function TEST:__private__/switch_case/9
execute if score __switch__0 __variable__ matches 6 run function TEST:__private__/switch_case/10
> VIRTUAL/data/TEST/functions/__private__/switch_case/9.mcfunction
tellraw @s "You are a pilot."
> VIRTUAL/data/TEST/functions/__private__/switch_case/10.mcfunction
tellraw @s "You are a god?"
            """)
        )


if __name__ == "__main__":
    unittest.main()
