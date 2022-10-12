import sys  # noqa
sys.path.append('./src')  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.test_compile import JMCPack

from jmc.exception import JMCMissingValueError, JMCSyntaxException, JMCValueError

class TestVarOperation(unittest.TestCase):
    def test_MathSqrt(self):
        pack = JMCPack().set_jmc_file("""
$i = Math.sqrt($x);
$i = Math.sqrt($i);
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
scoreboard objectives add __int__ dummy
scoreboard players set 2 __int__ 2
scoreboard players operation __math__.N __variable__ = $x __variable__
function TEST:__private__/math_sqrt/main
scoreboard players operation $i __variable__ = __math__.x_n __variable__
scoreboard players operation __math__.N __variable__ = $i __variable__
function TEST:__private__/math_sqrt/main
scoreboard players operation $i __variable__ = __math__.x_n __variable__
> VIRTUAL/data/TEST/functions/__private__/math_sqrt/newton_raphson.mcfunction
scoreboard players operation __math__.x __variable__ = __math__.x_n __variable__
scoreboard players operation __math__.x_n __variable__ = __math__.N __variable__
scoreboard players operation __math__.x_n __variable__ /= __math__.x __variable__
scoreboard players operation __math__.x_n __variable__ += __math__.x __variable__
scoreboard players operation __math__.x_n __variable__ /= 2 __int__
scoreboard players operation __math__.different __variable__ = __math__.x __variable__
scoreboard players operation __math__.different __variable__ -= __math__.x_n __variable__
execute unless score __math__.different __variable__ 0..1 run function TEST:__private__/math_sqrt/newton_raphson
> VIRTUAL/data/TEST/functions/__private__/math_sqrt/main.mcfunction
scoreboard players set __math__.x_n __variable__ 1225
function TEST:__private__/math_sqrt/newton_raphson
scoreboard players operation __main__.x_n_sq __variable__ = __math__.x_n __variable__
scoreboard players operation __main__.x_n_sq __variable__ *= __math__.x_n __variable__
scoreboard players operation __math__.x_n __variable__ /= 2 __int__
scoreboard players operation __math__.different __variable__ = __math__.x __variable__
scoreboard players operation __math__.different __variable__ -= __math__.x_n __variable__
execute if score __main__.x_n_sq __variable__ > __math__.N __variable__ run scoreboard players remove __math__.x_n __variable__ 1
            """)
        )

        with self.assertRaises(JMCMissingValueError):
            JMCPack().set_jmc_file("""
$x = Math.sqrt();
        """).build()

        with self.assertRaises(JMCValueError):
            JMCPack().set_jmc_file("""
$x = Math.sqrt(10);
        """).build()

    def test_MathRandom(self):
        pack = JMCPack().set_jmc_file("""
$x = Math.random();
$y = Math.random(min=5, max=10);
$z = Math.random(max=10);
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
scoreboard objectives add __int__ dummy
scoreboard players set 10 __int__ 10
scoreboard players set 6 __int__ 6
scoreboard players set 2147483647 __int__ 2147483647
execute unless score __math__.seed __variable__ matches -2147483648..2147483647 run function TEST:__private__/math_random/setup
function TEST:__private__/math_random/main
scoreboard players operation $x __variable__ = __math__.seed __variable__
scoreboard players operation $x __variable__ %= 2147483647 __int__
scoreboard players add $x __variable__ 1
function TEST:__private__/math_random/main
scoreboard players operation $y __variable__ = __math__.seed __variable__
scoreboard players operation $y __variable__ %= 6 __int__
scoreboard players add $y __variable__ 5
function TEST:__private__/math_random/main
scoreboard players operation $z __variable__ = __math__.seed __variable__
scoreboard players operation $z __variable__ %= 10 __int__
scoreboard players add $z __variable__ 1
> VIRTUAL/data/TEST/functions/__private__/math_random/setup.mcfunction
execute store result score __math__.seed __variable__ run loot spawn ~ ~ ~ loot TEST:__private__/math_random/rng
execute store result score __math__.rng.a __variable__ run loot spawn ~ ~ ~ loot TEST:__private__/math_random/rng
scoreboard players operation __math__.rng.a __variable__ *= __math__.rng.a __variable__
execute store result score __math__.rng.c __variable__ run loot spawn ~ ~ ~ loot TEST:__private__/math_random/rng
scoreboard players operation __math__.rng.c __variable__ *= __math__.rng.c __variable__
> VIRTUAL/data/TEST/functions/__private__/math_random/main.mcfunction
scoreboard players operation __math__.seed __variable__ *= __math__.rng.a __variable__
scoreboard players operation __math__.seed __variable__ += __math__.rng.c __variable__
> VIRTUAL/data/TEST/loot_tables/__private__/math_random/rng.json
{
  "pools": [
    {
      "rolls": {
        "min": 1,
        "max": 2147483647
      },
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
}
            """)
        )

        with self.assertRaises(JMCValueError):
            JMCPack().set_jmc_file("""
$x = Math.random(min=100,max=1);
        """).build()


