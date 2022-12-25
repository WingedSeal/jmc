import sys  # noqa
sys.path.append("./src")  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.compile.test_compile import JMCPack

from jmc.compile.exception import JMCFileNotFoundError, JMCSyntaxException


class TestFunction(unittest.TestCase):
    def test_define(self):
        pack = JMCPack().set_jmc_file("""
function customFunction() {
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
> VIRTUAL/data/TEST/functions/customfunction.mcfunction
say Hello World
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
            """)
        )

    def test_param_error(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
function customFunction(parameter) {
    say "Hello World";
}
        """).build()

        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
customFunction(argument);
        """).build()

    def test_call(self):
        pack = JMCPack().set_jmc_file("""
customFunction();
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
function TEST:customfunction
            """)
        )

    def test_anonymous(self):
        pack = JMCPack().set_jmc_file("""
execute as @a run {
    say "Hello World 1";
    say "Hello World 2";
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
execute as @a run function TEST:__private__/anonymous/0
> VIRTUAL/data/TEST/functions/__private__/anonymous/0.mcfunction
say Hello World 1
say Hello World 2
            """)
        )

    def test_class(self):
        pack = JMCPack().set_jmc_file("""
class foo {
    function bar() {//COMMENT_TEST
        say "bar"; //COMMENT_TEST
    }
    new advancements(bar) {
        "criteria": {
            "requirement": {
            "trigger": "minecraft:tick"
            }
        }
    }
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
> VIRTUAL/data/TEST/functions/foo/bar.mcfunction
say bar
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
> VIRTUAL/data/TEST/advancements/foo/bar.json
{
  "criteria": {
    "requirement": {
      "trigger": "minecraft:tick"
    }
  }
}
            """)
        )

    def test_json_empty_error(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
new advancements(foo) {
}
            """).build()
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
new advancements(foo) {}
            """).build()


class TestFeatures(unittest.TestCase):
    def test_import_error(self):
        with self.assertRaises(JMCFileNotFoundError):
            JMCPack().set_jmc_file("""
@import "foo";
            """).build()
        with self.assertRaises(JMCFileNotFoundError):
            JMCPack().set_jmc_file("""
@import "foo.jmc";
            """).build()
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
@import;
            """).build()
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
@import foo;
            """).build()

    def test_comment(self):
        pack = JMCPack().set_jmc_file("""
say "Hello World 1";
# This is comment
// This is jmc comment
say "Hello World 2"; // This is also a jmc comment
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
say Hello World 1
say Hello World 2
            """)
        )

    def test_tick(self):
        pack = JMCPack().set_jmc_file("""
function __tick__() {
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
> VIRTUAL/data/minecraft/tags/functions/tick.json
{
  "values": [
    "TEST:__tick__"
  ]
}
> VIRTUAL/data/TEST/functions/__tick__.mcfunction
say Hello World
> VIRTUAL/data/TEST/functions/__load__.mcfunction
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
            """)
        )

    def test_load_define_error(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
function __load__() {
    say "Hello World";
}
            """).build()


if __name__ == "__main__":
    unittest.main()
