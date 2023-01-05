import sys  # noqa
sys.path.append("./src")  # noqa
import unittest

import random
from jmc.compile import tokenizer, JMCSyntaxException, JMCSyntaxWarning


class Tokenizer(tokenizer.Tokenizer):
    def __init__(self, raw_string: str) -> None:
        super().__init__(raw_string, '')


class TestTokenizer(unittest.TestCase):
    SAMPLE = [
        "tp",
        "tellraw",
        "keyword",
        "random",
        "kill",
        "execute",
        "function",
        "gamemode",
        "gamerule",
        "give",
        "help",
        "item",
        "kill",
        "list",
    ]

    def test_keyword(self):
        for _ in range(10):
            string = " ".join(
                random.sample(self.SAMPLE,
                              random.randint(
                                  1, len(self.SAMPLE))
                              )) + ";"
            for token in Tokenizer(string).programs[0]:
                self.assertEqual(token.token_type, tokenizer.TokenType.KEYWORD)

    def test_string(self):
        for quote in ['"', "'"]:
            for _ in range(10):
                string = " ".join([f"{quote}{sample}{quote}" for sample in
                                   random.sample(self.SAMPLE,
                                                 random.randint(
                                                     1, len(self.SAMPLE))
                                                 )]) + ";"
                for token in Tokenizer(string).programs[0]:
                    self.assertEqual(token.token_type,
                                     tokenizer.TokenType.STRING)

    def test_diff_quote_type(self):
        with self.assertRaises(JMCSyntaxException):
            Tokenizer("'string\";")

    def test_missing_semicolon(self):
        with self.assertRaises(JMCSyntaxException):
            Tokenizer("keyword without semicolon")

    def test_paren(self):
        with self.assertRaises(JMCSyntaxException):
            Tokenizer("{{};")
        with self.assertRaises(JMCSyntaxException):
            Tokenizer("{}{}};")
        Tokenizer("{'}'};")

        self.assertListEqual(
            [token.string for token in Tokenizer(
                "HELLO [TEST TEST] WORLD;").programs[0]],
            [
                "HELLO",
                "[TEST TEST]",
                "WORLD"
            ]
        )

    def test_curly_append_keywords(self):
        self.assertListEqual(
            [token.string for token in Tokenizer(
                "HELLO {} WORLD;").programs[0]],
            [
                "HELLO", "{}", "WORLD"
            ]
        )
        self.assertListEqual(
            [token.string for token in Tokenizer(
                "if {} WORLD;").programs[0]],
            [
                "if", "{}"
            ]
        )

    def test_unncessary_semicolon(self):
        with self.assertRaises(JMCSyntaxWarning):
            Tokenizer("keyword;;")
        with self.assertRaises(JMCSyntaxWarning):
            Tokenizer("{};;")

    def test_newline(self):
        self.assertEqual(Tokenizer(
            "{A\nB};").programs[0][0].string,
            "{A\nB}")

        self.assertListEqual(
            [token.string for token in Tokenizer(
                "HELLO\nWORLD;").programs[0]],
            [
                "HELLO",
                "WORLD"
            ]
        )

        with self.assertRaises(JMCSyntaxException):
            Tokenizer('"HELLO\nWORLD;"')


if __name__ == "__main__":
    unittest.main()