class TestBoolFunction(unittest.TestCase):
    def test_TimerIsOver(self):
        pack = JMCPack().set_jmc_file("""
if (Timer.isOver(my_objective)) {
    say "Timer is over";
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
scoreboard objectives add __int__ dummy
execute unless score @s my_objective matches 1.. run say Timer is over
            """)
        )


class TestExecuteExcluded(unittest.TestCase):
    def test_error_execute(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
execute as @a run Hardcode.repeat();
            """).build()

        with self.assertRaises(JMCMissingValueError):
            JMCPack().set_jmc_file("""
Hardcode.repeat();
            """).build()

    def test_HardcodeRepeat(self):
        pack = JMCPack().set_jmc_file("""
Hardcode.repeat("index", ()=>{
    tellraw @a "Hello World: index";
}, start=1, stop=6, step=1); 
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
scoreboard objectives add __int__ dummy
tellraw @a "Hello World: 1"
tellraw @a "Hello World: 2"
tellraw @a "Hello World: 3"
tellraw @a "Hello World: 4"
tellraw @a "Hello World: 5"
            """)
        )

    def test_HardcodeCalc(self):
        pack = JMCPack().set_jmc_file("""
Hardcode.repeat("index", ()=>{
    tellraw @a "index^2=Hardcode.calc(index**2)";
}, start=1, stop=6, step=1);  
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
scoreboard objectives add __int__ dummy
tellraw @a "1^2=1"
tellraw @a "2^2=4"
tellraw @a "3^2=9"
tellraw @a "4^2=16"
tellraw @a "5^2=25"
            """)
        )

    def test_HardcodeSwitch(self):
        pack = JMCPack().set_jmc_file("""
Hardcode.switch($var, "index", ()=>{
    tellraw @s "index";
    tellraw @s "Hardcode.calc(index**2)";
}, count=5);
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
scoreboard objectives add __int__ dummy
function TEST:__private__/hard_code_switch/0
> VIRTUAL/data/TEST/functions/__private__/hard_code_switch/0.mcfunction
execute if score $var __variable__ matches 1..2 run function TEST:__private__/hard_code_switch/1
execute if score $var __variable__ matches 3..5 run function TEST:__private__/hard_code_switch/2
> VIRTUAL/data/TEST/functions/__private__/hard_code_switch/1.mcfunction
execute if score $var __variable__ matches 1 run function TEST:__private__/hard_code_switch/3
execute if score $var __variable__ matches 2 run function TEST:__private__/hard_code_switch/4
> VIRTUAL/data/TEST/functions/__private__/hard_code_switch/3.mcfunction
tellraw @s "1"
tellraw @s "1"
> VIRTUAL/data/TEST/functions/__private__/hard_code_switch/4.mcfunction
tellraw @s "2"
tellraw @s "4"
> VIRTUAL/data/TEST/functions/__private__/hard_code_switch/2.mcfunction
execute if score $var __variable__ matches 3 run function TEST:__private__/hard_code_switch/5
execute if score $var __variable__ matches 4..5 run function TEST:__private__/hard_code_switch/6
> VIRTUAL/data/TEST/functions/__private__/hard_code_switch/5.mcfunction
tellraw @s "3"
tellraw @s "9"
> VIRTUAL/data/TEST/functions/__private__/hard_code_switch/6.mcfunction
execute if score $var __variable__ matches 4 run function TEST:__private__/hard_code_switch/7
execute if score $var __variable__ matches 5 run function TEST:__private__/hard_code_switch/8
> VIRTUAL/data/TEST/functions/__private__/hard_code_switch/7.mcfunction
tellraw @s "4"
tellraw @s "16"
> VIRTUAL/data/TEST/functions/__private__/hard_code_switch/8.mcfunction
tellraw @s "5"
tellraw @s "25"
            """)
        )


class TestJMCCommand(unittest.TestCase):
    def test_TimerSet(self):
        pack = JMCPack().set_jmc_file("""
Timer.set(my_objective, @a, $i); 
Timer.set(my_objective, @s, 5); 
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
scoreboard objectives add __int__ dummy
scoreboard players operations @a my_objective = $i __variable__
scoreboard players set @s my_objective 5
            """)
        )

    def test_ParticleCircle(self):
        pack = JMCPack().set_jmc_file("""
Particle.circle("dust 1.0 1.0 1.0 0.7", radius=2, spread=10);
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
scoreboard objectives add __int__ dummy
function TEST:__private__/particle_circle/0
> VIRTUAL/data/TEST/functions/__private__/particle_circle/0.mcfunction
particle dust 1.0 1.0 1.0 0.7 ^2.0000000000 ^ ^ 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^1.6180339887 ^ ^1.1755705046 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^0.6180339887 ^ ^1.9021130326 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-0.6180339887 ^ ^1.9021130326 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-1.6180339887 ^ ^1.1755705046 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-2.0000000000 ^ ^0.0000000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-1.6180339887 ^ ^-1.1755705046 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-0.6180339887 ^ ^-1.9021130326 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^0.6180339887 ^ ^-1.9021130326 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^1.6180339887 ^ ^-1.1755705046 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^2.0000000000 ^ ^-0.0000000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^1.6180339887 ^ ^1.1755705046 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^0.6180339887 ^ ^1.9021130326 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-0.6180339887 ^ ^1.9021130326 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-1.6180339887 ^ ^1.1755705046 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-2.0000000000 ^ ^0.0000000000 0 0 0 1 1 normal
            """)
        )

    def test_ParticleSpiral(self):
        pack = JMCPack().set_jmc_file("""
Particle.spiral("dust 1.0 1.0 1.0 0.7", radius=1, height=1, spread=10);
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
scoreboard objectives add __int__ dummy
function TEST:__private__/particle_spiral/0
> VIRTUAL/data/TEST/functions/__private__/particle_spiral/0.mcfunction
particle dust 1.0 1.0 1.0 0.7 ^1.0000000000 ^ ^ 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^0.8090169944 ^0.1000000000 ^0.5877852523 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^0.3090169944 ^0.2000000000 ^0.9510565163 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-0.3090169944 ^0.3000000000 ^0.9510565163 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-0.8090169944 ^0.4000000000 ^0.5877852523 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-1.0000000000 ^0.5000000000 ^0.0000000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-0.8090169944 ^0.6000000000 ^-0.5877852523 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-0.3090169944 ^0.7000000000 ^-0.9510565163 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^0.3090169944 ^0.8000000000 ^-0.9510565163 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^0.8090169944 ^0.9000000000 ^-0.5877852523 0 0 0 1 1 normal
            """)
        )

    def test_ParticleCylinder(self):
        pack = JMCPack().set_jmc_file("""
Particle.spiral("dust 1.0 1.0 1.0 0.7", radius=1, height=1, spread=10);
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
scoreboard objectives add __int__ dummy
function TEST:__private__/particle_spiral/0
> VIRTUAL/data/TEST/functions/__private__/particle_spiral/0.mcfunction
particle dust 1.0 1.0 1.0 0.7 ^1.0000000000 ^ ^ 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^0.8090169944 ^0.1000000000 ^0.5877852523 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^0.3090169944 ^0.2000000000 ^0.9510565163 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-0.3090169944 ^0.3000000000 ^0.9510565163 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-0.8090169944 ^0.4000000000 ^0.5877852523 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-1.0000000000 ^0.5000000000 ^0.0000000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-0.8090169944 ^0.6000000000 ^-0.5877852523 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^-0.3090169944 ^0.7000000000 ^-0.9510565163 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^0.3090169944 ^0.8000000000 ^-0.9510565163 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^0.8090169944 ^0.9000000000 ^-0.5877852523 0 0 0 1 1 normal
            """)
        )

class TestLoadOnce(unittest.TestCase):
    def test_error_load_twice(self): ...
    def test_error_no_load(self): ...
    def test_PlayerFirstJoin(self): ...
    def test_PlayerRejoin(self): ...
    def test_PlayerDie(self): ...


class TestLoadOnly(unittest.TestCase):
    def test_error_no_load(self): ...
    def test_RightClickSetup(self): ...
    def test_PlayerOnEvent(self): ...
    def test_TriggerSetup(self): ...
    def test_TimerAdd(self): ...
    def test_RecipeTable(self): ...


if __name__ == '__main__':
    unittest.main()
