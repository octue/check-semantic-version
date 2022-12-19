import logging
import os
import subprocess
import tempfile

from check_semantic_version.configuration import Configuration


logger = logging.getLogger(__name__)

RED = "\033[0;31m"
GREEN = "\033[0;32m"
NO_COLOUR = "\033[0m"

SUPPORTED_VERSION_SOURCE_FILES = {"setup.py", "pyproject.toml", "package.json"}


def check_versions_match(path, breaking_change_indicated_by="major"):
    """Check that the current version in the version source file at the given path matches the expected semantic version.

    :param str path: the path to the version source file (it must be of type "setup.py", "pyproject.toml", or "package.json")
    :param str breaking_change_indicated_by: the number in the semantic version that a breaking change should increment (must be one of "major", "minor", or "patch")
    :return bool: whether the versions match
    """
    version_source_type = os.path.split(path)[-1]
    current_version = get_current_version(path=path, version_source_type=version_source_type)

    expected_semantic_version = get_expected_semantic_version(
        version_source_type=version_source_type,
        breaking_change_indicated_by=breaking_change_indicated_by,
    )

    if not current_version or current_version == "null":
        print(f"{RED}VERSION FAILED CHECKS:{NO_COLOUR} No current version found.")
        return False

    if current_version != expected_semantic_version:
        print(
            f"{RED}VERSION FAILED CHECKS:{NO_COLOUR} The current version ({current_version}) is different from the "
            f"expected semantic version ({expected_semantic_version})."
        )
        return False

    print(
        f"{GREEN}VERSION PASSED CHECKS:{NO_COLOUR} The current version is the same as the expected semantic version: "
        f"{expected_semantic_version}."
    )


def get_current_version(path, version_source_type):
    """Get the current version of the package via the given version source. The relevant file containing the version
    information is assumed to be in the current working directory unless `version_source_file` is given.

    :param str path: the path to the version source file (it must be of type "setup.py", "pyproject.toml", or "package.json")
    :param str version_source_type: the type of file containing the current version number (must be one of "setup.py", "pyproject.toml", or "package.json")
    :return str: the version specified in the version source file
    """
    if version_source_type not in SUPPORTED_VERSION_SOURCE_FILES:
        raise ValueError(
            f"Unsupported version source received: {version_source_type!r}; options are "
            f"{SUPPORTED_VERSION_SOURCE_FILES!r}."
        )

    absolute_path = os.path.abspath(path)

    if version_source_type == "setup.py":
        command = ["python", absolute_path, "--version"]
        shell = False
    elif version_source_type == "pyproject.toml":
        command = ["poetry", "version", "-s", f"--directory={os.path.dirname(absolute_path)}"]
        shell = False
    elif version_source_type == "package.json":
        command = f"""cat {absolute_path} | jq --raw-output '.["version"]'"""
        shell = True

    process = subprocess.run(command, shell=shell, capture_output=True)
    return process.stdout.strip().decode("utf8")


def get_expected_semantic_version(version_source_type, breaking_change_indicated_by):
    """Get the expected semantic version for the package as of the current HEAD git commit.

    :param str version_source_type: the type of file containing the current version number (must be one of "setup.py", "pyproject.toml", or "package.json")
    :param str breaking_change_indicated_by: the number in the semantic version that a breaking change should increment (must be one of "major", "minor", or "patch")
    :return str:
    """
    with tempfile.NamedTemporaryFile() as temporary_configuration:
        if not os.path.exists("mkver.conf"):
            logger.warning("No `mkver.conf` file found. Generating one instead.")

            configuration = Configuration(
                version_source_type=version_source_type,
                breaking_change_indicated_by=breaking_change_indicated_by,
            )

            configuration.generate()
            config_path = temporary_configuration.name
            configuration.write(path=config_path)
        else:
            logger.warning("`mkver.conf` file found. Ignoring `breaking_change_indicated_by` input.")
            config_path = "mkver.conf"

        process = subprocess.run(["git-mkver", "-c", config_path, "next"], capture_output=True)

    return process.stdout.strip().decode("utf8")
