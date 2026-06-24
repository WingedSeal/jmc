import sys  # noqa

sys.path.append("./src")  # noqa
import io  # noqa
import unittest  # noqa

from jmc.compile.hooks import emit_message, register_message
from jmc.terminal.utils import Colors, eprint, pprint


class TestHooks(unittest.TestCase):
    def test_default_handler_is_print(self):
        from jmc.compile import hooks
        self.assertIs(hooks._message_handler, print)

    def test_register_replaces_handler(self):
        received: list[str] = []
        register_message(received.append)
        emit_message("hello")
        self.assertEqual(received, ["hello"])

    def test_emit_calls_through_handler(self):
        received: list[str] = []
        register_message(received.append)
        emit_message("one")
        emit_message("two")
        self.assertEqual(received, ["one", "two"])

    def tearDown(self):
        register_message(print)


class TestPprint(unittest.TestCase):
    def test_no_colors_on_non_tty(self):
        buf = io.StringIO()
        pprint("hello", Colors.INFO, file=buf)
        self.assertEqual(buf.getvalue(), "hello\n")

    def test_colors_on_tty(self):
        buf = io.StringIO()
        buf.isatty = lambda: True
        pprint("hello", Colors.INFO, file=buf)
        self.assertIn(Colors.INFO.value, buf.getvalue())
        self.assertIn(Colors.ENDC.value, buf.getvalue())


class TestEprint(unittest.TestCase):
    def test_writes_to_stderr(self):
        stderr_buf = io.StringIO()
        stdout_buf = io.StringIO()
        old_stderr, old_stdout = sys.stderr, sys.stdout
        sys.stderr, sys.stdout = stderr_buf, stdout_buf
        try:
            eprint("error message")
        finally:
            sys.stderr, sys.stdout = old_stderr, old_stdout
        self.assertIn("error message", stderr_buf.getvalue())
        self.assertEqual(stdout_buf.getvalue(), "")
