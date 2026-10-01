#!/usr/bin/env bash
# Set up a local development environment for ohsh: create .venv, install ohsh
# (editable) with the dev and examples dependencies, and install the pre-commit
# hooks. Works in bash and zsh.
#
#   ./scripts/setup-dev.sh         # set up, then: source .venv/bin/activate
#   source scripts/setup-dev.sh    # set up and stay in the activated venv
#
# When sourced, this file runs inside your interactive shell, so the setup steps
# run in a subshell: their `set -euo pipefail` must not leak out, or the next
# failing command would exit your shell and close the terminal.

if [ -n "${BASH_SOURCE:-}" ]; then
    _ohsh_script="${BASH_SOURCE[0]}"
else
    _ohsh_script="$(eval 'echo "${(%):-%x}"')"
fi

_ohsh_sourced=false
case "${ZSH_EVAL_CONTEXT:-}" in *:file*) _ohsh_sourced=true ;; esac
if [ -n "${BASH_SOURCE:-}" ] && [ "${BASH_SOURCE[0]}" != "$0" ]; then
    _ohsh_sourced=true
fi

_ohsh_root="$(cd "$(dirname "$_ohsh_script")/.." && pwd)"
_ohsh_venv="${VENV_DIR:-$_ohsh_root/.venv}"

(
    set -euo pipefail
    cd "$_ohsh_root"

    if [ ! -d "$_ohsh_venv" ]; then
        echo ">> Creating virtual environment in $_ohsh_venv"
        "${PYTHON:-python3}" -m venv "$_ohsh_venv"
    fi

    echo ">> Upgrading pip"
    "$_ohsh_venv/bin/python" -m pip install --upgrade pip

    echo ">> Installing ohsh (editable) with dev and examples dependencies"
    "$_ohsh_venv/bin/python" -m pip install -e ".[dev,examples]"

    echo ">> Installing pre-commit hooks"
    "$_ohsh_venv/bin/pre-commit" install || echo "   (not a git checkout, skipping)"
)
_ohsh_status=$?

if [ "$_ohsh_status" -ne 0 ]; then
    echo "Setup failed." >&2
elif [ "$_ohsh_sourced" = true ]; then
    # shellcheck disable=SC1091
    . "$_ohsh_venv/bin/activate"
    echo "Done. The virtual environment is active. Run the tests with: make test"
else
    echo "Done. Activate the environment with: source $_ohsh_venv/bin/activate"
    echo "Run the tests with: make test"
fi

if [ "$_ohsh_sourced" = true ]; then
    # Clean up the helper variables, then leave the sourced file with the
    # setup status. The status is expanded before eval runs the unset.
    eval "unset _ohsh_script _ohsh_sourced _ohsh_root _ohsh_venv _ohsh_status; return $_ohsh_status"
fi
exit "$_ohsh_status"
