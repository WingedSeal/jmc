import sys  # noqa
sys.path.append('./src')  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.compile.test_compile import JMCPack

from jmc.compile.exception import JMCSyntaxException


class TestUnmatched(unittest.TestCase):
    def test_bracket_no_close(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
    execute as @a run {say "Hello World";
            """).build()

    def test_bracket_no_open(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
    execute as @a run say "Hello World"};
            """).build()

    def test_bracket_more_open(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
    execute as @a run {
        execute as @a run {
        say "Hello World";
    }
            """).build()

    def test_bracket_more_close(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
    execute as @a run {
        execute as @a run {
        say "Hello World";
    }
}
}
            """).build()

    def test_quote_no_end(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
say "Hello World;
            """).build()


class TestQuote(unittest.TestCase):
    def test_newline_in_quote(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
say "Hello World
";
            """).build()


class TestSemicolon(unittest.TestCase):
    def test_missing_semicolon(self):
        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
say "Hello World";
say "Hello World"
            """).build()

        with self.assertRaises(JMCSyntaxException):
            JMCPack().set_jmc_file("""
say "Hello World"
say "Hello World";
            """).build()

    def test_first_arg_exception(self):
        JMCPack().set_jmc_file("""
scoreboard objectives add my_obj trigger;
            """).build()

        JMCPack().set_jmc_file("""
execute as @p run effect give @s speed;
            """).build()


if __name__ == '__main__':
    unittest.main()
