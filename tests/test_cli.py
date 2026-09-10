import pytest
from unittest.mock import patch
from io import StringIO
import sys


class TestGenerateCommand:
    @patch("cli.generate_emails")
    @patch("sys.stdout", new_callable=StringIO)
    def test_generate_command_success(self, mock_stdout, mock_generate_emails):
        mock_generate_emails.return_value = ["test@gmail.com"]
        with patch("sys.argv", ["cli.py", "generate", "--count", "1"]):
            from cli import main
            main()
        output = mock_stdout.getvalue()
        assert "Se generaron 1 correos" in output
