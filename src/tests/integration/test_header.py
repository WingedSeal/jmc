import sys  # noqa
sys.path.append('./src')  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.test_compile import JMCPack

from jmc.exception import HeaderSyntaxException


class TestHeader(unittest.TestCase):
    def test_define(self):
        pack = JMCPack().set_jmc_file("""
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
scoreboard objectives add __int__ dummy
say Hello World
            """)
        )

    def test_syntax_error(self):
        with self.assertRaises(HeaderSyntaxException):
            JMCPack().set_jmc_file("""

        """).set_header_file("""
Hello World
        """).build()
        with self.assertRaises(HeaderSyntaxException):
            JMCPack().set_jmc_file("""

        """).set_header_file("""
#Unknown
        """).build()

    def test_credit(self):
        pack = JMCPack().set_jmc_file("""
say "Hello World";
function myFunc() {
    say "My function";
}
        """).set_header_file("""
#credit JMC by WingedSeal
#credit
#credit Made by WingedSeal
        """).build()

        self.maxDiff = None
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
scoreboard objectives add __int__ dummy
say Hello World


# JMC by WingedSeal
#
# Made by WingedSeal
            """)
        )


if __name__ == '__main__':
    unittest.main()
