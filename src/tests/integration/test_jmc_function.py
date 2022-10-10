import sys  # noqa
sys.path.append('./src')  # noqa

import unittest
from tests.utils import string_to_tree_dict
from jmc.test_compile import JMCPack


class TestVarOperation(unittest.TestCase):
    ...


class TestBoolFunction(unittest.TestCase):
    ...


class TestExecuteExcluded(unittest.TestCase):
    ...


class TestJMCCommand(unittest.TestCase):
    ...


class TestLoadOnce(unittest.TestCase):
    ...


class TestLoadOnly(unittest.TestCase):
    ...


if __name__ == '__main__':
    unittest.main()
