# GHDL

Status: **✅ both examples run in CI** (`.github/workflows/integration.yml`).

Run the examples with `./run.sh` in the example's directory. Both compile the
self-checking testbench [`tb_accumulator.vhd`](../../testbenches/tb_accumulator.vhd)
on top of the design, so a wrong file or library order fails the run.

## Simple: [`simple/run.sh`](simple/run.sh)

Every module is in the default `work` library, so the files are analyzed in the
order of `work_vhdl.src`:

```bash
ohsh -t ../../../projects/simple -o build accumulator
while IFS= read -r f; do ghdl -a --std=08 --workdir=build "$f"; done < build/work_vhdl.src
```

## Advanced: [`advanced/run.sh`](advanced/run.sh)

Three libraries, with the top library named `dsp_lib` by `-w`. Each library is
analyzed with `--work=<library>` in the order of `libraries.src`, and `-P`
lets later libraries find the earlier ones:

```bash
ohsh -t ../../../projects/advanced -w dsp_lib -o build accumulator
while IFS= read -r lib; do
  while IFS= read -r f; do
    ghdl -a --std=08 --workdir=build -Pbuild --work="$lib" "$f"
  done < "build/${lib}_vhdl.src"
done < build/libraries.src
```

The testbench is analyzed into `dsp_lib`, where `work.accumulator` resolves.

## Requirements

GHDL (CI uses the [`ghdl/setup-ghdl`](https://github.com/ghdl/setup-ghdl)
action). Docs: <https://ghdl.github.io/ghdl/using/InvokingGHDL.html>.
