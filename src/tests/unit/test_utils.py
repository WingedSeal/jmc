import sys  # noqa
sys.path.append('./src')  # noqa
import unittest

from tests.utils import string_to_tree_dict
from jmc.compile.datapack import DataPack
from jmc.compile.utils import SingleTon, is_connected, is_number, search_to_string
from jmc.compile.command.utils import ArgType, PlayerType, eval_expr, find_arg_type, find_scoreboard_player_type
from jmc.compile.tokenizer import Token, TokenType, Tokenizer

EMPTY_TOKENIZER = Tokenizer("", "")


class SingleTonClass(SingleTon):
    pass


class TestSingleTon(unittest.TestCase):
    def test_id(self):
        item1 = SingleTonClass()
        item2 = SingleTonClass()
        self.assertEqual(id(item1), id(item2))

    def test_instantiation(self):
        with self.assertRaises(TypeError):
            SingleTon()


class TestJMCutils(unittest.TestCase):
    def test_is_number(self):
        self.assertFalse(is_number("NAN"))
        self.assertTrue(is_number("0"))

    def test_is_connected(self):
        token1 = Token(TokenType.KEYWORD, line=1, col=0, string="ABC")
        token2 = Token(TokenType.KEYWORD, line=1, col=3, string="DEF")
        token3 = Token(TokenType.KEYWORD, line=1, col=6, string="GHI")
        self.assertTrue(is_connected(token2, token1))
        self.assertTrue(is_connected(token3, token2))
        self.assertFalse(is_connected(token3, token1))
        self.assertFalse(is_connected(token1, token2))
        self.assertFalse(is_connected(token2, token3))

    def test_search_to_string(self):
        new_str, found = search_to_string("$TEST.toString", Token(
            TokenType.PAREN_ROUND, line=-1, col=-1, string="()"), "VAR_NAME", EMPTY_TOKENIZER)
        self.assertTrue(found)
        self.assertEqual(
            new_str, '{"score": {"name": "$TEST", "objective": "VAR_NAME"}}')
        new_str, found = search_to_string("$TEST.toString", Token(
            TokenType.PAREN_ROUND, line=-1, col=-1, string='(color=red)'), "VAR_NAME", EMPTY_TOKENIZER)
        self.assertTrue(found)
        self.assertEqual(
            new_str, '{"color": "red", "score": {"name": "$TEST", "objective": "VAR_NAME"}}')

        with self.assertRaises(Exception):
            search_to_string("$TEST.toString", Token(
                TokenType.PAREN_ROUND, line=-1, col=-1, string='(color="red")'), "VAR_NAME", EMPTY_TOKENIZER)


class TestCommandUtils(unittest.TestCase):

    def test_find_scoreboard_player_type(self):
        scoreboard_player = find_scoreboard_player_type(
            Token.empty("10"), EMPTY_TOKENIZER)
        self.assertEqual(scoreboard_player.player_type, PlayerType.INTEGER)
        self.assertEqual(scoreboard_player.value, 10)

        scoreboard_player = find_scoreboard_player_type(
            Token.empty("$jmc_var"), EMPTY_TOKENIZER)
        self.assertEqual(scoreboard_player.player_type, PlayerType.VARIABLE)
        self.assertEqual(scoreboard_player.value,
                         (DataPack.var_name, "$jmc_var"))

        scoreboard_player = find_scoreboard_player_type(
            Token.empty("OBJ:SELECTOR"), EMPTY_TOKENIZER)
        self.assertEqual(scoreboard_player.player_type, PlayerType.SCOREBOARD)
        self.assertEqual(scoreboard_player.value,
                         ("OBJ", "SELECTOR"))

    def test_find_arg_type(self):
        self.assertEqual(find_arg_type(
            Token.empty("5"), EMPTY_TOKENIZER), ArgType.INTEGER)
        self.assertEqual(find_arg_type(
            Token.empty("@a"), EMPTY_TOKENIZER), ArgType.SELECTOR)

    def test_eval_expr(self):
        self.assertEqual(eval_expr("10+10"), "20")
        self.assertEqual(eval_expr("5**2"), "25")
        self.assertEqual(eval_expr("17*(10-9)"), "17")


class TestTestUtils(unittest.TestCase):
    def test_string_to_tree_dict(self):
        self.assertDictEqual(string_to_tree_dict("""
> FILE_NAME_1
FILE_CONTENT_1_1
FILE_CONTENT_1_2
> FILE_NAME_2
FILE_CONTENT_2_1
FILE_CONTENT_2_2
        """),
                             {"FILE_NAME_1": "FILE_CONTENT_1_1\nFILE_CONTENT_1_2",
                              "FILE_NAME_2": "FILE_CONTENT_2_1\nFILE_CONTENT_2_2"})
        self.assertDictEqual(string_to_tree_dict("""
> FILE_NAME_1
FILE_CONTENT_1_1
FILE_CONTENT_1_2
        """),
                             {"FILE_NAME_1": "FILE_CONTENT_1_1\nFILE_CONTENT_1_2"})
        with self.assertRaises(ValueError):
            string_to_tree_dict("""TEST""")

        with self.assertRaises(ValueError):
            string_to_tree_dict("""
> FILE_NAME_1
        """)
        with self.assertRaises(ValueError):
            string_to_tree_dict("""
FILE_CONTENT_1_1
        """)


if __name__ == '__main__':
    unittest.main()
