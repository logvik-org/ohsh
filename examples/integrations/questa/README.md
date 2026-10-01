# Questa / ModelSim

Status: **⚠️ not run in CI** (Questa / ModelSim, licensed software). Checked against the
vendor's command reference.

Generate the source lists from a shell in the example's directory, then run the
script with `vsim -c -do compile.do`.

## Simple: [`simple/compile.do`](simple/compile.do)

```bash
ohsh -t ../../../projects/simple -o build accumulator
```

The script compiles every file of `work_vhdl.src` into `work` with `vcom`, then
runs the testbench.

## Advanced: [`advanced/compile.do`](advanced/compile.do)

```bash
ohsh -t ../../../projects/advanced -w dsp_lib -o build accumulator
```

The script creates and maps each library with `vlib`/`vmap`, compiles it with
`vcom -work <library>` in the order of `libraries.src`, and runs the testbench
from `dsp_lib`.
