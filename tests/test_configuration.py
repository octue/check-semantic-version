from unittest import TestCase

from check_semantic_version.configuration import Configuration


class TestConfiguration(TestCase):
    def test_generate_with_setup_py_version_source(self):
        configuration = Configuration(version_source_type="setup.py")
        configuration.generate()

        self.assertEqual(configuration._configuration["defaults"]["patches"], ["setup.py"])
        self.assertEqual(
            configuration._configuration["patches"],
            {
                "name": "setup.py",
                "filePatterns": ["setup.py"],
                "replacements": [{"find": 'version="{VersionRegex}"', "replace": 'version="{Version}"'}],
            },
        )

    def test_generate_with_pyproject_toml_version_source(self):
        configuration = Configuration(version_source_type="pyproject.toml")
        configuration.generate()

        self.assertEqual(configuration._configuration["defaults"]["patches"], ["pyproject.toml"])
        self.assertEqual(
            configuration._configuration["patches"],
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
        )

    def test_generate_with_package_json_version_source(self):
        configuration = Configuration(version_source_type="package.json")
        configuration.generate()

        self.assertEqual(configuration._configuration["defaults"]["patches"], ["package.json"])
        self.assertEqual(
            configuration._configuration["patches"],
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
        )

    def test_generate_with_breaking_change_indicated_by_major(self):
        configuration = Configuration(version_source_type="pyproject.toml", breaking_change_indicated_by="major")
        configuration.generate()

        self.assertEqual(configuration._configuration["commitMessageActions"][0]["action"], "IncrementMajor")
        self.assertEqual(configuration._configuration["commitMessageActions"][1]["action"], "IncrementMajor")

    def test_generate_with_breaking_change_indicated_by_minor(self):
        configuration = Configuration(version_source_type="pyproject.toml", breaking_change_indicated_by="minor")
        configuration.generate()

        self.assertEqual(configuration._configuration["commitMessageActions"][0]["action"], "IncrementMinor")
        self.assertEqual(configuration._configuration["commitMessageActions"][1]["action"], "IncrementMinor")

    def test_generate_with_breaking_change_indicated_by_patch(self):
        configuration = Configuration(version_source_type="pyproject.toml", breaking_change_indicated_by="patch")
        configuration.generate()

        self.assertEqual(configuration._configuration["commitMessageActions"][0]["action"], "IncrementPatch")
        self.assertEqual(configuration._configuration["commitMessageActions"][1]["action"], "IncrementPatch")
