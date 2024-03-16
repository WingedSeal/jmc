import sys  # noqa
sys.path.append("./src")  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.compile.test_compile import JMCTestPack

from jmc.compile.exception import JMCSyntaxException


class TestNBT(unittest.TestCase):
    maxDiff = None

    def test_operation(self):
        pack = JMCTestPack().set_jmc_file("""
my_storage::my.path;
my_storage::my.path * 2;
my_storage::my.path = "Hello World";
my_storage::my.path = my_storage::other.path;
my_storage::my.path = my_storage::other.path[2:];
my_storage::my.path = my_storage::other.path[2:10];
my_storage::my.path >> "Hello World";
my_storage::my.path << "Hello World";
my_storage::my.path ^2 "Hello World";
my_storage::my.path ?= $my_var;
my_storage::my.path = $my_var;
my_storage::my.path = (float) $my_var;
my_storage::my.path = 2 * (float) $my_var;
my_storage::my.path += {key: "value"};
my_storage:: += {key: "value"};
my_storage::my.path.del();
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
data get storage TEST:my_storage my.path
data get storage TEST:my_storage my.path 2
data modify storage TEST:my_storage my.path set value 'Hello World'
data modify storage TEST:my_storage my.path set from storage TEST:my_storage other.path
data modify storage TEST:my_storage my.path set string storage TEST:my_storage other.path 2
data modify storage TEST:my_storage my.path set string storage TEST:my_storage other.path 2 10
data modify storage TEST:my_storage my.path prepend value 'Hello World'
data modify storage TEST:my_storage my.path append value 'Hello World'
data modify storage TEST:my_storage my.path insert 2 value 'Hello World'
execute store success storage TEST:my_storage my.path int 1 run scoreboard players get $my_var __variable__
execute store result storage TEST:my_storage my.path int 1 run scoreboard players get $my_var __variable__
execute store result storage TEST:my_storage my.path float 1 run scoreboard players get $my_var __variable__
execute store result storage TEST:my_storage my.path float 2 run scoreboard players get $my_var __variable__
data modify storage TEST:my_storage my.path merge value {key:"value"}
data merge storage TEST:my_storage {key:"value"}
data remove storage TEST:my_storage my.path
            """)
        )

    def test_path(self):
        pack = JMCTestPack().set_jmc_file("""
my_namespace:my_storage::my.path;
my_storage::my.path;
my_storage::;
::my.path;
[0,0,0]::my.path;
@a::my.path;
@a[tag=test]::my.path;
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
data get storage my_namespace:my_storage my.path
data get storage TEST:my_storage my.path
data get storage TEST:my_storage
data get storage TEST:TEST my.path
data get block 0 0 0 my.path
data get entity @a my.path
data get entity @a[tag=test] my.path
            """)
        )

    def test_interaction(self):
        pack = JMCTestPack().set_jmc_file("""
$var = storage::path[-1].int;
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
execute store result score $var __variable__ run data get storage TEST:storage path[-1].int
            """)
        )


if __name__ == "__main__":
    unittest.main()
