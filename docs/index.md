# ohsh

<p align="center">
  <img class="only-light" alt="ohsh: a humble HDL source handler" src="_static/logo-light.png" width="600">
  <img class="only-dark" alt="ohsh: a humble HDL source handler" src="_static/logo-dark.png" width="600">
</p>

**ohsh** is a humble command-line tool that works out which HDL source files
(SystemVerilog and VHDL) a design needs and in what order to compile them. Each
module gets a `manifest.json` that lists its sources and the modules it depends
on. ohsh reads the manifests and writes plain `.src` file lists, one per
library and language.

ohsh works alongside build flows such as [hog](https://hog.readthedocs.io),
Vivado, Quartus, Questa, cocotb and VUnit. It does not run simulators, manage
tool projects or parse your HDL.

```bash
pip install ohsh
ohsh my_top_module
```

## Why ohsh

**One description for every tool.** The same manifests feed your cocotb testbenches, your VUnit runs and your Vivado
or Quartus build. A new dependency is added once, in one manifest, instead of in
every tool's file list.

**Compile only what the design or the testbench needs.** Give each testbench its
own manifest and ohsh lists only the files under it.

**Third-party code stays untouched.** Vendor IP and libraries pulled in as git submodules don't need to know about
ohsh. A manifest next to the submodule lists the files you use, in their own
library, and every module that needs them names that library.

**Manifests don't have to be written by hand.** ohsh can read the HDL sources
and [create, fix and check the manifests](manifest-actions.md) for you. This is
best effort, so review what it writes.

## Documentation

- [Getting started](getting-started.md): install ohsh, write manifests, add
  third-party libraries and compile the result.
- [Manifest file format](manifest-format.md): every field of a manifest, and
  what order things go in.
- [Create, fix and check manifests](manifest-actions.md): let ohsh create manifests
  for an existing source tree, and keep them in line with the sources.
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
manifest-actions
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
