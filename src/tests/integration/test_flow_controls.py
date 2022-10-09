import unittest
import sys


sys.path.append('./src')  # noqa

from tests.utils import string_to_tree_dict
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
execute if condition run say Hello World
            """)
        )

    def test_if_else(self):
        pack = JMCPack().set_jmc_file("""
if (condition) {
    say "TRUE";
} else {
    say "FALSE";
}
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
scoreboard players set __if_else__ __variable__ 0
execute if condition run function TEST:__private__/if_else/0
execute if score __if_else__ __variable__ matches 0 run function TEST:__private__/__if_else__/1
> VIRTUAL/data/TEST/functions/__private__/if_else/0.mcfunction
say TRUE
scoreboard players set __if_else__ __variable__ 1
> VIRTUAL/data/TEST/functions/__private__/if_else/1.mcfunction
say FALSE
            """)
        )

    def test_if_elif(self):
        pack = JMCPack().set_jmc_file("""
if (condition) {
    say "CONDITION1";
} else if (condition2) {
    say "CONDITION2";
}
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
scoreboard players set __if_else__ __variable__ 0
execute if condition run function TEST:__private__/if_else/0
execute if score __if_else__ __variable__ matches 0 run function TEST:__private__/__if_else__/1
> VIRTUAL/data/TEST/functions/__private__/if_else/0.mcfunction
say CONDITION1
scoreboard players set __if_else__ __variable__ 1
> VIRTUAL/data/TEST/functions/__private__/if_else/1.mcfunction
execute if condition2 run function TEST:__private__/__if_else__/2
> VIRTUAL/data/TEST/functions/__private__/if_else/2.mcfunction
say CONDITION2
scoreboard players set __if_else__ __variable__ 1
            """)
        )


if __name__ == '__main__':
    unittest.main()
