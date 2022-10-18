import json
import tempfile
from unittest import TestCase

from pyhocon import ConfigFactory, HOCONConverter

from check_semantic_version.configuration import Configuration


class TestConfiguration(TestCase):
    def test_generate_with_setup_py_version_source(self):
        """Test generating a configuration for a `setup.py` version source works."""
        configuration = Configuration(version_source_type="setup.py")
        configuration.generate()

        self.assertEqual(configuration._configuration["defaults"]["patches"], ["setup.py"])
        self.assertEqual(
            configuration._configuration["patches"],
            [
                {
                    "name": "setup.py",
                    "filePatterns": ["setup.py"],
                    "replacements": [{"find": 'version="{VersionRegex}"', "replace": 'version="{Version}"'}],
                },
            ],
        )

    def test_generate_with_pyproject_toml_version_source(self):
        """Test generating a configuration for a `pyproject.toml` version source works."""
        configuration = Configuration(version_source_type="pyproject.toml")
        configuration.generate()

        self.assertEqual(configuration._configuration["defaults"]["patches"], ["pyproject.toml"])
        self.assertEqual(
            configuration._configuration["patches"],
            [
                {
                    "name": "pyproject.toml",
                    "filePatterns": ["pyproject.toml"],
                    "replacements": [
                        {
                            "find": 'version = "{VersionRegex}"',
                            "replace": 'version = "{Version}"',
                        }
                    ],
                },
            ],
        )

    def test_generate_with_package_json_version_source(self):
        """Test generating a configuration for a `package.json` version source works."""
        configuration = Configuration(version_source_type="package.json")
        configuration.generate()

        self.assertEqual(configuration._configuration["defaults"]["patches"], ["package.json"])
        self.assertEqual(
            configuration._configuration["patches"],
            [
                {
                    "name": "package.json",
                    "filePatterns": ["package.json"],
                    "replacements": [
                        {
                            "find": '"version": "{VersionRegex}"',
                            "replace": '"version": "{Version}"',
                        }
                    ],
                },
            ],
        )

    def test_generate_with_breaking_change_indicated_by_major(self):
        """Test generating a configuration that indicates breaking changes by a major version change works."""
        configuration = Configuration(version_source_type="pyproject.toml", breaking_change_indicated_by="major")
        configuration.generate()

        self.assertEqual(configuration._configuration["commitMessageActions"][0]["action"], "IncrementMajor")
        self.assertEqual(configuration._configuration["commitMessageActions"][1]["action"], "IncrementMajor")

    def test_generate_with_breaking_change_indicated_by_minor(self):
        """Test generating a configuration that indicates breaking changes by a minor version change works."""
        configuration = Configuration(version_source_type="pyproject.toml", breaking_change_indicated_by="minor")
        configuration.generate()

        self.assertEqual(configuration._configuration["commitMessageActions"][0]["action"], "IncrementMinor")
        self.assertEqual(configuration._configuration["commitMessageActions"][1]["action"], "IncrementMinor")

    def test_generate_with_breaking_change_indicated_by_patch(self):
        """Test generating a configuration that indicates breaking changes by a patch version change works."""
        configuration = Configuration(version_source_type="pyproject.toml", breaking_change_indicated_by="patch")
        configuration.generate()

        self.assertEqual(configuration._configuration["commitMessageActions"][0]["action"], "IncrementPatch")
        self.assertEqual(configuration._configuration["commitMessageActions"][1]["action"], "IncrementPatch")

    def test_write(self):
        """Test writing a configuration to a file works."""
        configuration = Configuration(version_source_type="pyproject.toml")
        configuration.generate()

        with tempfile.NamedTemporaryFile() as temporary_file:
            configuration.write(temporary_file.name)
            hocon_configuration = json.loads(HOCONConverter.to_json(ConfigFactory.parse_file(temporary_file.name)))

        self.assertEqual(
            hocon_configuration,
            {
                "tagPrefix": "",
                "defaults": {
                    "tag": False,
                    "tagMessageFormat": "Release/{Tag}",
                    "preReleaseFormat": "RC{PreReleaseNumber}",
                    "buildMetaDataFormat": "{Branch}.{ShortHash}",
                    "includeBuildMetaData": False,
                    "whenNoValidCommitMessages": "IncrementPatch",
                    "patches": ["pyproject.toml"],
                },
                "patches": [
                    {
                        "name": "pyproject.toml",
                        "filePatterns": ["pyproject.toml"],
                        "replacements": [{"find": 'version = "{VersionRegex}"', "replace": 'version = "{Version}"'}],
                    },
                ],
                "commitMessageActions": [
                    {"pattern": "BREAKING CHANGE", "action": "IncrementMajor"},
                    {"pattern": "BREAKING-CHANGE", "action": "IncrementMajor"},
                    {"pattern": "FEA:", "action": "IncrementMinor"},
                ],
            },
        )
