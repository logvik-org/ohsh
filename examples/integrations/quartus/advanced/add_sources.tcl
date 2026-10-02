# Altera Quartus, advanced project: add each library's files to a project, with
# the VHDL files assigned to their library.
#
# Generate the lists first (from a shell, in this directory):
#   ohsh -t ../../../projects/advanced -w dsp_lib -o build accumulator
# Then run:
#   quartus_sh -t add_sources.tcl
#
# Not run in CI (Quartus is licensed software). Checked against the Quartus
# Tcl and settings reference.

load_package flow

# Add every file from an ohsh .src list with the given assignment + library.
proc add_src {srcfile kind lib} {
    if {![file exists $srcfile]} { return }
    set fp [open $srcfile r]
    while {[gets $fp line] >= 0} {
        if {[string trim $line] eq ""} { continue }
        puts "Adding $line ($kind, lib=$lib)"
        switch -- $kind {
            vhdl { set_global_assignment -name VHDL_FILE $line -library $lib }
            systemverilog {
                if {[is_systemverilog_only $line]} {
                    set_global_assignment -name SYSTEMVERILOG_FILE $line
                } else {
                    set_global_assignment -name VERILOG_FILE $line
                }
            }
        }
    }
    close $fp
}

# The SystemVerilog list also holds plain Verilog (.v, .vh) files, which the
# tool should keep compiling as Verilog.
proc is_systemverilog_only {path} {
    return [expr {[string tolower [file extension $path]] in {.sv .svh .svp}}]
}

# Library names in the order ohsh wrote them to libraries.src.
proc read_library_order {path} {
    set fp [open $path r]
    set libraries [split [string trim [read $fp]] "\n"]
    close $fp
    return $libraries
}

project_new -overwrite demo
set_global_assignment -name TOP_LEVEL_ENTITY accumulator

foreach lib [read_library_order build/libraries.src] {
    add_src build/${lib}_vhdl.src          vhdl          $lib
    add_src build/${lib}_systemverilog.src systemverilog $lib
}

export_assignments
project_close
