import unittest
from tests import (
    tokenizer_test,
    lexer_test
)


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for module in (
        tokenizer_test,
        lexer_test
    ):
        suite.addTests(loader.loadTestsFromModule(module))
    return suite


unittest.main()
