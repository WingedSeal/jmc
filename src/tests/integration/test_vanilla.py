import sys

from jmc.compile.exception import MinecraftVersionTooLow  # noqa

sys.path.append("./src")  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.compile.test_compile import JMCTestPack


class TestVanilla(unittest.TestCase):

    def test_brackets(self):
        pack = (
            JMCTestPack()
            .set_jmc_file(
                """
give @s carrot_on_a_stick[tag=my_tag];
give @s carrot_on_a_stick[tag =my_tag];
give @s carrot_on_a_stick[tag = my_tag];
give @s carrot_on_a_stick [tag=my_tag];
give @s stone[custom_data={key:"value"}];
give @s stone[custom_data={key : "value"}];
        """
            )
            .set_pack_format(57)
            .build()
        )

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict(
                """
> VIRTUAL/data/minecraft/tags/function/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/function/__load__.mcfunction
scoreboard objectives add __variable__ dummy
give @s carrot_on_a_stick[tag=my_tag]
give @s carrot_on_a_stick[tag=my_tag]
give @s carrot_on_a_stick[tag=my_tag]
give @s carrot_on_a_stick [tag=my_tag]
give @s stone[custom_data={key:"value"}]
give @s stone[custom_data={key:"value"}]
            """
            ),
        )

    def test_vanilla_macro_list(self):
        pack = (
            JMCTestPack()
            .set_jmc_file(
                """
execute run {
    $tp @s $(0) $(1) $(2);
} with [$x, $y, $z];
        """
            )
            .set_pack_format(57)
            .build()
        )

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict(
                """
> VIRTUAL/data/minecraft/tags/function/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/function/__load__.mcfunction
scoreboard objectives add __variable__ dummy
execute store result storage TEST:__private__ global.0 int 1 run scoreboard players get $x __variable__
execute store result storage TEST:__private__ global.1 int 1 run scoreboard players get $y __variable__
execute store result storage TEST:__private__ global.2 int 1 run scoreboard players get $z __variable__
function TEST:__private__/anonymous/0 with storage TEST:__private__ global
> VIRTUAL/data/TEST/function/__private__/anonymous/0.mcfunction
$tp @s $(0) $(1) $(2)
            """
            ),
        )

    def test_vanilla_macro(self):
        pack = (
            JMCTestPack()
            .set_jmc_file(
                """
function myFunc() {
    $ say "$(name)";
}
myFunc() with {"name": "WingedSeal"};
myFunc({"name": "WingedSeal"});
myFunc(name="WingedSeal");
myFunc() with storage::path;
myFunc() with @s[tag=myTag]::;
myFunc() with [~, ~, ~]::path;
        """
            )
            .set_pack_format(57)
            .build()
        )

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict(
                """
> VIRTUAL/data/minecraft/tags/function/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/function/__load__.mcfunction
scoreboard objectives add __variable__ dummy
function TEST:myfunc with {"name":"WingedSeal"}
function TEST:myfunc {"name":"WingedSeal"}
function TEST:myfunc {"name":"WingedSeal"}
function TEST:myfunc with storage TEST:storage path
function TEST:myfunc with entity @s[tag=myTag]
function TEST:myfunc with block ~ ~ ~ path
> VIRTUAL/data/TEST/function/myfunc.mcfunction
$say $(name)
            """
            ),
        )

    def test_vanilla_macro_version_too_low(self):
        with self.assertRaises(MinecraftVersionTooLow):
            JMCTestPack().set_jmc_file(
                """
function myFunc() {}
myFunc() with [$a];
        """
            ).set_pack_format(32).build()


if __name__ == "__main__":
    unittest.main()
