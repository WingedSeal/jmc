import unittest
import sys


sys.path.append('./src')  # noqa

from jmc.exception import HeaderSyntaxException
from tests.utils import string_to_tree_dict
from jmc.test_compile import JMCPack


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


if __name__ == '__main__':
    unittest.main()
