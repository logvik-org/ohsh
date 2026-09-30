# SPDX-License-Identifier: Apache-2.0
#
# Intel/Altera Quartus: add ohsh-generated source lists to a project.
#
# Generate the lists first:
#   ohsh -t ../../demo_project -o build accumulator
# Then run:
#   quartus_sh -t add_sources.tcl
#
# Status: validated against the Quartus Tcl / settings reference; not executed in
# CI (Quartus is licensed proprietary software).

load_package flow

# Add every file from an ohsh .src list with the given assignment + library.
proc add_src {srcfile kind lib} {
    if {![file exists $srcfile]} { return }
    set fp [open $srcfile r]
    while {[gets $fp line] >= 0} {
        if {[string trim $line] eq ""} { continue }
        puts "Adding $line ($kind, lib=$lib)"
        switch -- $kind {
            vhdl    { set_global_assignment -name VHDL_FILE $line -library $lib }
            verilog { set_global_assignment -name VERILOG_FILE $line }
            sv      { set_global_assignment -name SYSTEMVERILOG_FILE $line }
        }
    }
    close $fp
}

project_new -overwrite demo
set_global_assignment -name TOP_LEVEL_ENTITY accumulator

add_src build/math_lib_vhdl.src vhdl    math_lib
add_src build/work_vhdl.src     vhdl    work
add_src build/work_verilog.src  verilog work

export_assignments
project_close
