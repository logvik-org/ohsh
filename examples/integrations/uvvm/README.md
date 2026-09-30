# UVVM integration

Status: **✅ verified in CI** (`.github/workflows/integration.yml`, GHDL backend).

[`run.sh`](run.sh):

1. Obtains [UVVM](https://github.com/UVVM/UVVM) (clones release `$UVVM_VERSION`,
   default `2026.03.20`, or uses `$UVVM_ROOT`)
   and compiles `uvvm_util` into its own library, following UVVM's own
   `uvvm_util/script/compile_order.txt`.
2. Runs `ohsh` on the [demo project](../../demo_project) and compiles the design
   libraries in the order listed in `libraries.src` (`math_lib`, then `work`).
3. Compiles and runs the UVVM testbench
   ([`tb_accumulator_uvvm.vhd`](tb_accumulator_uvvm.vhd)), which uses
   `uvvm_util` `log()` / `check_value()` and ends with an alert summary.

```bash
./run.sh                       # clones UVVM 2026.03.20 into build/
UVVM_VERSION=2026.02.14 ./run.sh   # clone a different UVVM release
UVVM_ROOT=/path/to/UVVM ./run.sh   # reuse an existing checkout
```

Notes:
- GHDL needs `-fsynopsys -frelaxed` to compile UVVM; the same flags are used for
  the design and testbench so the libraries are compatible.
- The point of the example is that ohsh supplies the *design* file list; UVVM and
  the testbench layer on top.

Requires `ghdl`. Docs: <https://uvvm.github.io/>.
