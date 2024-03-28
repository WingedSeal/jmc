import unittest
import unit
import integration


def load_tests(
    loader: unittest.loader.TestLoader, tests: unittest.loader.TestLoader, pattern: None
) -> unittest.suite.TestSuite:
    suite = unittest.TestSuite()
    for module in unit.ALL + integration.ALL:
        suite.addTests(loader.loadTestsFromModule(module))
    return suite


def test_all():
    unittest.main()


if __name__ == "__main__":
    test_all()
