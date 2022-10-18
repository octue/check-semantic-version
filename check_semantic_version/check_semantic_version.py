import argparse
import copy
import logging
import os
import subprocess
import sys
import tempfile

from check_semantic_version.configuration import Configuration


logger = logging.getLogger(__name__)

RED = "\033[0;31m"
GREEN = "\033[0;32m"
NO_COLOUR = "\033[0m"

VERSION_PARAMETERS = {
    "setup.py": [["python", "setup.py", "--version"], False],
    "pyproject.toml": [["poetry", "version", "-s"], False],
    "package.json": ["""cat {} | jq --raw-output '.["version"]'""", True],
}


def get_current_version(path, version_source_type):
    """Get the current version of the package via the given version source. The relevant file containing the version
    information is assumed to be in the current working directory unless `version_source_file` is given.

    :param str path: the path to the version source file (it must be of type "setup.py", "pyproject.toml", or "package.json")
    :param str version_source_type: the type of file containing the current version number (must be one of "setup.py", "pyproject.toml", or "package.json")
    :return str: the version specified in the version source file
    """
    try:
        version_parameters = copy.deepcopy(VERSION_PARAMETERS[version_source_type])
    except KeyError:
        raise ValueError(
            f"Unsupported version source received: {version_source_type!r}; options are {list(VERSION_PARAMETERS.keys())!r}."
        )

    original_working_directory = os.getcwd()

    if version_source_type in {"setup.py", "pyproject.toml"}:
        os.chdir(os.path.dirname(os.path.abspath(path)))

    elif version_source_type == "package.json":
        version_parameters[0] = version_parameters[0].format(path)

    process = subprocess.run(version_parameters[0], shell=version_parameters[1], capture_output=True)

    if os.getcwd() != original_working_directory:
        os.chdir(original_working_directory)

    return process.stdout.strip().decode("utf8")


def get_expected_semantic_version(version_source_type, breaking_change_indicated_by):
    """Get the expected semantic version for the package as of the current HEAD git commit.

    :param str version_source_type: the type of file containing the current version number (must be one of "setup.py", "pyproject.toml", or "package.json")
    :param str breaking_change_indicated_by: the semantic version number type that a breaking change increments (must be one of "major", "minor", or "patch")
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
            config_path = "mkver.conf"

        process = subprocess.run(["git-mkver", "-c", config_path, "next"], capture_output=True)

    return process.stdout.strip().decode("utf8")


def main(argv=None):
    """Compare the current version to the expected semantic version. If they match, exit successfully with an exit code
    of 0; if they don't, exit with an exit code of 1.

    :return None:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "path",
        choices=list(VERSION_PARAMETERS.keys()),
        help=f"The path to the version source file. It must be one of these types: {list(VERSION_PARAMETERS.keys())}",
    )

    parser.add_argument(
        "breaking_change_indicated_by",
        choices=["major", "minor", "patch"],
        nargs="?",
        help='The semantic version number type that a breaking change increments (must be one of "major", "minor", or "patch"). This is ignored if a `mkver.conf` file is present in the repository root.',
    )

    args = parser.parse_args(argv)

    version_source_type = os.path.split(args.path)[-1]
    current_version = get_current_version(path=args.path, version_source_type=version_source_type)

    expected_semantic_version = get_expected_semantic_version(
        version_source_type=version_source_type,
        breaking_change_indicated_by=args.breaking_change_indicated_by,
    )

    if not current_version or current_version == "null":
        print(f"{RED}VERSION FAILED CHECKS:{NO_COLOUR} No current version found.")
        sys.exit(1)

    if current_version != expected_semantic_version:
        print(
            f"{RED}VERSION FAILED CHECKS:{NO_COLOUR} The current version ({current_version}) is different from the "
            f"expected semantic version ({expected_semantic_version})."
        )
        sys.exit(1)

    print(
        f"{GREEN}VERSION PASSED CHECKS:{NO_COLOUR} The current version is the same as the expected semantic version: "
        f"{expected_semantic_version}."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
