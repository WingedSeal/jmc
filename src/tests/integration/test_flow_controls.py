import unittest
import sys

sys.path.append('./src')  # noqa

from jmc.test_compile import JMCPack


class TestIfElse(unittest.TestCase):

    def test_if(self):
        pack = JMCPack().set_jmc_file("""
if (condition) {
    say "Hello World";
}
""").build()
        self.assertDictEqual(
            pack.built,
            {"VIRTUAL/data/minecraft/tags/functions/load.json":
             """{
  "values": [
    "TEST:__load__"
  ]
}""",
             "VIRTUAL/data/TEST/functions/__load__.mcfunction":
             """scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
execute if condition run say Hello World"""}
        )


if __name__ == '__main__':
    unittest.main()
