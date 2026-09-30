<!-- SPDX-License-Identifier: Apache-2.0 -->
# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-29

First public release.

### Added
- `manifest.json`-driven discovery of HDL modules under a project tree.
- Recursive dependency resolution producing ordered, per-library
  source lists (`<lib>_verilog.src` / `<lib>_vhdl.src`).
- `libraries.src`: the order to compile the libraries in, with a warning when
  libraries depend on each other in a loop.
- CLI: `-t/--top-dir`, `-w/--work`, `-o/--output`, `-v/--verbose`,
  `--log-file`, `--version`.
- Verified integration examples for cocotb (Makefile + Python runner), VUnit,
  GHDL, NVC, and UVVM, plus documented examples for hog, Questa/ModelSim,
  Vivado, and Quartus.
- pytest test suite, ruff lint/format, pre-commit hooks, and dev setup scripts.
- CI (lint + Python 3.9-3.14 matrix, with an experimental 3.15 pre-release leg,
  + build), integration CI, and an automated
  TestPyPI → PyPI release workflow using Trusted Publishing.
- Apache 2.0 license.

### Changed
- Renamed the project from `oshsh` to **`ohsh`** (package, import path, and CLI
  command). The `oshsh` name on PyPI is an unrelated placeholder.
- Logging now attaches to the package logger so messages from all modules are
  captured. Output goes to the console by default, and to a file only with
  `--log-file`. Only the `ohsh` command configures logging, so calling `run()`
  from Python leaves the application's logging alone.
- A missing dependency now names the module that requires it.

### Fixed
- A relative `-t/--top-dir` is now resolved against the working directory
  (previously the resolved path was discarded).
- Running the tool no longer writes a stray `debug.log` into the working
  directory.
- Circular dependencies now exit with an error (exit code 8) naming the cycle,
  instead of recursing infinitely.

[Unreleased]: https://github.com/logvik-org/oshsh/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/logvik-org/oshsh/releases/tag/v0.1.0
