import unittest
from unit import (
    test_utils,
    test_tokenizer
)
from integration import (
    test_flow_controls
)


def load_tests(loader: unittest.loader.TestLoader, tests: unittest.loader.TestLoader, pattern: None) -> unittest.suite.TestSuite:
    suite = unittest.TestSuite()
    for module in (
        test_utils,
        test_tokenizer,
        test_flow_controls
    ):
        suite.addTests(loader.loadTestsFromModule(module))
    return suite


unittest.main()
