import os
import unittest
from unittest.mock import patch

from check_semantic_version import cli


TEST_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIRECTORY = os.path.join(TEST_DIRECTORY, "test_package")


class TestCLI(unittest.TestCase):
    def test_cli_with_matching_versions(self):
        """Test that the correct message and error message are returned if the current version and the expected version
        are the same.
        """
        with patch(
            "check_semantic_version.check_semantic_version._get_expected_semantic_version",
            return_value="0.3.9",
        ):
            with patch("check_semantic_version.check_semantic_version._get_current_version", return_value="0.3.9"):
                with patch("sys.stdout") as mock_stdout:
                    with self.assertRaises(SystemExit) as e:
                        cli.main(["setup.py"])

                    # Check that the exit code is 0.
                    self.assertEqual(e.exception.code, 0)

                    message = mock_stdout.method_calls[0].args[0]
                    self.assertIn("VERSION PASSED CHECKS:", message)
                    self.assertIn("The current version is the same as the expected semantic version: 0.3.9.", message)

    def test_cli_with_non_matching_versions(self):
        """Test that the correct message and error message are returned if the current version and the expected version
        are not the same.
        """
        with patch(
            "check_semantic_version.check_semantic_version._get_expected_semantic_version",
            return_value="0.5.3",
        ):
            with patch("check_semantic_version.check_semantic_version._get_current_version", return_value="0.3.9"):
                with patch("sys.stdout") as mock_stdout:
                    with self.assertRaises(SystemExit) as e:
                        cli.main(["setup.py"])

                    # Check that the exit code is 1.
                    self.assertEqual(e.exception.code, 1)

                    message = mock_stdout.method_calls[0].args[0]
                    self.assertIn("VERSION FAILED CHECKS:", message)
                    self.assertIn(
                        "The current version (0.3.9) is different from the expected semantic version (0.5.3).",
                        message,
                    )

    def test_cli_with_non_matching_versions_reversed(self):
        """Test that the correct message and error message are returned if the current version and the expected version
        are not the same (reversed compared to the previous test).
        """
        with patch(
            "check_semantic_version.check_semantic_version._get_expected_semantic_version",
            return_value="0.3.9",
        ):
            with patch("check_semantic_version.check_semantic_version._get_current_version", return_value="0.5.3"):
                with patch("sys.stdout") as mock_stdout:
                    with self.assertRaises(SystemExit) as e:
                        cli.main(["setup.py"])

                    # Check that the exit code is 1.
                    self.assertEqual(e.exception.code, 1)

                    message = mock_stdout.method_calls[0].args[0]
                    self.assertIn("VERSION FAILED CHECKS:", message)
                    self.assertIn(
                        "The current version (0.5.3) is different from the expected semantic version (0.3.9).",
                        message,
                    )
