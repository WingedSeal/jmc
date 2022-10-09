import unittest
import sys


sys.path.append('./src')  # noqa

from tests.utils import string_to_tree_dict
from jmc.test_compile import JMCPack


class TestNew(unittest.TestCase):
    def test_new(self): ...
