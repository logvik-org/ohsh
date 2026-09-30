# Questa / ModelSim integration

Status: **⚠️ documented & validated against vendor docs** - not executed in CI
(Questa/ModelSim is licensed proprietary software).

[`compile.do`](compile.do) reads ohsh's `.src` lists and compiles each file into
the right library with `vcom`/`vlog`, dependency libraries first:

```tcl
proc compile_src {srcfile lib lang} { ... vcom -2008 -work $lib $line ... }
vlib math_lib; vmap math_lib math_lib
compile_src build/math_lib_vhdl.src math_lib vhdl
compile_src build/work_vhdl.src     work     vhdl
```

Usage:

```bash
ohsh -t ../../demo_project -o build accumulator
vsim -c -do compile.do
```

Key commands: `vlib`/`vmap` create and map libraries, `vcom -work <lib>`
compiles VHDL, `vlog [-sv] -work <lib>` compiles Verilog/SystemVerilog. Docs:
Questa SIM / ModelSim Command Reference.
