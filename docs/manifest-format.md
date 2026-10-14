# Manifest file format

Each module gets a manifest file, usually `manifest.json`, next to its sources:

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

- `module` (required): the module's name. It must be unique across all
  manifests under `--top-dir`, otherwise ohsh stops with exit code 103 and
  lists the manifests that declare it.
- `sources` (optional): list of HDL source files, relative to the manifest.
  Files ending in `.v`, `.sv`, `.svp`, `.vh` or `.svh` go to the SystemVerilog list,
  and `.vhd`, `.vhdl` or `.vo` to the VHDL list, regardless of case. Other files
  are skipped with a warning.
- `source_lists` (optional): list of text files that list source files, one
  per line, relative to the list file. Blank lines and lines starting with `#`
  are skipped. Use it for a library that ships its own compile order, see
  [below](#libraries-that-ship-a-compile-order).
- `dependencies` (optional): modules this one needs, as lists grouped by
  library. The special library `work` is remapped to whatever `--work` (or the
  resolving library) is.

## Ordering

<img class="mascot" src="_static/mascot-sorting.png" alt="The ohsh dog sorting files into a neat stack">

The order of `sources` matters. ohsh writes a module's files in the order the
manifest lists them, so list them in compile order. A VHDL package goes before
the files that use it, and a SystemVerilog header or package before the code
that includes or imports it.

The order of `dependencies` does not. List the modules and libraries in any
order. ohsh always puts a module, and everything it depends on, before the
modules that use it, and puts each library before the libraries that use it. The
listed order only decides the order between modules that don't depend on each
other.

So ohsh orders the modules, and you order the files inside each module. When a
module's files would need another module compiled in between them, split it
into two modules.

## Libraries that ship a compile order

Some HDL libraries list their files in compile order in a text file, such as
the `compile_order.txt` of [Open Logic](https://github.com/open-logic/open-logic).
`source_lists` reads the sources from such a file instead of repeating them in
the manifest, so the manifest stays correct when the library is updated. The
manifest does not have to be in the library's directory: a library included as
a git submodule can get its manifest from your own repository.

```json
{
  "module": "open_logic",
  "source_lists": ["../../lib/open-logic/compile_order.txt"]
}
```

The files of the source lists come first, in the order they are listed, and
then the files of `sources`. `--fix` only sorts `sources` and leaves the order
of a source list alone.

Paths in `sources` and in source lists may start with `../` to point outside
the manifest's directory. ohsh writes them without the `..` parts.

## Discovery and validation

ohsh searches `--top-dir` and all its subdirectories for files named
`manifest*.json`. Any name that matches is read, so one directory can hold
several manifests, for example `manifest.json` for a module and
`manifest_tb.json` for its testbench. Each file still describes exactly one
module.

ohsh stops if a manifest is not valid JSON or does not have this structure.
Unknown keys are ignored.
