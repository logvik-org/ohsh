# Example projects

Two small HDL projects that the [integration examples](../integrations) resolve
with ohsh. Both have the same VHDL `accumulator` and Verilog `counter`
interfaces, so the shared testbenches in [`../testbenches`](../testbenches)
work with either.

## [`simple/`](simple)

Every module is in one library, the default `work`.

| Module | Language | Depends on |
|---|---|---|
| `adder` | VHDL | |
| `accumulator` | VHDL | `adder` (`work`) |
| `counter` | Verilog | |

```bash
ohsh -t simple -o build accumulator
# build/libraries.src  -> work
# build/work_vhdl.src  -> adder.vhd accumulator.vhd
```

## [`advanced/`](advanced)

Modules spread over three libraries, the top one named with `-w`:

| Module | Language | Library | Depends on |
|---|---|---|---|
| `util_pkg` | VHDL package | `util_lib` | |
| `adder` | VHDL | `math_lib` | `util_pkg` (`util_lib`) |
| `acc_register` | VHDL | top library | |
| `accumulator` | VHDL | top library | `adder` (`math_lib`), `acc_register` (`work`) |
| `counter` | Verilog, with header `counter_defs.vh` | top library | |

The accumulator's manifest lists `acc_register` under `work`, which ohsh maps to
whatever library the accumulator itself is compiled into, here the one given
with `-w`.

```bash
ohsh -t advanced -w dsp_lib -o build accumulator
# build/libraries.src      -> util_lib math_lib dsp_lib
# build/util_lib_vhdl.src  -> util_pkg.vhd
# build/math_lib_vhdl.src  -> adder.vhd
# build/dsp_lib_vhdl.src   -> acc_register.vhd accumulator.vhd
```
