# cocotb, Python runner

Status: **✅ both examples run in CI** (`.github/workflows/integration.yml`).

Both examples use cocotb's Python runner API (`cocotb_tools.runner`, cocotb 2.x)
and run ohsh as `python -m ohsh`, so they work with whatever Python runs them.
Run them with `python runner.py` in the example's directory.

## Simple: [`simple/runner.py`](simple/runner.py)

The Verilog `counter` from the simple project on Icarus Verilog:

```python
sources = read_src(BUILD / "work_verilog.src")
runner = get_runner("icarus")
runner.build(sources=sources, hdl_toplevel="counter", timescale=("1ns", "1ps"), always=True)
runner.test(hdl_toplevel="counter", test_module="test_counter")
```

## Advanced: [`advanced/runner.py`](advanced/runner.py)

Two runs on the advanced project:

1. The VHDL `accumulator` on NVC. Each library is built with its own
   `runner.build(hdl_library=...)` call, in the order of `libraries.src`, and
   the test names the top library:

   ```python
   for library in read_src(build / "libraries.src"):
       runner.build(hdl_library=library, sources=read_src(build / f"{library}_vhdl.src"), ...)
   runner.test(hdl_toplevel="accumulator", hdl_toplevel_library="dsp_lib", ...)
   ```

2. The Verilog `counter`, whose settings come from the header `counter_defs.vh`,
   on Icarus Verilog. The header is listed in the manifest before `counter.v`,
   so it comes first in `work_verilog.src`.

## Requirements

cocotb 2.x (`pip install -e ".[examples]"`), Icarus Verilog, and NVC for the
advanced example. The cocotb tests are in [`../../testbenches`](../../testbenches).
Docs: <https://docs.cocotb.org/en/stable/runner.html>.
