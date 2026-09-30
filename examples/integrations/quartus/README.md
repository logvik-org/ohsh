# Quartus integration

Status: **⚠️ documented & validated against vendor docs** - not executed in CI
(Quartus is licensed proprietary software).

[`add_sources.tcl`](add_sources.tcl) loops over the libraries in ohsh's
`libraries.src` and adds each library's files to the project with
`set_global_assignment`:

```tcl
proc add_src {srcfile kind lib} {
    ... set_global_assignment -name VHDL_FILE $line -library $lib ...
}
foreach lib [read_library_order build/libraries.src] {
    add_src build/${lib}_vhdl.src    vhdl    $lib
    add_src build/${lib}_verilog.src verilog $lib
}
```

Usage:

```bash
ohsh -t ../../demo_project -o build accumulator
quartus_sh -t add_sources.tcl
```

Notes:
- File assignments: `VHDL_FILE`, `VERILOG_FILE`, `SYSTEMVERILOG_FILE`.
- `-library <lib>` on a `VHDL_FILE` assignment places it in that VHDL library.

Docs: Intel Quartus Prime Scripting / Settings reference.
