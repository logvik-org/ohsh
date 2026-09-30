# Questa / ModelSim integration

Status: **⚠️ documented & validated against vendor docs** - not executed in CI
(Questa/ModelSim is licensed proprietary software).

[`compile.do`](compile.do) reads ohsh's `.src` lists and compiles each file into
the right library with `vcom`/`vlog`, in the order listed in `libraries.src`:

```tcl
proc compile_src {srcfile lib lang} { ... vcom -2008 -work $lib $line ... }
foreach lib [read_library_order build/libraries.src] {
    vlib $lib
    vmap $lib $lib
    compile_src build/${lib}_vhdl.src    $lib vhdl
    compile_src build/${lib}_verilog.src $lib verilog
}
```

Usage:

```bash
ohsh -t ../../demo_project -o build accumulator
vsim -c -do compile.do
```

Key commands: `vlib`/`vmap` create and map libraries, `vcom -work <lib>`
compiles VHDL, `vlog [-sv] -work <lib>` compiles Verilog/SystemVerilog. Docs:
Questa SIM / ModelSim Command Reference.
