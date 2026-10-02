# ohsh

<p align="center">
  <img class="only-light" alt="ohsh: a humble HDL source handler" src="_static/logo-light.png" width="600">
  <img class="only-dark" alt="ohsh: a humble HDL source handler" src="_static/logo-dark.png" width="600">
</p>

**ohsh** is a small, deliberately humble command-line tool that figures out, in
the right order, which HDL (SystemVerilog and VHDL) source files your
design needs - by reading simple per-module `manifest.json` files and resolving
their dependencies.

It is a *companion* to the big build flows (like [hog](https://hog.readthedocs.io),
Vivado, Quartus, Questa, cocotb, VUnit, …), not a replacement for them. ohsh
just answers one question well - *"what files, in what order, for which
libraries?"* - and hands you plain `.src` lists you can feed anywhere.

```bash
pip install ohsh
ohsh my_top_module
```

## Why ohsh

**One description for every tool.** The same manifests feed your cocotb
testbenches, your VUnit runs and your Vivado or Quartus build. A new dependency
is added once, in one manifest, instead of in every tool's file list.

**Compile only what a testbench needs.** Give each testbench its own manifest
and ohsh lists just the files under it, not the whole project. In one FPGA
project with about 1100 HDL files, a unit testbench compiles 35 of them and the
full design 165.

**Third-party code stays untouched.** Vendor IP and libraries pulled in as git
submodules don't need to know about ohsh. A manifest next to the submodule lists
the files you use, in their own library, and every module that needs them
names that library.

ohsh does not run simulators, manage tool projects or parse your HDL. It hands
those tools the file lists and leaves the rest to them.

## Documentation

- [Getting started](getting-started.md): install ohsh, write manifests, add
  third-party libraries and compile the result.
- [Manifest file format](manifest-format.md): every field of a manifest, and
  what order things go in.
- [Integrations](integrations.md): runnable examples for simulators and build
  tools.
- [Exit codes](exit-codes.md): what each exit code means.

<div class="mascot-strip">
  <figure><img src="_static/mascot-unsorted.png" alt="The ohsh dog surrounded by scattered source files"><figcaption>Your files</figcaption></figure>
  <figure><img src="_static/mascot-sorting.png" alt="The dog sorting files into a neat stack"><figcaption>ohsh</figcaption></figure>
  <figure><img src="_static/mascot-sorted.png" alt="The dog resting next to an ordered, checked list"><figcaption>In order</figcaption></figure>
</div>

```{toctree}
:hidden:

Home <self>
```

```{toctree}
:hidden:
:caption: User guide

getting-started
manifest-format
integrations
exit-codes
```

```{toctree}
:hidden:
:caption: Project

Changelog <https://github.com/logvik-org/ohsh/blob/main/CHANGELOG.md>
Contributing <https://github.com/logvik-org/ohsh/blob/main/CONTRIBUTING.md>
GitHub <https://github.com/logvik-org/ohsh>
PyPI <https://pypi.org/project/ohsh/>
```
