import argparse
import os
import sys

from check_semantic_version.check_semantic_version import (
    GREEN,
    NO_COLOUR,
    RED,
    VERSION_PARAMETERS,
    get_current_version,
    get_expected_semantic_version,
)


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
        default="major",
        nargs="?",
        help='the number in the semantic version that a breaking change should increment (must be one of "major", "minor", or "patch"). This is ignored if a `mkver.conf` file is present in the repository root.',
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
