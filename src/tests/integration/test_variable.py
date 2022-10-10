import unittest
import sys


sys.path.append('./src')  # noqa

from tests.utils import string_to_tree_dict
from jmc.test_compile import JMCPack


class TestVariable(unittest.TestCase):
    def test_declaration(self):
        pack = JMCPack().set_jmc_file("""
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
scoreboard objectives add __int__ dummy
scoreboard players add $x __variable__ 0
scoreboard players add $y __variable__ 0
            """)
        )
    def test_assignment(self): ...
    def test_operations(self): ...
    def test_increment(self): ...


if __name__ == '__main__':
    unittest.main()
