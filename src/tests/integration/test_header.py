import sys  # noqa
sys.path.append("./src")  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.compile.test_compile import JMCTestPack

from jmc.compile.exception import HeaderSyntaxException, JMCSyntaxException


class TestHeader(unittest.TestCase):
    def test_define(self):
        pack = JMCTestPack().set_jmc_file("""
TEST_DEFINE "Hello World";
        """).set_header_file("""
#define TEST_DEFINE say
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
say Hello World
            """)
        )

    def test_syntax_error(self):
        with self.assertRaises(HeaderSyntaxException):
            JMCTestPack().set_jmc_file("""

        """).set_header_file("""
Hello World
        """).build()
        with self.assertRaises(HeaderSyntaxException):
            JMCTestPack().set_jmc_file("""

        """).set_header_file("""
#Unknown
        """).build()

    def test_credit(self):
        pack = JMCTestPack().set_jmc_file("""
say "Hello World";
function myFunc() {
    say "My function";
}
        """).set_header_file("""
#credit "JMC by WingedSeal"
#credit
#credit "Made by WingedSeal"
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
> VIRTUAL/data/TEST/functions/myfunc.mcfunction
say My function


# JMC by WingedSeal
#
# Made by WingedSeal
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
say Hello World


# JMC by WingedSeal
#
# Made by WingedSeal
            """)
        )

    def test_command(self):
        with self.assertRaises(JMCSyntaxException):
            JMCTestPack().set_jmc_file("""
test "TEST";
        """).build()
        JMCTestPack().set_jmc_file("""
test "TEST";
        """).set_header_file("""
#command test
        """).build()

    def test_override_minecraft_json(self):
        pack = JMCTestPack().set_jmc_file("""
new tags.functions(minecraft.custom) {
    "values": []
}
        """).set_header_file("""
#override minecraft
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
> VIRTUAL/data/minecraft/tags/functions/custom.json
{
    "values": []
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
            """)
        )

        pack2 = JMCTestPack().set_jmc_file("""
new tags.functions(minecraft.custom) {
    "values": []
}
        """).build()

        self.assertDictEqual(
            pack2 .built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/tags/functions/minecraft/custom.json
{
    "values": []
}
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
            """)
        )

    def test_override_minecraft_mcfunction(self):
        pack = JMCTestPack().set_jmc_file("""
function minecraft.custom() {
    say "custom";
}
        """).set_header_file("""
#override minecraft
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
> VIRTUAL/data/minecraft/functions/custom.mcfunction
say custom
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
            """)
        )

        pack2 = JMCTestPack().set_jmc_file("""
function minecraft.custom() {
  say "custom";
}
        """).build()

        self.assertDictEqual(
            pack2.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/functions/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/functions/minecraft/custom.mcfunction
say custom
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
            """)
        )


if __name__ == "__main__":
    unittest.main()
