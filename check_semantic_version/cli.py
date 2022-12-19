import argparse
import sys

from check_semantic_version.check_semantic_version import SUPPORTED_VERSION_SOURCE_FILES, check_versions_match


def main(argv=None):
    """Compare the current version to the expected semantic version. If they match, exit successfully with an exit code
    of 0; if they don't, exit with an exit code of 1.

    :return None:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "path",
        choices=SUPPORTED_VERSION_SOURCE_FILES,
        help=f"The path to the version source file. The file must be one of these types: {SUPPORTED_VERSION_SOURCE_FILES}",
    )

    parser.add_argument(
        "breaking_change_indicated_by",
        choices=["major", "minor", "patch"],
        default="major",
        nargs="?",
        help='The number in the semantic version that a breaking change should increment (must be one of "major", '
        '"minor", or "patch"). This is ignored if a `mkver.conf` file is present in the repository root.',
    )

    args = parser.parse_args(argv)
    match = check_versions_match(args.path, args.breaking_change_indicated_by)

    if not match:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
