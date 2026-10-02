# ohsh

**ohsh** is a small command-line tool that works out which HDL source files your
design needs, and in which order to compile them. You describe each module in a
short `manifest.json` next to its sources. ohsh follows the dependencies from
your top module and writes plain `.src` lists, one per library and language,
plus the order to compile the libraries in. Those lists drop into any simulator
or build flow.

```bash
pip install ohsh
ohsh my_top_module
```

- [Getting started](getting-started.md): install ohsh, write manifests and
  compile the result.
- [Why ohsh](why-ohsh.md): the problem ohsh solves and where it fits next to
  the tools you already use.
- [Manifest file format](manifest-format.md): every field of a manifest.
- [Integrations](integrations.md): runnable examples for simulators and build
  tools.
- [Exit codes](exit-codes.md): what each exit code means.

```{toctree}
:hidden:
:caption: User guide

getting-started
why-ohsh
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
