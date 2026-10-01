# cocotb Makefile flow, advanced project: VHDL in three libraries on NVC.
#
# ohsh writes libraries.src with the library compile order. The libraries before
# the top library go to VHDL_LIB_ORDER, each with its files in
# VHDL_SOURCES_<library>. The top library's files go to VHDL_SOURCES.
#
# This uses NVC because cocotb's GHDL makefile compiles the VHDL_SOURCES_<library>
# variables in no particular order, while its NVC makefile follows VHDL_LIB_ORDER.

SIM ?= nvc
TOPLEVEL_LANG ?= vhdl

EXAMPLES := $(abspath $(CURDIR)/../../..)
BUILD := $(CURDIR)/build
TOP_LIBRARY := dsp_lib

_ := $(shell ohsh -t $(EXAMPLES)/projects/advanced -w $(TOP_LIBRARY) -o $(BUILD) accumulator)
ifneq ($(.SHELLSTATUS),0)
$(error ohsh failed, see the message above)
endif

VHDL_LIB_ORDER := $(filter-out $(TOP_LIBRARY),$(shell cat $(BUILD)/libraries.src))
$(foreach lib,$(VHDL_LIB_ORDER),$(eval VHDL_SOURCES_$(lib) := $(shell cat $(BUILD)/$(lib)_vhdl.src)))
VHDL_SOURCES := $(shell cat $(BUILD)/$(TOP_LIBRARY)_vhdl.src)
TOPLEVEL_LIBRARY := $(TOP_LIBRARY)

COCOTB_TOPLEVEL := accumulator
COCOTB_TEST_MODULES := test_accumulator
export PYTHONPATH := $(EXAMPLES)/testbenches:$(PYTHONPATH)
SIM_BUILD := $(BUILD)/sim_build
COCOTB_RESULTS_FILE := $(BUILD)/results.xml

include $(shell cocotb-config --makefiles)/Makefile.sim
