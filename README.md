# ohsh - Ola's HDL Source Handler

[![CI](https://github.com/logvik-org/ohsh/actions/workflows/ci.yml/badge.svg)](https://github.com/logvik-org/ohsh/actions/workflows/ci.yml)
[![Integrations](https://github.com/logvik-org/ohsh/actions/workflows/integration.yml/badge.svg)](https://github.com/logvik-org/ohsh/actions/workflows/integration.yml)
[![PyPI](https://img.shields.io/pypi/v/ohsh.svg)](https://pypi.org/project/ohsh/)
[![Python](https://img.shields.io/pypi/pyversions/ohsh.svg)](https://pypi.org/project/ohsh/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/logvik-org/ohsh/blob/main/LICENSE)

**ohsh** is a small, deliberately humble command-line tool that figures out, in
the right order, which HDL (Verilog / SystemVerilog / VHDL) source files your
design needs - by reading simple per-module `manifest.json` files and resolving
their dependencies.

It is a *companion* to the big build flows (like [hog](https://hog.readthedocs.io),
Vivado, Quartus, Questa, cocotb, VUnit, …), not a replacement for them. ohsh
just answers one question well - *"what files, in what order, for which
libraries?"* - and hands you plain `.src` lists you can feed anywhere.

> So simple it's an *oh sh… that was easy* moment. 🙂

---

## Features

- 🔍 Auto-discovers HDL module manifests anywhere under a project tree.
- 📂 Resolves module dependencies recursively, across libraries.
- 🔁 Detects circular dependencies and exits with an error naming the cycle.
- 📝 Emits ordered, per-library source lists for Verilog and VHDL.
- 📚 Writes the order to compile the libraries in.
- ✅ Validates that every referenced source file actually exists.
- 🐍 Pure Python, zero runtime dependencies.

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
3. Generate ordered Verilog and VHDL source lists per library.
4. Write them as `<lib>_verilog.src` / `<lib>_vhdl.src` in the output directory.
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

```bash
ohsh -t /path/to/hdl_project -w mylib -o ./src_lists top_module
```

Produces:

```
src_lists/
├── libraries.src
├── mylib_verilog.src
└── mylib_vhdl.src
```

Each `<lib>_verilog.src` / `<lib>_vhdl.src` file contains absolute paths to the
source files, one per line, in compilation order.

`libraries.src` lists the library names, one per line, in the order to compile
them: each library comes after the libraries it uses. Compile the libraries in
this order rather than hard-coding it. If libraries depend on each other in a
loop (a module in `libA` uses `libB` and a module in `libB` uses `libA`), no
such order exists. ohsh then logs a warning and writes a best-effort order,
which works for tools that sort files themselves (such as Vivado or Quartus
projects) but may fail with tools that compile one library at a time.

## Documentation

- [Manifest file format](https://github.com/logvik-org/ohsh/blob/main/docs/manifest-format.md)
- [Exit codes](https://github.com/logvik-org/ohsh/blob/main/docs/exit-codes.md)
- [Integrations with simulators and build tools](https://github.com/logvik-org/ohsh/blob/main/docs/integrations.md)
- [Contributing and development](https://github.com/logvik-org/ohsh/blob/main/CONTRIBUTING.md)

## License

Licensed under the **Apache License 2.0**. See [LICENSE](https://github.com/logvik-org/ohsh/blob/main/LICENSE) and
[NOTICE](https://github.com/logvik-org/ohsh/blob/main/NOTICE).

## Author

**Ola Groettvik** - [GitHub](https://github.com/olagrottvik)

Contributions, issues, and suggestions are welcome!
