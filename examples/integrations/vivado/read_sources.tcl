# SPDX-License-Identifier: Apache-2.0
#
# AMD/Xilinx Vivado: read ohsh-generated source lists in non-project (Tcl) mode.
#
# Generate the lists first:
#   ohsh -t ../../demo_project -o build accumulator
# Then run:
#   vivado -mode batch -source read_sources.tcl
#
# Status: validated against the Vivado Tcl command reference (UG835); not
# executed in CI (Vivado is licensed proprietary software).

# Read every file from an ohsh .src list with the given command/library.
proc read_src {srcfile kind lib} {
    if {![file exists $srcfile]} { return }
    set fp [open $srcfile r]
    while {[gets $fp line] >= 0} {
        if {[string trim $line] eq ""} { continue }
        puts "Reading $line ($kind, lib=$lib)"
        switch -- $kind {
            vhdl    { read_vhdl -library $lib $line }
            verilog { read_verilog $line }
            sv      { read_verilog -sv $line }
        }
    }
    close $fp
}

# VHDL into named libraries (dependency libraries first); Verilog is global.
read_src build/math_lib_vhdl.src vhdl    math_lib
read_src build/work_vhdl.src     vhdl    work
read_src build/work_verilog.src  verilog work

# Example continuation:
# synth_design -top accumulator
