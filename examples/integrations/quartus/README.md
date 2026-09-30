# Quartus integration

Status: **⚠️ documented & validated against vendor docs** - not executed in CI
(Quartus is licensed proprietary software).

[`add_sources.tcl`](add_sources.tcl) reads ohsh's `.src` lists and adds each file
to the project with `set_global_assignment`:

```tcl
proc add_src {srcfile kind lib} {
    ... set_global_assignment -name VHDL_FILE $line -library $lib ...
}
add_src build/math_lib_vhdl.src vhdl    math_lib
add_src build/work_vhdl.src     vhdl    work
add_src build/work_verilog.src  verilog work
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
