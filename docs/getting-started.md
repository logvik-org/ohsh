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

## Third-party libraries

ohsh is most useful once a design pulls in code from elsewhere: vendor IP,
libraries from other groups, open-source cores. Keep such code exactly as it
comes, for example as a git submodule, and put a manifest *next to* it instead
of inside it. The manifest's paths point into the submodule and list the files
you use, in compile order:

```
project/
├── submodules/
│   ├── ipbus-firmware/          # git submodule, never edited
│   └── manifest_ipbus.json
└── slow_control/
    ├── slow_control.vhd
    └── manifest.json
```

`submodules/manifest_ipbus.json`:

```json
{
  "module": "ipbus",
  "sources": [
    "ipbus-firmware/components/ipbus_core/firmware/hdl/ipbus_package.vhd",
    "ipbus-firmware/components/ipbus_util/firmware/hdl/ipbus_addr_decode.vhd",
    "ipbus-firmware/components/ipbus_core/firmware/hdl/ipbus_fabric.vhd"
  ]
}
```

Modules that need it name the library to compile it into, here `ipbus`:

```json
{
  "module": "slow_control",
  "sources": ["slow_control.vhd"],
  "dependencies": {
    "ipbus": ["ipbus"]
  }
}
```

ohsh writes the third-party files to `ipbus_vhdl.src`, and `libraries.src` puts
`ipbus` before the libraries that use it. Updating the submodule only means
updating the one manifest next to it, and only if its file list changed.

## One manifest per testbench

A testbench is a module like any other. Give it a manifest with its own sources
and the modules it tests, and run ohsh with its name:

```json
{
  "module": "slow_control_tb",
  "sources": ["slow_control_tb.vhd"],
  "dependencies": {
    "work": ["slow_control"]
  }
}
```

```bash
ohsh -t ../.. slow_control_tb
```

The lists then hold only the files that testbench needs, so the simulator
compiles a few dozen files instead of the whole project. In one FPGA project
with about 1100 HDL files, most of them in third-party submodules, a unit
testbench compiles 35 files while the full design compiles 165. The full design
is just another module, so the synthesis flow uses the same manifests.

A common setup is a small Makefile next to each testbench that runs ohsh before
the simulator. See the [cocotb Makefile example](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/cocotb_makefile).
