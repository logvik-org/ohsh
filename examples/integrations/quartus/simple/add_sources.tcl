# Altera Quartus, simple project: add every file to a project in the default
# library.
#
# Generate the list first (from a shell, in this directory):
#   ohsh -t ../../../projects/simple -o build accumulator
# Then run:
#   quartus_sh -t add_sources.tcl
#
# Not run in CI (Quartus is licensed software). Checked against the Quartus
# Tcl and settings reference.

load_package flow

project_new -overwrite demo
set_global_assignment -name TOP_LEVEL_ENTITY accumulator

set fp [open build/work_vhdl.src r]
foreach file [split [string trim [read $fp]] "\n"] {
    set_global_assignment -name VHDL_FILE $file
}
close $fp

export_assignments
project_close
