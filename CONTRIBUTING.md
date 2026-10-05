# Contributing to ohsh

Thanks for your interest in improving **ohsh**! This is a small project, so the
process is light.

## Development setup

Development needs Python 3.9 or newer, although ohsh itself runs on 3.6: the
build and lint tools have dropped the older versions.

```bash
git clone https://github.com/logvik-org/ohsh.git
cd ohsh
source scripts/setup-dev.sh
```

This creates `.venv`, installs ohsh in editable mode with the `dev`, `examples`
and `docs` extras, installs the pre-commit hooks, and leaves the environment
active. Running it as `./scripts/setup-dev.sh` instead does the same without
activating the environment.

Or, if you manage your own environment:

```bash
pip install -e ".[dev,examples,docs]"
pre-commit install
```

## Everyday commands

| Command         | What it does                                          |
|-----------------|-------------------------------------------------------|
| `make test`     | Run the test suite with coverage                      |
| `make lint`     | Run every pre-commit check, fixing what it can        |
| `make examples` | Run the integration examples CI runs                  |
| `make build`    | Build sdist + wheel and validate them                 |
| `make docs`     | Build the documentation site into `docs/_build/html`  |
| `make dev`      | Set up `.venv` again (e.g. after changing extras)     |
| `make clean`    | Remove build, test and example outputs                |

The make targets use `.venv` directly, so they work without activating it. When
`pyproject.toml` changes, they set the environment up again before running.
`make examples` needs the simulators described in
[`examples/README.md`](examples/README.md).

## Before you open a pull request

1. Add or update tests for your change (`tests/`). New behavior should be
   covered, and bug fixes should come with a regression test.
2. Make sure `make test` and `make lint` pass, and `make examples` if you
   changed the examples or the output format.
3. Update `CHANGELOG.md` under the `Unreleased` section.
4. Keep commits focused and write clear commit messages.

CI runs the pre-commit checks, the test matrix (Python 3.6-3.14, plus an
experimental 3.15 pre-release leg), a package build, and the end-to-end
integration examples. PRs need a green pipeline to merge.

## Documentation

The documentation site is built with [Sphinx](https://www.sphinx-doc.org) from
the Markdown pages in `docs/` and published on
[Read the Docs](https://ohsh.readthedocs.io), which rebuilds it on every push to
`main` and for every release tag. Its configuration is in `.readthedocs.yaml`
and `docs/conf.py`. Run `make docs` to check a change locally: it fails on any
warning, like the Read the Docs build and CI.

## Coding style

- All lint checks run through [pre-commit](https://pre-commit.com), which also
  pins their versions in `.pre-commit-config.yaml`: Python code is formatted and
  linted with [ruff](https://docs.astral.sh/ruff/) (config in `pyproject.toml`),
  shell scripts are checked with shellcheck, and workflows with actionlint.
- Keep ohsh dependency-free at runtime (standard library only).
- Add a `# SPDX-License-Identifier: Apache-2.0` header to new modules in `ohsh/`.

## Releasing (maintainers)

1. On `main`, bump `__version__` in `ohsh/__init__.py` and move the
   `Unreleased` entries in `CHANGELOG.md` under a new `## [<version>] - <date>`
   heading.
2. Publish a **GitHub Release** with a new tag `v<version>` (for example
   `v1.2.3`) on that commit.

Publishing the release starts `.github/workflows/release.yml`, which runs these
jobs in order and stops at the first failure:

1. The CI and integration workflows.
2. Build, after checking that the tag equals `v` + `__version__`.
3. Upload to **TestPyPI**.
4. Install the package from TestPyPI and run `scripts/smoke-test.sh`.
5. Upload the same files to **PyPI**.

If a job fails for a reason outside the code (for example TestPyPI was slow),
re-run the failed jobs from the Actions tab. TestPyPI skips files it already has,
so a re-run gets past step 3. If the code needs a fix, delete the release and its
tag, fix the code, and publish the release again. A version that reached PyPI
can never be uploaded again, so bump the version in that case.

To approve each PyPI upload by hand, add yourself as a required reviewer on the
`pypi` environment in the repository settings.

Publishing uses PyPI [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
(OIDC) - no API tokens are stored. The `testpypi` and `pypi` environments and the
trusted publisher must be configured in the repository / PyPI project settings.

## License

By contributing, you agree that your contributions are licensed under the
Apache License 2.0.
