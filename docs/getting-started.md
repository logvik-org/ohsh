# Getting started

This page takes you from installing ohsh to compiling its output with a
simulator. It uses a three-module project, the same one the
[examples](https://github.com/logvik-org/ohsh/tree/main/examples/projects/simple)
use.

## Install

ohsh needs Python 3.9 or newer and has no other dependencies.

```bash
pip install ohsh
ohsh --version
```

## Describe your modules

Give every module a `manifest.json` next to its sources. A manifest names the
module, lists its source files (relative to the manifest), and lists the modules
it uses, grouped by library:

```
project/
├── accumulator/
│   ├── accumulator.vhd
│   └── manifest.json
├── adder/
│   ├── adder.vhd
│   └── manifest.json
└── counter/
    ├── counter.v
    └── manifest.json
```

`accumulator/manifest.json` says that the accumulator uses the adder:

```json
{
  "module": "accumulator",
  "sources": ["accumulator.vhd"],
  "dependencies": {
    "work": ["adder"]
  }
}
```

`adder/manifest.json` and `counter/manifest.json` have no dependencies:

```json
{
  "module": "adder",
  "sources": ["adder.vhd"]
}
```

```json
{
  "module": "counter",
  "sources": ["counter.v"]
}
```

`work` means "the same library as the module that uses it". The
[manifest format](manifest-format.md) page has every field.

## Run ohsh

Run ohsh from the project directory with the name of your top module:

```bash
cd project
ohsh accumulator
```

ohsh is quiet when everything works. It finds every `manifest*.json` under the
current directory, follows the dependencies of `accumulator`, and writes two
files:

`work_vhdl.src`, the VHDL sources of library `work` in compile order, as
absolute paths:

```
/path/to/project/adder/adder.vhd
/path/to/project/accumulator/accumulator.vhd
```

`libraries.src`, the libraries to compile, in order:

```
work
```

The adder comes before the accumulator because the accumulator needs it. The
counter is left out because nothing under `accumulator` uses it. Run
`ohsh counter` to get it, in `work_systemverilog.src`.

Three options cover most uses:

- `-t DIR` searches for manifests under `DIR` instead of the current directory.
- `-o DIR` writes the lists to `DIR`, creating it if needed.
- `-v` prints what ohsh found and wrote. `-vv` adds debug details.

So `ohsh -t project -o build accumulator` does the same from anywhere and keeps
the output in `build/`.

## Compile the result

Each line of a `.src` file is one path, so a shell loop is enough to feed them
to a tool. With [GHDL](https://github.com/ghdl/ghdl):

```bash
ohsh -t project -o build accumulator
while IFS= read -r f; do ghdl -a --std=08 "$f"; done < build/work_vhdl.src
ghdl -e --std=08 accumulator
```

The [integrations](integrations.md) page has runnable examples for cocotb,
VUnit, GHDL, NVC, UVVM, hog, Questa, Vivado and Quartus.

## More than one library

Larger designs usually spread modules over several libraries. List each
dependency under its library, and use `-w` to choose the library of the top
module. In the
[advanced example](https://github.com/logvik-org/ohsh/tree/main/examples/projects/advanced),
the accumulator uses an adder in `math_lib`, which uses a package in `util_lib`:

```bash
ohsh -t advanced -w dsp_lib -o build accumulator
```

ohsh then writes one list per library, and `libraries.src` gives the order to
compile them in, each library after the ones it uses:

```
util_lib
math_lib
dsp_lib
```

Loop over `libraries.src` and compile each library's lists in turn. The
[integrations](integrations.md) page shows this for GHDL.

## When something is wrong

ohsh stops with a message and a specific exit code when a manifest is broken, a
module is missing, a module name is used twice, or modules depend on each other
in a loop:

```
$ ohsh nosuch
ohsh - ERROR - The specified module nosuch was not found in any manifest.
$ echo $?
100
```

Scripts and CI jobs can check the code. The [exit codes](exit-codes.md) page
lists them all.
