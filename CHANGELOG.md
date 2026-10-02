# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-02

First release.

### Added
- `ohsh` command (also `python -m ohsh`) that reads `manifest.json` files under a
  project tree, resolves the dependencies of a top module and writes per-library
  source lists in compile order, plus `libraries.src` with the library order.
- Clear errors with documented exit codes for missing, malformed, duplicate and
  circular manifests.
- Integration examples for cocotb, VUnit, GHDL, NVC, UVVM, hog, Questa, Vivado
  and Quartus.

[Unreleased]: https://github.com/logvik-org/ohsh/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/logvik-org/ohsh/releases/tag/v0.1.0
