import sys

sys.path.append("./src")  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.compile.test_compile import JMCTestPack


class TestJMCMacro(unittest.TestCase):
    maxDiff = None

    def test_define(self):
        pack = JMCTestPack().set_header_file("""
#define TOKEN1 1
#define TOKEN2 2
#define TOKEN3 3
        """).set_pack_format(57).set_jmc_file("""
tp @s TOKEN1 TOKEN2 TOKEN3;
        """).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/function/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/function/__load__.mcfunction
scoreboard objectives add __variable__ dummy
tp @s 1 2 3
            """)
        )

    def test_deepdefine(self):
        pack = JMCTestPack().set_header_file("""
#bind EVAL
#define TOKEN1(x) TEST(x)
#deepdefine TOKEN2(x) TEST(x)
#deepdefine TOKEN3(x) EVAL(x + 1)
#deepdefine MY_TOKEN(x) carrot_on_a_stick[tag=x]
        """).set_jmc_file("""
tp @s TOKEN1(test);
tp @s TOKEN2(test);
tp @s TOKEN3(10);
give @s MY_TOKEN(myTag);
        """).set_pack_format(57).build()

        self.assertDictEqual(
            pack.built,
            string_to_tree_dict("""
> VIRTUAL/data/minecraft/tags/function/load.json
{
    "values": [
        "TEST:__load__"
    ]
}
> VIRTUAL/data/TEST/function/__load__.mcfunction
scoreboard objectives add __variable__ dummy
tp @s TEST(x)
tp @s TEST(test)
tp @s 11
give @s carrot_on_a_stick[tag=myTag]
            """)
        )


if __name__ == "__main__":
    unittest.main()
