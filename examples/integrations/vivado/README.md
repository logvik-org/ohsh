# Vivado

Status: **⚠️ not run in CI** (Vivado, licensed software). Checked against the
vendor's command reference.

Generate the source lists from a shell in the example's directory, then run the
script with `vivado -mode batch -source read_sources.tcl`.

## Simple: [`simple/read_sources.tcl`](simple/read_sources.tcl)

```bash
ohsh -t ../../../projects/simple -o build accumulator
```

The script reads every file of `work_vhdl.src` with `read_vhdl` in non-project mode.

## Advanced: [`advanced/read_sources.tcl`](advanced/read_sources.tcl)

```bash
ohsh -t ../../../projects/advanced -w dsp_lib -o build accumulator
```

The script reads each library's files with `read_vhdl -library <library>` in
the order of `libraries.src`. Verilog has no libraries in Vivado synthesis, so
any Verilog files are read globally.
