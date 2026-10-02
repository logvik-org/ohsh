.PHONY: help dev test lint build examples clean

VENV ?= .venv
VENV_BIN := $(VENV)/bin
# Written by scripts/setup-dev.sh after a successful setup. Every target depends
# on it, so the venv is set up again whenever pyproject.toml (and with it the
# dependencies) is newer. Code changes need no reinstall: ohsh is installed in
# editable mode.
STAMP := $(VENV)/.installed

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

dev: ## Create or update the dev environment in .venv
	VENV_DIR=$(abspath $(VENV)) scripts/setup-dev.sh

$(STAMP): pyproject.toml
	VENV_DIR=$(abspath $(VENV)) scripts/setup-dev.sh

test: $(STAMP) ## Run the test suite with coverage
	$(VENV_BIN)/python -m pytest --cov=ohsh --cov-report=term-missing

lint: $(STAMP) ## Run every pre-commit check on all files, fixing what it can
	$(VENV_BIN)/pre-commit run --all-files

build: $(STAMP) ## Build sdist + wheel and validate them
	$(VENV_BIN)/python -m build
	$(VENV_BIN)/python -m twine check dist/*

examples: $(STAMP) ## Run the integration examples that CI runs
	PATH="$(abspath $(VENV_BIN)):$$PATH" scripts/run-examples.sh

clean: ## Remove build, test and example outputs (keeps .venv)
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .coverage htmlcov
	find . -path ./$(VENV) -prune -o -type d -name __pycache__ -exec rm -rf {} +
	find examples -type d \( -name build -o -name sim_build -o -name vunit_out \) -prune -exec rm -rf {} +
	find examples -name results.xml -delete
