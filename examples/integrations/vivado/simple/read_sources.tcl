# AMD Vivado, simple project: read every file into the default library in
# non-project mode.
#
# Generate the list first (from a shell, in this directory):
#   ohsh -t ../../../projects/simple -o build accumulator
# Then run:
#   vivado -mode batch -source read_sources.tcl
#
# Not run in CI (Vivado is licensed software). Checked against the Vivado
# Tcl command reference (UG835).

set fp [open build/work_vhdl.src r]
foreach file [split [string trim [read $fp]] "\n"] {
    read_vhdl $file
}
close $fp

# Continue with synthesis, for example:
#   synth_design -top accumulator -part <your part>
