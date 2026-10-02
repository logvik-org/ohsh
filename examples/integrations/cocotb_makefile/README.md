# cocotb, Makefile flow

Status: **✅ both examples run in CI** (`.github/workflows/integration.yml`).

In both examples, ohsh runs while make reads the Makefile, and the cocotb
variables are filled straight from its output. Run them with `make` in the
example's directory.

## Simple: [`simple/Makefile`](simple/Makefile)

The SystemVerilog `counter` from the simple project on Icarus Verilog. Its sources are
in the `work` library, so `VERILOG_SOURCES` is just `work_verilog.src`:

```make
_ := $(shell ohsh -t $(EXAMPLES)/projects/simple -o $(BUILD) counter)
VERILOG_SOURCES := $(shell cat $(BUILD)/work_verilog.src)
```

## Advanced: [`advanced/Makefile`](advanced/Makefile)

The VHDL `accumulator` from the advanced project, spread over `util_lib`,
`math_lib` and the top library `dsp_lib`, on NVC. `libraries.src` maps directly
onto cocotb's library variables: the libraries before the top one go to
`VHDL_LIB_ORDER` with their files in `VHDL_SOURCES_<library>`, and the top
library's files go to `VHDL_SOURCES`:

```make
VHDL_LIB_ORDER := $(filter-out $(TOP_LIBRARY),$(shell cat $(BUILD)/libraries.src))
$(foreach lib,$(VHDL_LIB_ORDER),$(eval VHDL_SOURCES_$(lib) := $(shell cat $(BUILD)/$(lib)_vhdl.src)))
VHDL_SOURCES := $(shell cat $(BUILD)/$(TOP_LIBRARY)_vhdl.src)
TOPLEVEL_LIBRARY := $(TOP_LIBRARY)
```

This uses NVC because cocotb's GHDL makefile compiles the
`VHDL_SOURCES_<library>` variables in no particular order, while its NVC
makefile follows `VHDL_LIB_ORDER`.

## Requirements

cocotb 2.x (`pip install -e ".[examples]"`), Icarus Verilog for the simple
example and NVC for the advanced one. The cocotb tests are in
[`../../testbenches`](../../testbenches). Docs:
<https://docs.cocotb.org/en/stable/building.html>.
