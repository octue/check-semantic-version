import logging
import os
import signal
import subprocess
import sys
import tempfile

import tomlkit

from check_semantic_version.configuration import Configuration

logger = logging.getLogger(__name__)

logging.basicConfig(
    stream=sys.stdout,
    format="[%(asctime)s | %(levelname)s | %(name)s] %(message)s",
    level=logging.INFO,
)

RED = "\033[0;31m"
GREEN = "\033[0;32m"
NO_COLOUR = "\033[0m"

SUPPORTED_VERSION_SOURCE_FILES = {"setup.py", "pyproject.toml", "package.json", "Cargo.toml"}


class CalledProcessError(subprocess.CalledProcessError):
    """A `CalledProcessError` that reports the `stderr` output of the process that errored."""

    def __str__(self):
        if self.returncode and self.returncode < 0:
            try:
                return "Command '%s' died with %r. Stderr: %r" % (
                    self.cmd,
                    signal.Signals(-self.returncode),
                    self.stderr,
                )
            except ValueError:
                return "Command '%s' died with unknown signal %d. Stderr: %r" % (
                    self.cmd,
                    -self.returncode,
                    self.stderr,
                )

        return "Command '%s' returned non-zero exit status %d. Stderr: %r" % (self.cmd, self.returncode, self.stderr)


def check_versions_match(path, breaking_change_indicated_by="major"):
    """Check that the current version in the version source file at the given path matches the expected semantic version.

    :param str path: the path to the version source file (it must be of type "setup.py", "pyproject.toml", "package.json", or "Cargo.toml")
    :param str breaking_change_indicated_by: the number in the semantic version that a breaking change should increment (must be one of "major", "minor", or "patch")
    :return bool: whether the versions match
    """
    version_source_type = os.path.split(path)[-1]
    current_version = _get_current_version(path=path, version_source_type=version_source_type)

    expected_semantic_version = _get_expected_semantic_version(
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
    return True


def _get_current_version(path, version_source_type):
    """Get the current version of the package via the given version source. The relevant file containing the version
    information is assumed to be in the current working directory unless `version_source_file` is given.

    :param str path: the path to the version source file (it must be of type "setup.py", "pyproject.toml", "package.json", or "Cargo.toml")
    :param str version_source_type: the type of file containing the current version number (must be one of "setup.py", "pyproject.toml", "package.json", or "Cargo.toml")
    :return str: the version specified in the version source file
    """
    if version_source_type not in SUPPORTED_VERSION_SOURCE_FILES:
        raise ValueError(
            f"Unsupported version source received: {version_source_type!r}; options are "
            f"{SUPPORTED_VERSION_SOURCE_FILES!r}."
        )

    absolute_path = os.path.abspath(path)
    logger.info("Getting current version from %r.", absolute_path)

    if version_source_type == "Cargo.toml":
        current_version = _get_current_version_from_cargo_manifest(absolute_path)
        logger.info("Current version: %s", current_version)
        return current_version

    if version_source_type == "setup.py":
        command = ["python", absolute_path, "--version"]
        shell = False
    elif version_source_type == "pyproject.toml":
        command = ["poetry", "version", "-s", f"--directory={os.path.dirname(absolute_path)}"]
        shell = False
    elif version_source_type == "package.json":
        command = f"""cat {absolute_path} | jq --raw-output '.["version"]'"""
        shell = True

    try:
        process = subprocess.run(command, shell=shell, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        raise CalledProcessError(returncode=e.returncode, cmd=e.cmd, output=e.output, stderr=e.stderr) from None

    current_version = process.stdout.strip().decode("utf8")
    logger.info("Current version: %s", current_version)
    return current_version


def _get_current_version_from_cargo_manifest(path):
    """Get the current version of a Rust package or Cargo workspace from its `Cargo.toml` file.

    The version is taken from the `version` field of the `[package]` section if that section states one literally. If it
    doesn't, the version is taken from the `version` field of the `[workspace.package]` section, which is where a Cargo
    workspace declares the single version that its member crates inherit.

    :param str path: the absolute path to the `Cargo.toml` file
    :raise ValueError: if the file declares no version that can be resolved from the file alone
    :return str: the version declared in the file
    """
    with open(path, encoding="utf8") as f:
        manifest = tomlkit.parse(f.read())

    package_section = manifest.get("package") or {}
    workspace_package_section = (manifest.get("workspace") or {}).get("package") or {}

    for version in (package_section.get("version"), workspace_package_section.get("version")):
        # An inherited version (`version = { workspace = true }`) is a table rather than a string, so it is skipped in
        # favour of the workspace's own version.
        if isinstance(version, str):
            return str(version)

    if package_section.get("version") is not None:
        raise ValueError(
            f"The Cargo manifest at {path!r} inherits its version from a workspace it isn't the root of, so the "
            f"version can't be read from it. Point the checker at the workspace root's `Cargo.toml` file instead."
        )

    raise ValueError(
        f"No version found in the Cargo manifest at {path!r}. The version must be given as the `version` field of its "
        f"`[package]` section or, for a workspace, of its `[workspace.package]` section."
    )


def _get_expected_semantic_version(version_source_type, breaking_change_indicated_by):
    """Get the expected semantic version for the package as of the current HEAD git commit.

    :param str version_source_type: the type of file containing the current version number (must be one of "setup.py", "pyproject.toml", "package.json", or "Cargo.toml")
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
            logger.info("`mkver.conf` file created at %r.", config_path)

        else:
            config_path = os.path.abspath("mkver.conf")
            logger.warning("`mkver.conf` file found at %r. Ignoring `breaking_change_indicated_by` input.", config_path)

        try:
            process = subprocess.run(["git-mkver", "-c", config_path, "next"], capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            raise CalledProcessError(returncode=e.returncode, cmd=e.cmd, output=e.output, stderr=e.stderr)

    return process.stdout.strip().decode("utf8")
