# cocotb - Makefile flow

Status: **✅ verified in CI** (`.github/workflows/integration.yml`).

The [`Makefile`](Makefile) runs `ohsh` at parse time and reads the resulting
list straight into cocotb's `VERILOG_SOURCES`:

```makefile
_ := $(shell mkdir -p $(BUILD) && ohsh -t $(DEMO) -o $(BUILD) counter >/dev/null 2>&1)
VERILOG_SOURCES := $(shell cat $(BUILD)/work_verilog.src)
COCOTB_TOPLEVEL := counter
COCOTB_TEST_MODULES := test_counter
include $(shell cocotb-config --makefiles)/Makefile.sim
```

Run it:

```bash
make            # SIM defaults to icarus
make SIM=questa # or any other supported simulator
```

[`test_counter.py`](test_counter.py) is a small self-checking cocotb test.

Requires cocotb (`pip install -e ".[examples]"`) and a simulator - CI uses Icarus
Verilog (`apt-get install iverilog`). Variable names target **cocotb 2.x**
(`COCOTB_TOPLEVEL`, `COCOTB_TEST_MODULES`). Docs:
<https://docs.cocotb.org/en/stable/building.html>.
