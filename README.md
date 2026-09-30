<!-- SPDX-License-Identifier: Apache-2.0 -->
# ohsh - Ola's HDL Source Handler

[![CI](https://github.com/logvik-org/oshsh/actions/workflows/ci.yml/badge.svg)](https://github.com/logvik-org/oshsh/actions/workflows/ci.yml)
[![Integrations](https://github.com/logvik-org/oshsh/actions/workflows/integration.yml/badge.svg)](https://github.com/logvik-org/oshsh/actions/workflows/integration.yml)
[![PyPI](https://img.shields.io/pypi/v/ohsh.svg)](https://pypi.org/project/ohsh/)
[![Python](https://img.shields.io/pypi/pyversions/ohsh.svg)](https://pypi.org/project/ohsh/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

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
git clone https://github.com/logvik-org/oshsh.git
cd oshsh
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
| `-w`, `--work`      | Name of the work library.                                              | `work`       |
| `-o`, `--output`    | Output directory for the `.src` lists.                                 | cwd          |
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

## Manifest file format

Each module gets a `manifest.json` next to its sources:

```json
{
  "module": "alu",
  "sources": [
    "alu_core.v",
    "alu_control.vhd"
  ],
  "dependencies": {
    "work": ["adder", "multiplier"],
    "math_lib": ["sqrt_module"]
  }
}
```

- `module` - the module's name.
- `sources` - HDL source files, relative to the manifest.
- `dependencies` - modules this one needs, grouped by library. The special
  library `work` is remapped to whatever `--work` (or the resolving library) is.

## Integrations

ohsh's `.src` lists are just text - one absolute path per line - so they drop
into almost any flow. Runnable, self-checking examples live in
[`examples/`](examples/). The ones marked ✅ are **executed in CI** against a
demo project; the vendor-tool ones (⚠️) are validated against official docs but
can't run on a public CI runner.

| Tool | Example | Verified |
|------|---------|----------|
| [cocotb (Makefile)](examples/integrations/cocotb_makefile/) | `Makefile` | ✅ CI |
| [cocotb (Python runner)](examples/integrations/cocotb_runner/) | `runner.py` | ✅ CI |
| [VUnit](examples/integrations/vunit/) | `run.py` | ✅ CI |
| [GHDL](examples/integrations/ghdl/) | `run.sh` | ✅ CI |
| [NVC](examples/integrations/nvc/) | `run.sh` | ✅ CI |
| [UVVM](examples/integrations/uvvm/) | `run.sh` | ✅ CI |
| [hog](examples/integrations/hog/) | `README.md` | doc |
| [Questa / ModelSim](examples/integrations/questa/) | `compile.do` | ⚠️ doc |
| [Vivado](examples/integrations/vivado/) | `read_sources.tcl` | ⚠️ doc |
| [Quartus](examples/integrations/quartus/) | `add_sources.tcl` | ⚠️ doc |

For example, feeding ohsh output to GHDL:

```bash
ohsh -t my_project -o build top
while IFS= read -r lib; do
  [ -f "build/${lib}_vhdl.src" ] || continue
  while IFS= read -r f; do ghdl -a --work="$lib" --std=08 "$f"; done < "build/${lib}_vhdl.src"
done < build/libraries.src
ghdl -e --std=08 top && ghdl -r --std=08 top
```

## Development

```bash
git clone https://github.com/logvik-org/oshsh.git
cd oshsh
./scripts/setup-dev.sh   # or: make dev
make test                # run tests with coverage
make lint                # ruff lint + format check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

Licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) and
[NOTICE](NOTICE).

## Author

**Ola Groettvik** - [GitHub](https://github.com/olagrottvik)

Contributions, issues, and suggestions are welcome!
