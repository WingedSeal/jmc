import sys  # noqa
sys.path.append('./src')  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.test_compile import JMCPack

from jmc.exception import HeaderSyntaxException


class TestJMCtxt(unittest.TestCase):
    def test_load(self):
        pack = JMCPack().set_jmc_file("""
say "Hello World";
        """).set_cert("""
LOAD=load
TICK=__tick__
PRIVATE=__private__
VAR=__variable__
INT=__int__
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
  "values": [
    "TEST:load"
  ]
}
> VIRTUAL/data/TEST/functions/load.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
say Hello World
            """)
        )

    def test_tick(self):
        pack = JMCPack().set_jmc_file("""
function loop() {
    say "Hello World";
}
        """).set_cert("""
LOAD=__load__
TICK=loop
PRIVATE=__private__
VAR=__variable__
INT=__int__
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
    "TEST:loop"
  ]
}
> VIRTUAL/data/TEST/functions/loop.mcfunction
say Hello World
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
            """)
        )

    def test_private(self):
        pack = JMCPack().set_jmc_file("""
execute as @a run {
    say "Hello World 1";
    say "Hello World 2";
}
        """).set_cert("""
LOAD=__load__
TICK=__tick__
PRIVATE=JMC
VAR=__variable__
INT=__int__
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
execute as @a run function TEST:JMC/anonymous/0
> VIRTUAL/data/TEST/functions/JMC/anonymous/0.mcfunction
say Hello World 1
say Hello World 2
            """)
        )

    def test_var(self):
        pack = JMCPack().set_jmc_file("""
$i = 1;
        """).set_cert("""
LOAD=__load__
TICK=__tick__
PRIVATE=__private__
VAR=var
INT=__int__
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
scoreboard objectives add var dummy
scoreboard objectives add __int__ dummy
scoreboard players set $i var 1
            """)
        )

    def test_int(self):
        pack = JMCPack().set_jmc_file("""
$i *= 2;
        """).set_cert("""
LOAD=__load__
TICK=__tick__
PRIVATE=__private__
VAR=__var__
INT=int
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
scoreboard objectives add __var__ dummy
scoreboard objectives add int dummy
scoreboard players set 2 int 2
scoreboard players operation $i __var__ *= 2 int
            """)
        )

    def test_syntax_error(self):
        pack = JMCPack().set_jmc_file("""
say "Hello World";
        """).set_cert("""
LOAD=load
TICK=__tick__
PRIVATE=__private__
VAR=__variable__
INT=__int__=init
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
say Hello World
            """)
        )

    def test_unknown_key(self):
        pack = JMCPack().set_jmc_file("""
say "Hello World";
        """).set_cert("""
LOAD=load
TICK=__tick__
PRIVATE=__private__
VAR=__variable__
INT=__int__
UNKNOWN=__test__
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
  "values": [
    "TEST:load"
  ]
}
> VIRTUAL/data/TEST/functions/load.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
say Hello World
            """)
        )

    def test_missing_key(self):
        pack = JMCPack().set_jmc_file("""
say "Hello World";
        """).set_cert("""
LOAD=load
TICK=__tick__
PRIVATE=__private__
VAR=__variable__
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
  "values": [
    "TEST:load"
  ]
}
> VIRTUAL/data/TEST/functions/load.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
say Hello World
            """)
        )

if __name__ == '__main__':
    unittest.main()
