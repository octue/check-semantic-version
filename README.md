[![codecov](https://codecov.io/gh/octue/check-semantic-version/branch/main/graph/badge.svg?token=AL0I3UVUV2)](https://codecov.io/gh/octue/check-semantic-version)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Semantic version checker
A GitHub action and command-line tool that automatically checks if a package's semantic version is correct. It compares
the semantic version specified in the given type of "version source" file against the expected semantic version
calculated from the commits since the last tagged version in the git history. This is determined according to the
mandatory `git-mkver` configuration file in the working directory. If the version source file and the expected version
agree, the checker exits with a zero return code and displays a success message. If they don't agree, it exits with a
non-zero return code and displays an error message.

The checker works with:
- `setup.py`
- `pyproject.toml`
- `package.json`

## GitHub action
The checker can be easily used as a step in a GitHub workflow:

```yaml
steps:
- uses: actions/checkout@v3
  with:
    # Set fetch-depth to 0 to fetch all tags (necessary for git-mkver to determine the correct semantic version).
    fetch-depth: 0
- uses: octue/check-semantic-version@1.0.0.beta-0
  with:
    version_source_type: setup.py
```

See [here](examples/workflow.yml) for an example in a workflow.

## CLI
```shell
usage: check-semantic-version [-h] [--file FILE] {setup.py,pyproject.toml,package.json}

positional arguments:
  {setup.py,pyproject.toml,package.json}
                        The type of file to look for the version in. It must be one of ['setup.py', 'pyproject.toml', 'package.json'] and is assumed to be in the
                        repository root unless the --file option is also given

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           The path to the version source file if it isn't in the repository root e.g. path/to/setup.py
```

## More information

### Example
For [this standard configuration file](examples/mkver.conf), if the last tagged version in your
repository is `0.7.3` and since then:
* There has been a breaking change and any number of features or bug-fixes/small-changes, the expected version will
  be `1.0.0`
* There has been a new feature, any number of bug-fixes/small-changes, but no breaking changes, the expected
  version will be `0.8.0`
* There has been a bug-fix/small-change but no breaking changes or new features, the expected version will be `0.7.4`

### Version source files
A version source file is one of the following, which must contain the package version:
* `setup.py` (this covers versions defined in a `setup.py` or `setup.cfg` file)
* `pyproject.toml`
* `package.json`

If the version source file is not in the root directory, an optional argument can be passed to the checker to tell it to
look at a file of the version source file type at a different location.

### Extra requirements
Note that this command requires:
* `git-mkver` to be installed and available in the shell as `git-mkver` (this is already done if using the GitHub action)
* A `mkver.conf` file to be present in the working directory (usually the repository root):
  - [See an example for non-beta packages](examples/mkver.conf) (full semantic versioning)
  - [See an example for packages in beta](examples/mkver-for-beta-versions.conf) (keeps the version below `1.0.0`)
