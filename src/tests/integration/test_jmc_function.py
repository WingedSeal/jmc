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
Particle.circle("dust 1.0 1.0 1.0 0.7", radius=2.0, spread=10);
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
Particle.spiral("dust 1.0 1.0 1.0 0.7", radius=1, height=1.0, spread=10);
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

    def test_ParticleLine(self):
        pack = JMCPack().set_jmc_file("""
Particle.line("dust 1.0 1.0 1.0 0.7", distance=10.5, spread=10);
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
function TEST:__private__/particle_line/0
> VIRTUAL/data/TEST/functions/__private__/particle_line/0.mcfunction
particle dust 1.0 1.0 1.0 0.7 ^ ^ ^1.0000000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^ ^ ^2.0500000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^ ^ ^3.1000000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^ ^ ^4.1500000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^ ^ ^5.2000000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^ ^ ^6.2500000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^ ^ ^7.3000000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^ ^ ^8.3500000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^ ^ ^9.4000000000 0 0 0 1 1 normal
particle dust 1.0 1.0 1.0 0.7 ^ ^ ^10.4500000000 0 0 0 1 1 normal
            """)
        )


class TestLoadOnce(unittest.TestCase):
    def test_error_load_twice(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
Player.firstJoin(()=>{
    tellraw @s "Welcome!";
});
Player.firstJoin(()=>{
    tellraw @s "Welcome!";
});
            """).build()

    def test_error_no_load(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
function test() {
    Player.firstJoin(()=>{
        tellraw @s "Welcome!";
    });
}

            """).build()

    def test_PlayerFirstJoin(self):
        pack = JMCPack().set_jmc_file("""
Player.firstJoin(()=>{
    tellraw @s "Welcome!";
});
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
> VIRTUAL/data/TEST/functions/__private__/player_first_join/main.mcfunction
tellraw @s "Welcome!"
> VIRTUAL/data/TEST/advancements/__private__/player_first_join.json
{
  "criteria": {
    "requirement": {
      "trigger": "minecraft:tick"
    }
  },
  "rewards": {
    "function": "TEST:__private__/player_first_join/main"
  }
}
            """)
        )

    def test_PlayerRejoin(self):
        pack = JMCPack().set_jmc_file("""
Player.rejoin(()=>{
    tellraw @s "Welcome!";
});
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
> VIRTUAL/data/minecraft/tags/functions/tick.json
{
  "values": [
    "TEST:__tick__"
  ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
scoreboard objectives add __rejoin__ custom:leave_game
> VIRTUAL/data/TEST/functions/__tick__.mcfunction
execute as @a[scores={__rejoin__=1..}] at @s run function TEST:__private__/player_rejoin/main
> VIRTUAL/data/TEST/functions/__private__/player_rejoin/main.mcfunction
scoreboard players reset @s __rejoin__
tellraw @s "Welcome!"
            """)
        )

    def test_PlayerDie(self):
        pack = JMCPack().set_jmc_file("""
Player.die(onDeath=()=>{
    tellraw @s "You died";
},onRespawn=()=>{
    tellraw @s "Welcome back to live";
    say "I'm back";
});
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
> VIRTUAL/data/minecraft/tags/functions/tick.json
{
  "values": [
    "TEST:__tick__"
  ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
scoreboard objectives add __die__ deathCount
> VIRTUAL/data/TEST/functions/__tick__.mcfunction
execute as @a[scores={__die__=1..}] at @s run function TEST:__private__/player_die/on_death
execute as @e[type=player,scores={__die__=2..}] at @s run function TEST:__private__/player_die/on_respawn
> VIRTUAL/data/TEST/functions/__private__/player_die/on_death.mcfunction
scoreboard players set @s __die__ 2
tellraw @s "You died"
> VIRTUAL/data/TEST/functions/__private__/player_die/on_respawn.mcfunction
scoreboard players reset @s __die__
tellraw @s "Welcome back to live"
say I'm back
            """)
        )


