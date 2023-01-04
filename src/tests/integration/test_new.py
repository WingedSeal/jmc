import sys  # noqa
sys.path.append("./src")  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.compile.test_compile import JMCTestPack

from jmc.compile.exception import MinecraftSyntaxWarning


class TestNew(unittest.TestCase):
    def test_new(self):
        pack = JMCTestPack().set_jmc_file("""
new advancements(my_datapack.first_join) {
    "criteria": {
        "requirement": {
          "trigger": "minecraft:tick"
        }
    },
    "rewards": {"function": "namespace:mydatapack/rejoin/first_join"}
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
> VIRTUAL/data/TEST/advancements/my_datapack/first_join.json
{
  "criteria": {
    "requirement": {
      "trigger": "minecraft:tick"
    }
  },
  "rewards": {
    "function": "namespace:mydatapack/rejoin/first_join"
  }
}
            """)
        )

    def test_uppercase(self):
        with self.assertRaises(MinecraftSyntaxWarning):
            JMCTestPack().set_jmc_file("""
new advancements(myDatapack.firstJoin) {
    "criteria": {
        "requirement": {
          "trigger": "minecraft:tick"
        }
    },
    "rewards": {"function": "namespace:mydatapack/rejoin/first_join"}
}
            """).build()


if __name__ == "__main__":
    unittest.main()
