#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Bootstrap a local development environment for ohsh.
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

if [ ! -d "$VENV_DIR" ]; then
    echo ">> Creating virtual environment in $VENV_DIR"
    "$PYTHON" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo ">> Upgrading pip"
python -m pip install --upgrade pip

echo ">> Installing ohsh with dev dependencies (editable)"
pip install -e ".[dev]"

echo ">> Installing pre-commit hooks"
pre-commit install || echo "   (pre-commit not configured; skipping)"

echo
echo "Done. Activate the environment with:  source $VENV_DIR/bin/activate"
echo "Run the test suite with:             make test"
