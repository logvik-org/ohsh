# VUnit

Status: **✅ both examples run in CI** (`.github/workflows/integration.yml`).

VUnit works out the compile order from the files itself, so here ohsh's job is
to say which files belong to which library. Both examples add the testbench
[`tb_accumulator_vunit.vhd`](../../testbenches/tb_accumulator_vunit.vhd) to the
same library as the design. Run them with `python run.py` in the example's
directory (`VUNIT_SIMULATOR=ghdl` in CI).

VUnit reserves the library name `work`, so ohsh is always run with `-w` to give
the top library another name.

## Simple: [`simple/run.py`](simple/run.py)

```python
dut_lib = vu.add_library("dut_lib")
dut_lib.add_source_files(read_src(BUILD / "dut_lib_vhdl.src"))
dut_lib.add_source_files(TESTBENCH)
```

## Advanced: [`advanced/run.py`](advanced/run.py)

One VUnit library per line of `libraries.src`:

```python
for library in read_src(BUILD / "libraries.src"):
    vu.add_library(library).add_source_files(read_src(BUILD / f"{library}_vhdl.src"))
vu.library("dsp_lib").add_source_files(TESTBENCH)
```

## Requirements

VUnit (`pip install -e ".[examples]"`) and a simulator (GHDL in CI). Both
examples use VUnit's current API: `VUnit.from_argv(compile_builtins=False)`
followed by `add_vhdl_builtins()`. Docs: <https://vunit.github.io/py/ui.html>.
