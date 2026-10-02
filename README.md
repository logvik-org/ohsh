<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="docs/images/logo-light.png">
    <img alt="ohsh: a humble HDL source handler" src="https://raw.githubusercontent.com/logvik-org/ohsh/main/docs/images/logo-light.png" width="600">
  </picture>
</p>

[![CI](https://github.com/logvik-org/ohsh/actions/workflows/ci.yml/badge.svg)](https://github.com/logvik-org/ohsh/actions/workflows/ci.yml)
[![Integrations](https://github.com/logvik-org/ohsh/actions/workflows/integration.yml/badge.svg)](https://github.com/logvik-org/ohsh/actions/workflows/integration.yml)
[![Docs](https://readthedocs.org/projects/ohsh/badge/?version=latest)](https://ohsh.readthedocs.io)
[![PyPI](https://img.shields.io/pypi/v/ohsh.svg)](https://pypi.org/project/ohsh/)
[![Python](https://img.shields.io/pypi/pyversions/ohsh.svg)](https://pypi.org/project/ohsh/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/logvik-org/ohsh/blob/main/LICENSE)

**ohsh** is a small, deliberately humble command-line tool that figures out, in
the right order, which HDL (SystemVerilog and VHDL) source files your
design needs - by reading simple per-module `manifest.json` files and resolving
their dependencies.

It is a *companion* to the big build flows (like [hog](https://hog.readthedocs.io),
Vivado, Quartus, Questa, cocotb, VUnit, …), not a replacement for them. ohsh
just answers one question well - *"what files, in what order, for which
libraries?"* - and hands you plain `.src` lists you can feed anywhere.

## Features

- Auto-discovers HDL module manifests anywhere under a project tree.
- Resolves module dependencies recursively, across libraries.
- Detects circular dependencies and exits with an error naming the cycle.
- Emits ordered, per-library source lists for SystemVerilog and VHDL.
- Writes the order to compile the libraries in.
- Validates that every referenced source file actually exists.
- Pure Python, zero runtime dependencies.

## Installation

```bash
pip install ohsh
```

Or from a clone:

```bash
git clone https://github.com/logvik-org/ohsh.git
cd ohsh
pip install .
```

## Usage

```bash
ohsh [OPTIONS] MODULE
```

ohsh will:
1. Search for all `manifest*.json` files starting from `--top-dir`.
2. Resolve dependencies for `MODULE` (the top-level).
3. Generate ordered SystemVerilog and VHDL source lists per library.
4. Write them as `<lib>_systemverilog.src` / `<lib>_vhdl.src` in the output directory.
5. Write the library compile order to `libraries.src`.

### Options

| Option              | Description                                                            | Default      |
|---------------------|------------------------------------------------------------------------|--------------|
| `-t`, `--top-dir`   | Project top-level directory, the base for manifest discovery.          | cwd          |
| `-w`, `--work`      | Library for the top module, which `work` in its manifest refers to.    | `work`       |
| `-o`, `--output`    | Directory for the `.src` lists and `libraries.src`, created if missing. | cwd          |
| `-v`, `--verbose`   | Show progress (`-v`) or debug details (`-vv`).                         | quiet        |
| `--log-file PATH`   | Also write logs to a file (no log file is written by default).         | none         |
| `--version`         | Print version and exit.                                                |              |
| `-h`, `--help`      | Show help and exit.                                                    |              |

### Example

Give each module a `manifest.json` next to its sources:

```
project/
├── accumulator/
│   ├── accumulator.vhd
│   └── manifest.json
└── adder/
    ├── adder.vhd
    └── manifest.json
```

```json
{
  "module": "accumulator",
  "sources": ["accumulator.vhd"],
  "dependencies": {
    "work": ["adder"]
  }
}
```

```json
{
  "module": "adder",
  "sources": ["adder.vhd"]
}
```

Then run ohsh in the project directory with the top module's name:

```bash
cd project
ohsh accumulator
```

It writes `work_vhdl.src` with the sources in compile order:

```
/path/to/project/adder/adder.vhd
/path/to/project/accumulator/accumulator.vhd
```

and `libraries.src` with the libraries to compile (here only `work`). Modules
with SystemVerilog sources go to `<lib>_systemverilog.src` in the same way. See
[the manifest file format](https://ohsh.readthedocs.io/en/latest/manifest-format.html)
for dependencies across libraries.

`libraries.src` lists the library names, one per line, in the order to compile
them: each library comes after the libraries it uses. Compile the libraries in
this order rather than hard-coding it. If libraries depend on each other in a
loop (a module in `libA` uses `libB` and a module in `libB` uses `libA`), no
such order exists. ohsh then logs a warning and writes a best-effort order,
which works for tools that sort files themselves (such as Vivado or Quartus
projects) but may fail with tools that compile one library at a time.

## Documentation

The full documentation is at [ohsh.readthedocs.io](https://ohsh.readthedocs.io):

- [Getting started](https://ohsh.readthedocs.io/en/latest/getting-started.html)
- [Manifest file format](https://ohsh.readthedocs.io/en/latest/manifest-format.html)
- [Integrations with simulators and build tools](https://ohsh.readthedocs.io/en/latest/integrations.html)
- [Exit codes](https://ohsh.readthedocs.io/en/latest/exit-codes.html)
- [Contributing and development](https://github.com/logvik-org/ohsh/blob/main/CONTRIBUTING.md)

## License

Licensed under the **Apache License 2.0**. See [LICENSE](https://github.com/logvik-org/ohsh/blob/main/LICENSE) and
[NOTICE](https://github.com/logvik-org/ohsh/blob/main/NOTICE).

## Author

**Ola Groettvik** - [GitHub](https://github.com/olagrottvik)

Contributions, issues, and suggestions are welcome!
