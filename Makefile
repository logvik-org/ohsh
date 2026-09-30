# SPDX-License-Identifier: Apache-2.0
.PHONY: help install dev test lint format build clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	pip install .

dev: ## Install the package with dev dependencies (editable) + pre-commit hooks
	pip install -e ".[dev]"
	pre-commit install || true

test: ## Run the test suite with coverage
	pytest --cov=ohsh --cov-report=term-missing

lint: ## Run ruff lint + format checks
	ruff check .
	ruff format --check .

format: ## Auto-fix lint issues and format the code
	ruff check --fix .
	ruff format .

build: ## Build sdist + wheel and validate them
	python -m build
	twine check dist/*

clean: ## Remove build/test artifacts
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
