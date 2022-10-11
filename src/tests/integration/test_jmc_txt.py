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


if __name__ == '__main__':
    unittest.main()
