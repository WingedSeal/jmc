import unittest
import sys


sys.path.append('./src')  # noqa

from tests.utils import string_to_tree_dict
from jmc.test_compile import JMCPack


class TestVariable(unittest.TestCase):
    def test_declaration(self): ...
    def test_assignment(self): ...
    def test_operations(self): ...
    def test_increment(self): ...
