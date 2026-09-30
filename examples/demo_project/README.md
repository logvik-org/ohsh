# demo_project

A minimal HDL project used by all the [integration examples](../README.md). It
exists to give ohsh something realistic to resolve - multiple libraries and a
cross-library dependency.

```
demo_project/
├── math_lib/        # library: math_lib
│   ├── manifest.json    (module: adder)
│   └── adder.vhd
├── accumulator/     # library: work
│   ├── manifest.json    (module: accumulator, depends on math_lib.adder)
│   └── accumulator.vhd
└── verilog/         # library: work
    ├── manifest.json    (module: counter)
    └── counter.v
```

Resolve the VHDL design (top = `accumulator`):

```bash
ohsh -t . -o build accumulator
# build/math_lib_vhdl.src  -> adder.vhd
# build/work_vhdl.src      -> accumulator.vhd   (compiled after math_lib)
```

Resolve the Verilog design (top = `counter`):

```bash
ohsh -t . -o build counter
# build/work_verilog.src   -> counter.v
```

The testbenches live with each integration example, not here - ohsh provides the
*design* file lists, and each tool layers its own testbench on top.
