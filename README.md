[![Release](https://github.com/octue/check-semantic-version/actions/workflows/release.yml/badge.svg)](https://github.com/octue/check-semantic-version/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/octue/check-semantic-version/branch/main/graph/badge.svg?token=AL0I3UVUV2)](https://codecov.io/gh/octue/check-semantic-version)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Semantic version checker
A GitHub action that automatically checks if a package's semantic version is correct based on the
[Conventional Commit](https://www.conventionalcommits.org/en/) messages on the branch.

It supports the following version source files:
- `setup.py`
- `pyproject.toml`
- `package.json`

## Usage
Add the action as a step in your workflow:

```yaml
steps:
- uses: actions/checkout@v3
  with:
    # Set fetch-depth to 0 to fetch all tags (necessary for `git-mkver` to determine the correct semantic version).
    fetch-depth: 0
- uses: octue/check-semantic-version@1.0.0.beta-6
  with:
    path: setup.py
    breaking_change_indicated_by: major
```

See [here](examples/workflow.yml) for an example in a workflow.

## More information

### How does it work?
The action compares the semantic version specified in the package's version source file (e.g. `setup.py`) against the
expected semantic version calculated by `git-mkver` from the Conventional Commits created since the last tagged version
in the branch's git history. If the version source file and the expected version agree, the checker exits with a zero
return code and displays a success message. If they don't agree, it exits with a non-zero return code and displays an
error message.

### Version source files
A version source file is one of the following, which must contain the package version:
* `setup.py`
* `pyproject.toml`
* `package.json`

If the version source file is not in the root directory, an optional argument can be passed to the checker to tell it to
look at a file of the version source file type at a different location.

### `mkver.conf` files
This action automatically generates a standard `mkver.conf` file to configure `git-mkver`. For more control, you can add
your own `mkver.conf` file to the repository root. Here are some example `mkver.conf` files:
- [Non-beta packages](examples/mkver.conf) (full semantic versioning)
- [Beta packages](examples/mkver-for-beta-versions.conf) (keeps the version below `1.0.0`)

### Example
For [this standard configuration file](examples/mkver.conf), if the last tagged version in your
repository is `0.7.3` and since then:
* There has been a breaking change and any number of features or bug-fixes/small-changes, the expected version will
  be `1.0.0`
* There has been a new feature, any number of bug-fixes/small-changes, but no breaking changes, the expected
  version will be `0.8.0`
* There has been a bug-fix/small-change but no breaking changes or new features, the expected version will be `0.7.4`
