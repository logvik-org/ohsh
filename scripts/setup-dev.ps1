# SPDX-License-Identifier: Apache-2.0
# Bootstrap a local development environment for ohsh (Windows / PowerShell).
$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
$VenvDir = if ($env:VENV_DIR) { $env:VENV_DIR } else { ".venv" }

if (-not (Test-Path $VenvDir)) {
    Write-Host ">> Creating virtual environment in $VenvDir"
    & $Python -m venv $VenvDir
}

& (Join-Path $VenvDir "Scripts\Activate.ps1")

Write-Host ">> Upgrading pip"
python -m pip install --upgrade pip

Write-Host ">> Installing ohsh with dev dependencies (editable)"
pip install -e ".[dev]"

Write-Host ">> Installing pre-commit hooks"
try { pre-commit install } catch { Write-Host "   (pre-commit not configured; skipping)" }

Write-Host ""
Write-Host "Done. Activate the environment with:  $VenvDir\Scripts\Activate.ps1"
Write-Host "Run the test suite with:             make test"
