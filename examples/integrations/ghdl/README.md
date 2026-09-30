# GHDL integration

Status: **✅ verified in CI** (`.github/workflows/integration.yml`).

[`run.sh`](run.sh):

1. Runs `ohsh` on the [demo project](../../demo_project) to produce
   `libraries.src`, `math_lib_vhdl.src` and `work_vhdl.src`.
2. Analyzes each library with `ghdl -a --work=<lib>`, in the order listed in
   `libraries.src` (`math_lib`, then `work`), using `-P<builddir>` so `work`
   can find `math_lib`.
3. Compiles the self-checking [`tb_accumulator.vhd`](tb_accumulator.vhd),
   then elaborates and runs it.

```bash
./run.sh
```

The testbench drives the accumulator and asserts the running total, ending with
`std.env.finish`. A wrong file/library order would fail analysis, so a green run
proves the ohsh-generated lists are correct.

Requires `ghdl` (`apt-get install ghdl`, or the
[`ghdl/setup-ghdl`](https://github.com/ghdl/setup-ghdl) action). Docs:
<https://ghdl.github.io/ghdl/using/InvokingGHDL.html>.
