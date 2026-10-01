# Questa / ModelSim, simple project: every module in the default `work` library.
#
# Generate the list first (from a shell, in this directory):
#   ohsh -t ../../../projects/simple -o build accumulator
# Then run:
#   vsim -c -do compile.do
#
# Not run in CI (Questa / ModelSim is licensed software). Checked against
# the Questa / ModelSim command reference.

vlib work
vmap work work

set fp [open build/work_vhdl.src r]
foreach file [split [string trim [read $fp]] "\n"] {
    vcom -2008 -work work $file
}
close $fp

vcom -2008 -work work ../../../testbenches/tb_accumulator.vhd
vsim -c work.tb_accumulator -do "run -all; quit -f"
