import copy

from pyhocon import ConfigFactory, HOCONConverter

DEFAULTS = {
    "tag": False,
    "tagMessageFormat": "Release/{Tag}",
    "preReleaseFormat": "RC{PreReleaseNumber}",
    "buildMetaDataFormat": "{Branch}.{ShortHash}",
    "includeBuildMetaData": False,
    "whenNoValidCommitMessages": "IncrementPatch",
    "patches": [],
}

PATCHES = {
    "setup.py": {
        "name": "setup.py",
        "filePatterns": ["setup.py"],
        "replacements": [
            {
                "find": 'version="{VersionRegex}"',
                "replace": 'version="{Version}"',
            },
        ],
    },
    "pyproject.toml": {
        "name": "pyproject.toml",
        "filePatterns": ["pyproject.toml"],
        "replacements": [
            {
                "find": 'version = "{VersionRegex}"',
                "replace": 'version = "{Version}"',
            }
        ],
    },
    "package.json": {
        "name": "package.json",
        "filePatterns": ["package.json"],
        "replacements": [
            {
                "find": '"version": "{VersionRegex}"',
                "replace": '"version": "{Version}"',
            }
        ],
    },
}

COMMIT_MESSAGE_ACTIONS_TEMPLATE = [
    {
        "pattern": "BREAKING CHANGE",
        "action": None,
    },
    {
        "pattern": "BREAKING-CHANGE",
        "action": None,
    },
    {
        "pattern": "FEA:",
        "action": "IncrementMinor",
    },
]

BREAKING_CHANGE_COMMIT_ACTION_MAPPING = {
    "major": "IncrementMajor",
    "minor": "IncrementMinor",
    "patch": "IncrementPatch",
}


class Configuration:
    """A representation of a `mkver.conf` (`git-mkver` configuration) file.

    :param str version_source_type: the type of file containing the current version number (must be one of "setup.py", "pyproject.toml", or "package.json")
    :param str breaking_change_indicated_by: the number in the semantic version that a breaking change should increment (must be one of "major", "minor", or "patch")
    :param str tag_prefix: the prefix to be used before version numbers (e.g. "v")
    :return None:
    """

    def __init__(self, version_source_type, breaking_change_indicated_by="major", tag_prefix=""):
        self.version_source_type = version_source_type
        self.breaking_change_indicated_by = breaking_change_indicated_by.lower()
        self.tag_prefix = tag_prefix

    def generate(self):
        """Generate the configuration.

        :return None:
        """
        self._configuration = {
            "tagPrefix": self.tag_prefix,
            "defaults": self._get_defaults(),
            "patches": [PATCHES[self.version_source_type]],
            "commitMessageActions": self._get_commit_message_actions(),
        }

        self._hocon_configuration = ConfigFactory.from_dict(self._configuration)

    def write(self, path):
        """Write the configuration to a file.

        :param str path: the path to write the file to
        :return None:
        """
        with open(path, "w") as f:
            f.write(HOCONConverter.to_hocon(self._hocon_configuration))

    def _get_defaults(self):
        """Generate the defaults section of the configuration.

        :return dict:
        """
        defaults = DEFAULTS.copy()
        defaults["patches"] = [self.version_source_type]
        return defaults

    def _get_commit_message_actions(self):
        """Generate the commit message actions section of the configuration.

        :return dict:
        """
        actions = copy.deepcopy(COMMIT_MESSAGE_ACTIONS_TEMPLATE)

        for pattern in actions[:2]:
            pattern["action"] = BREAKING_CHANGE_COMMIT_ACTION_MAPPING[self.breaking_change_indicated_by]

        return actions
