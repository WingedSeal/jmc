import sys  # noqa
sys.path.append("./src")  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.compile.test_compile import JMCTestPack

from jmc.compile.exception import JMCSyntaxException


class TestVariable(unittest.TestCase):
    def test_declaration(self):
        pack = JMCTestPack().set_jmc_file("""
$x += 0;
$y += 0;
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
scoreboard players add $x __variable__ 0
scoreboard players add $y __variable__ 0
            """)
        )

    def test_no_op_error(self):
        with self.assertRaises(JMCSyntaxException):
            JMCTestPack().set_jmc_file("""
$x;
        """).build()

    def test_assignment(self):
        pack = JMCTestPack().set_jmc_file("""
$x = obj:var1;
$y = 1;
$z = $x;
$z -> obj:var2;
$z->obj:var3;
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
scoreboard players operation $x __variable__ = var1 obj
scoreboard players set $y __variable__ 1
scoreboard players operation $z __variable__ = $x __variable__
scoreboard players operation var2 obj = $z __variable__
scoreboard players operation var3 obj = $z __variable__
            """)
        )

    def test_operations(self):
        pack = JMCTestPack().set_jmc_file("""
$x += 1;
$x *= 2;
$x /= 3;
$x += obj:var;
$x -= $y;
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
scoreboard players set 3 __int__ 3
scoreboard players add $x __variable__ 1
scoreboard players operation $x __variable__ *= 2 __int__
scoreboard players operation $x __variable__ /= 3 __int__
scoreboard players operation $x __variable__ += var obj
scoreboard players operation $x __variable__ -= $y __variable__
            """)
        )

    def test_increment(self):
        pack = JMCTestPack().set_jmc_file("""
$x ++;
$x++;
$x--;
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
scoreboard players add $x __variable__ 1
scoreboard players add $x __variable__ 1
scoreboard players remove $x __variable__ 1
            """)
        )

    def test_get(self):
        pack = JMCTestPack().set_jmc_file("""
execute store result score @s obj run $x.get();
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
execute store result score @s obj run scoreboard players get $x __variable__
            """)
        )

        with self.assertRaises(JMCSyntaxException):
            JMCTestPack().set_jmc_file("""
$x.get(key=value);
        """).build()

    def test_store_result(self):
        pack = JMCTestPack().set_jmc_file("""
$currentAmmo = data get entity @s SelectedItem.tag.ammo;
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
execute store result score $currentAmmo __variable__ run data get entity @s SelectedItem.tag.ammo
            """)
        )

    def test_store_success(self):
        pack = JMCTestPack().set_jmc_file("""
$currentAmmo ?= data get entity @s SelectedItem.tag.ammo;
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
execute store success score $currentAmmo __variable__ run data get entity @s SelectedItem.tag.ammo
            """)
        )


if __name__ == "__main__":
    unittest.main()
