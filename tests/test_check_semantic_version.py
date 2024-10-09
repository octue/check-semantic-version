import logging
import os
import unittest
from unittest.mock import patch

from check_semantic_version import check_semantic_version

TEST_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIRECTORY = os.path.join(TEST_DIRECTORY, "test_package")


class MockCompletedProcess:
    """A mock of subprocess.CompletedProcess.

    :param bytes stdout:
    :return None:
    """

    def __init__(self, stdout):
        self.stdout = stdout


class TestGetCurrentVersion(unittest.TestCase):
    def test_error_raised_if_unsupported_version_source_provided(self):
        """Ensure an error is raised if an unsupported version source is provided."""
        with self.assertRaises(ValueError):
            check_semantic_version._get_current_version(path="blah", version_source_type="blah")

    def test_get_current_version_for_setup_py(self):
        """Test that the current version can be extracted from a `setup.py` file."""
        path = os.path.join(TEST_DATA_DIRECTORY, "setup.py")
        version = check_semantic_version._get_current_version(path, version_source_type="setup.py")
        self.assertEqual(version, "0.3.4")

    def test_get_current_version_for_pyproject_toml(self):
        """Test that the current version can be extracted from a `pyproject.toml` file."""
        path = os.path.join(TEST_DATA_DIRECTORY, "pyproject.toml")
        version = check_semantic_version._get_current_version(path, version_source_type="pyproject.toml")
        self.assertEqual(version, "0.6.3")

    def test_get_current_version_with_custom_file_path_for_pyproject_toml(self):
        """Test that the current version can be extracted from a different file than the top-level file pyproject.toml."""
        version = check_semantic_version._get_current_version(
            path=os.path.join(TEST_DATA_DIRECTORY, "pyproject.toml"),
            version_source_type="pyproject.toml",
        )

        self.assertEqual(version, "0.6.3")

    def test_get_current_version_for_package_json(self):
        """Test that the current version can be extracted from a top-level `package.json` file."""
        path = os.path.join(TEST_DATA_DIRECTORY, "package.json")
        version = check_semantic_version._get_current_version(path, version_source_type="package.json")
        self.assertEqual(version, "1.5.3")


class TestGetExpectedSemanticVersion(unittest.TestCase):
    def test_get_expected_semantic_version(self):
        """Test that the expected semantic version can be parsed from a successful `git-mkver` command."""
        with patch("subprocess.run", return_value=MockCompletedProcess(stdout=b"0.3.9")):
            version = check_semantic_version._get_expected_semantic_version(
                version_source_type="setup.py",
                breaking_change_indicated_by="minor",
            )
            self.assertEqual(version, "0.3.9")

    def test_mkver_conf_file_generated_if_not_present_in_current_working_directory(self):
        """Test that a `mkver.conf` file is generated if one is not already present in the current working directory."""
        original_working_directory = os.getcwd()

        try:
            os.chdir(TEST_DATA_DIRECTORY)

            with self.assertLogs(level=logging.WARNING) as logging_context:
                with patch("subprocess.run", return_value=MockCompletedProcess(stdout=b"0.3.9")):
                    check_semantic_version._get_expected_semantic_version(
                        "setup.py",
                        breaking_change_indicated_by="minor",
                    )

        finally:
            os.chdir(original_working_directory)

        self.assertEqual(logging_context.records[0].message, "No `mkver.conf` file found. Generating one instead.")
