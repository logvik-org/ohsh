# cocotb - Python runner flow

Status: **✅ verified in CI** (`.github/workflows/integration.yml`).

[`runner.py`](runner.py) uses cocotb's Python runner API (cocotb ≥ 2.0). It runs
`ohsh`, reads the `.src` list, and passes it to `runner.build(sources=...)`:

```python
from cocotb_tools.runner import get_results, get_runner

sources = read_src(BUILD / "work_verilog.src")  # from ohsh
runner = get_runner("icarus")
runner.build(sources=sources, hdl_toplevel="counter", timescale=("1ns", "1ps"), always=True)
results = runner.test(hdl_toplevel="counter", test_module="test_counter")
```

Run it:

```bash
python runner.py
```

Notes:
- The language-agnostic `sources=` parameter is the cocotb 2.0 way (the older
  `verilog_sources=` / `vhdl_sources=` are deprecated).
- A `timescale` is set because Icarus otherwise can't represent a 10 ns clock.
- `get_results()` is used to fail the script if any test fails.

Requires cocotb (`pip install -e ".[examples]"`) and Icarus Verilog
(`apt-get install iverilog`).

Docs: <https://docs.cocotb.org/en/stable/runner.html>.
