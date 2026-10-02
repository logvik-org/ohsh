# Quartus

Status: **⚠️ not run in CI** (Quartus, licensed software). Checked against the
vendor's command reference.

Generate the source lists from a shell in the example's directory, then run the
script with `quartus_sh -t add_sources.tcl`.

## Simple: [`simple/add_sources.tcl`](simple/add_sources.tcl)

```bash
ohsh -t ../../../projects/simple -o build accumulator
```

The script adds every file of `work_vhdl.src` to a new project with
`set_global_assignment -name VHDL_FILE`.

## Advanced: [`advanced/add_sources.tcl`](advanced/add_sources.tcl)

```bash
ohsh -t ../../../projects/advanced -w dsp_lib -o build accumulator
```

The script adds each library's files with `-library <library>` on the
`VHDL_FILE` assignment, in the order of `libraries.src`.
