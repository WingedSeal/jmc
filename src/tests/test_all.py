import unittest
import unit
import integration


def load_tests(loader: unittest.loader.TestLoader, tests: unittest.loader.TestLoader, pattern: None) -> unittest.suite.TestSuite:
    suite = unittest.TestSuite()
    for module in unit.ALL + integration.ALL:
        suite.addTests(loader.loadTestsFromModule(module))
    return suite


unittest.main()
