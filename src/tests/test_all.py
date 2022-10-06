import unittest
from unit import (
    test_lexer,
    test_tokenizer
)
from integration import (
    test_flow_controls
)


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for module in (
        test_lexer,
        test_tokenizer,
        test_flow_controls
    ):
        suite.addTests(loader.loadTestsFromModule(module))
    return suite


unittest.main()