class TestLoadOnly(unittest.TestCase):
    def test_error_no_load(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
function notLoad() {
    Timer.add(help_cd, runOnce, @a, ()=>{
        tellraw @s "Your help command is ready!";
    });
}
            """).build()

    def test_RightClickSetup(self):
        pack = JMCPack().set_jmc_file("""
RightClick.setup(
    custom_id,
    {
        1: ()=>{
            say "1";
        },
        2: ()=>{
            say "2";
        }
    }
);
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
> VIRTUAL/data/minecraft/tags/functions/tick.json
{
  "values": [
    "TEST:__tick__"
  ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
scoreboard objectives add __rc__custom_id used:carrot_on_a_stick
> VIRTUAL/data/TEST/functions/__tick__.mcfunction
execute as @a[scores={__rc__custom_id=1..}] at @s run function TEST:__private__/right_click_setup/main
> VIRTUAL/data/TEST/functions/__private__/right_click_setup/main.mcfunction
scoreboard players reset @s __rc__custom_id
execute store result score __item_id__ __variable__ run data get entity @s SelectedItem.tag.custom_id
execute if score __item_id__ __variable__ matches 1.. run function TEST:__private__/right_click_setup/1
> VIRTUAL/data/TEST/functions/__private__/right_click_setup/1.mcfunction
execute if score @s __item_id__ matches 1 run function TEST:__private__/right_click_setup/2
execute if score @s __item_id__ matches 2 run function TEST:__private__/right_click_setup/3
> VIRTUAL/data/TEST/functions/__private__/right_click_setup/2.mcfunction
say 1
> VIRTUAL/data/TEST/functions/__private__/right_click_setup/3.mcfunction
say 2
            """)
        )

    def test_PlayerOnEvent(self):
        pack = JMCPack().set_jmc_file("""
Player.onEvent(my_objective, ()=>{
    say "Hello World";
});
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
> VIRTUAL/data/minecraft/tags/functions/tick.json
{
  "values": [
    "TEST:__tick__"
  ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
> VIRTUAL/data/TEST/functions/__tick__.mcfunction
execute as @a[scores={my_objective=1..}] at @s run function TEST:__private__/player_on_event/0
> VIRTUAL/data/TEST/functions/__private__/player_on_event/0.mcfunction
scoreboard players reset @s my_objective
say Hello World
            """)
        )

    def test_TriggerSetup(self):
        pack = JMCPack().set_jmc_file("""
Trigger.setup(help, {
    1: ()=>{
        tellraw @s {"text":"Cool help commands", "color":"gold"}
    }
});
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
> VIRTUAL/data/minecraft/tags/functions/tick.json
{
  "values": [
    "TEST:__tick__"
  ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
scoreboard objectives add help trigger
> VIRTUAL/data/TEST/functions/__tick__.mcfunction
function TEST:__private__/trigger_setup/main
function TEST:__private__/trigger_setup/enable
> VIRTUAL/data/TEST/functions/__private__/trigger_setup/main.mcfunction
execute as @a[scores={help=1..}] at @s run function TEST:__private__/trigger_setup/0
> VIRTUAL/data/TEST/functions/__private__/trigger_setup/enable.mcfunction
scoreboard players enable @s help
> VIRTUAL/data/TEST/functions/__private__/trigger_setup/1.mcfunction
tellraw @s {"text":"Cool help commands","color":"gold"}
> VIRTUAL/data/TEST/functions/__private__/trigger_setup/0.mcfunction
function TEST:__private__/trigger_setup/1
scoreboard players reset @s help
scoreboard players enable @s help
> VIRTUAL/data/TEST/advancements/__private__/trigger_setup/enable.json
{
  "criteria": {
    "requirement": {
      "trigger": "minecraft:tick"
    }
  },
  "rewards": {
    "function": "TEST:__private__/trigger_setup/enable"
  }
}
            """)
        )

    def test_TimerAdd(self):
        pack = JMCPack().set_jmc_file("""
Timer.add(help_cd, runOnce, @a, ()=>{
    tellraw @s "Your help command is ready!";
});
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
> VIRTUAL/data/minecraft/tags/functions/tick.json
{
  "values": [
    "TEST:__tick__"
  ]
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
scoreboard objectives add dummy help_cd
> VIRTUAL/data/TEST/functions/__tick__.mcfunction
function TEST:__private__/timer_add/main
> VIRTUAL/data/TEST/functions/__private__/timer_add/main.mcfunction
execute as @a if score @s help_cd matches 1.. run scoreboard players remove @s help_cd 1
execute as @a if score @s help_cd matches 0 run function TEST:__private__/timer_add/0
> VIRTUAL/data/TEST/functions/__private__/timer_add/0.mcfunction
scoreboard players reset @s help_cd
tellraw @s "Your help command is ready!"
            """)
        )

    def test_RecipeTable(self):
        pack = JMCPack().set_jmc_file("""
Recipe.table({
    "type": "minecraft:crafting_shapeless",
    "ingredients": [
        {
            "item": "minecraft:oak_planks"
        }
    ],
    "result": {
        "item": "minecraft:diamond{test:1b}",
        "count": 5
    }
}, baseItem=barrier, onCraft=()=>{
    tellraw @s "Wow! You crafted a special diamond";
});
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
> VIRTUAL/data/TEST/functions/__private__/recipe_table/0.mcfunction
clear @s minecraft:barrier 1
give @s minecraft:diamond{test:1b} 5
recipe take @s TEST:__private__/recipe_table/0
advancement revoke @s only TEST:__private__/recipe_table/0
tellraw @s "Wow! You crafted a special diamond"
> VIRTUAL/data/TEST/advancements/__private__/recipe_table/0.json
{
  "criteria": {
    "requirement": {
      "trigger": "minecraft:recipe_unlocked",
      "conditions": {
        "recipe": "TEST:__private__/recipe_table/0"
      }
    }
  },
  "rewards": {
    "function": "TEST:__private__/recipe_table/0"
  }
}
> VIRTUAL/data/TEST/recipes/__private__/recipe_table/0.json
{
  "type": "minecraft:crafting_shapeless",
  "ingredients": [
    {
      "item": "minecraft:oak_planks"
    }
  ],
  "result": {
    "item": "minecraft:barrier",
    "count": 1
  }
}
            """)
        )


if __name__ == '__main__':
    unittest.main()
