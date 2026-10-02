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

ohsh reads every `manifest*.json` file under `--top-dir` and stops with exit
code 65 if one is not valid JSON or does not have this structure. Unknown keys
are ignored.
