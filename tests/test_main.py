import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from main import run


class TestMain(unittest.TestCase):
    @patch("builtins.input", side_effect=["Board:", "xK .", "Commands:", EOFError()])
    def test_run_prints_unknown_token_error(self, _mock_input):
        output = io.StringIO()
        with redirect_stdout(output):
            run()
        self.assertEqual(output.getvalue(), "ERROR UNKNOWN_TOKEN\n")

    @patch(
        "builtins.input",
        side_effect=[
            "Board:",
            ". .",
            ". wP",
            "Commands:",
            "click 100 100",
            "click 100 0",
            "wait 1000",
            "print board",
            EOFError(),
        ],
    )
    def test_run_executes_commands(self, _mock_input):
        output = io.StringIO()
        with redirect_stdout(output):
            run()
        self.assertEqual(output.getvalue(), ". wQ\n. .\n")


if __name__ == "__main__":
    unittest.main()
