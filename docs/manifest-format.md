# Manifest file format

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

- `module` (required) - the module's name. It must be unique across all
  manifests under `--top-dir`, otherwise ohsh stops with exit code 103 and
  lists the manifests that declare it.
- `sources` (optional) - list of HDL source files, relative to the manifest.
  Files ending in `.v`, `.sv`, `.svp`, `.vh` or `.svh` go to the SystemVerilog list,
  and `.vhd`, `.vhdl` or `.vo` to the VHDL list, regardless of case. Other files
  are skipped with a warning.
- `dependencies` (optional) - modules this one needs, as lists grouped by
  library. The special library `work` is remapped to whatever `--work` (or the
  resolving library) is.

## Does order matter?

<img class="mascot" src="_static/mascot-sorting.png" alt="The ohsh dog sorting files into a neat stack">

**`sources`: yes.** ohsh writes a module's files in the order the manifest lists
them, so list them in compile order. A VHDL package goes before the files that
use it, and a SystemVerilog header or package before the code that includes or
imports it.

**`dependencies`: no.** List the modules and libraries in any order. ohsh
always puts a module, and everything it depends on, before the modules that use
it, and puts each library before the libraries that use it. The listed order
only decides the order between modules that don't depend on each other.

In other words, ohsh orders *modules*, and you order the *files* inside each
module. When a module's files would need another module compiled in between
them, split it into two modules.

## Discovery and validation

ohsh reads every `manifest*.json` file under `--top-dir` and stops with exit
code 65 if one is not valid JSON or does not have this structure. Unknown keys
are ignored.
