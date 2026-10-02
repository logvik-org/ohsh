# cocotb Makefile flow, simple project: one SystemVerilog module on Icarus Verilog.
#
# ohsh writes the source lists while make reads this file, and VERILOG_SOURCES
# comes straight from the list for the `work` library.

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

EXAMPLES := $(abspath $(CURDIR)/../../..)
BUILD := $(CURDIR)/build

_ := $(shell ohsh -t $(EXAMPLES)/projects/simple -o $(BUILD) counter)
ifneq ($(.SHELLSTATUS),0)
$(error ohsh failed, see the message above)
endif

VERILOG_SOURCES := $(shell cat $(BUILD)/work_verilog.src)

COCOTB_TOPLEVEL := counter
COCOTB_TEST_MODULES := test_counter
export PYTHONPATH := $(EXAMPLES)/testbenches:$(PYTHONPATH)
SIM_BUILD := $(BUILD)/sim_build
COCOTB_RESULTS_FILE := $(BUILD)/results.xml

include $(shell cocotb-config --makefiles)/Makefile.sim
