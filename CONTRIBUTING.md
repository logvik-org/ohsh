<!-- SPDX-License-Identifier: Apache-2.0 -->
# Contributing to ohsh

Thanks for your interest in improving **ohsh**! This is a small project, so the
process is light.

## Development setup

```bash
git clone https://github.com/logvik-org/oshsh.git
cd oshsh
./scripts/setup-dev.sh        # creates .venv, installs ".[dev]", sets up pre-commit
# Windows: ./scripts/setup-dev.ps1
```

Or, if you manage your own environment:

```bash
pip install -e ".[dev]"
pre-commit install
```

## Everyday commands

| Command       | What it does                          |
|---------------|---------------------------------------|
| `make test`   | Run the test suite with coverage      |
| `make lint`   | Ruff lint + format check              |
| `make format` | Auto-fix lint issues and format       |
| `make build`  | Build sdist + wheel, validate them    |

## Before you open a pull request

1. Add or update tests for your change (`tests/`). New behavior should be
   covered; bug fixes should come with a regression test.
2. Make sure `make test` and `make lint` pass.
3. Update `CHANGELOG.md` under the `Unreleased` section.
4. Keep commits focused and write clear commit messages.

CI runs ruff, the test matrix (Python 3.9-3.14, plus an experimental 3.15
pre-release leg), a package build, and the
end-to-end integration examples. PRs need a green pipeline to merge.

## Coding style

- Code is formatted and linted with [ruff](https://docs.astral.sh/ruff/); the
  config lives in `pyproject.toml`. `pre-commit` applies it automatically.
- Keep ohsh dependency-free at runtime (standard library only).
- Add a `# SPDX-License-Identifier: Apache-2.0` header to new source files.

## Releasing (maintainers)

Releases are automated via `.github/workflows/release.yml`:

1. Bump `__version__` in `ohsh/__init__.py` and update `CHANGELOG.md`.
2. Tag the commit: `git tag v1.2.3 && git push --tags`.
   → publishes to **TestPyPI**.
3. Verify the TestPyPI release, then publish a **GitHub Release** for the tag.
   → publishes to **PyPI**.

Publishing uses PyPI [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
(OIDC) - no API tokens are stored. The `testpypi` and `pypi` environments and the
trusted publisher must be configured in the repository / PyPI project settings.

## License

By contributing, you agree that your contributions are licensed under the
Apache License 2.0.
