# Vivado integration

Status: **⚠️ documented & validated against vendor docs** - not executed in CI
(Vivado is licensed proprietary software).

[`read_sources.tcl`](read_sources.tcl) loops over ohsh's `.src` lists and reads
each file in non-project (Tcl) mode:

```tcl
proc read_src {srcfile kind lib} { ... read_vhdl -library $lib $line ... }
read_src build/math_lib_vhdl.src vhdl    math_lib
read_src build/work_vhdl.src     vhdl    work
read_src build/work_verilog.src  verilog work
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
