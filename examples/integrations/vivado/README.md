# Vivado integration

Status: **⚠️ documented & validated against vendor docs** - not executed in CI
(Vivado is licensed proprietary software).

[`read_sources.tcl`](read_sources.tcl) loops over the libraries in ohsh's
`libraries.src` and reads each library's files in non-project (Tcl) mode:

```tcl
proc read_src {srcfile kind lib} { ... read_vhdl -library $lib $line ... }
foreach lib [read_library_order build/libraries.src] {
    read_src build/${lib}_vhdl.src    vhdl    $lib
    read_src build/${lib}_verilog.src verilog $lib
}
```

Usage:

```bash
ohsh -t ../../demo_project -o build accumulator
vivado -mode batch -source read_sources.tcl
```

Notes:
- `read_vhdl -library <lib> <file>` places VHDL into a named library (UG835).
- Use `read_verilog -sv` for SystemVerilog. Verilog has no library namespace in
  Vivado synthesis, so it is read globally.

Docs: AMD Vivado Design Suite Tcl Command Reference (UG835).
