# SPDX-License-Identifier: Apache-2.0
#
# cocotb (Makefile flow) integration example.
#
# ohsh generates the source list at parse time; the Makefile reads it straight
# into VERILOG_SOURCES. Verified in CI against the demo project.

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

DEMO  := $(CURDIR)/../../demo_project
BUILD := $(CURDIR)/build

# Generate per-library .src lists with ohsh before reading them.
_ := $(shell mkdir -p $(BUILD) && ohsh -t $(DEMO) -o $(BUILD) counter >/dev/null 2>&1)

# Pull the ordered source list straight from ohsh output.
VERILOG_SOURCES := $(shell cat $(BUILD)/work_verilog.src)

COCOTB_TOPLEVEL := counter
COCOTB_TEST_MODULES := test_counter

include $(shell cocotb-config --makefiles)/Makefile.sim
