# UVVM

Status: **✅ both examples run in CI** (`.github/workflows/integration.yml`).

[UVVM](https://github.com/UVVM/UVVM) testbenches on GHDL. ohsh supplies the
design's file lists, and UVVM's `uvvm_util` library and the testbench
[`tb_accumulator_uvvm.vhd`](../../testbenches/tb_accumulator_uvvm.vhd) are
compiled alongside it. Run the examples with `./run.sh` in the example's
directory.

Both examples first compile `uvvm_util` in the order of UVVM's own
`compile_order.txt`. UVVM is cloned once into `uvvm/build/UVVM` and shared:

```bash
./run.sh                           # clones UVVM 2026.03.20 on first use
UVVM_VERSION=2026.02.14 ./run.sh   # clone a different UVVM release
UVVM_ROOT=/path/to/UVVM ./run.sh   # use an existing checkout
```

GHDL needs `-fsynopsys -frelaxed` to compile UVVM. The same flags are used for
the design and testbench, so all libraries are compatible.

## Simple: [`simple/run.sh`](simple/run.sh)

The design is analyzed into the default `work` library from `work_vhdl.src`.

## Advanced: [`advanced/run.sh`](advanced/run.sh)

The design's three libraries are analyzed in the order of `libraries.src`, as in
the [advanced GHDL example](../ghdl), and the testbench goes into the top
library `dsp_lib`.

## Requirements

GHDL and git. Docs: <https://uvvm.github.io/>.
