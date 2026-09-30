# SPDX-License-Identifier: Apache-2.0
#
# Questa / ModelSim do-file: compile ohsh-generated source lists into libraries,
# dependency libraries first, then run the testbench.
#
# Generate the lists first (from a shell):
#   ohsh -t ../../demo_project -o build accumulator
# Then run:
#   vsim -c -do compile.do
#
# Status: validated against the Questa/ModelSim command reference; not executed
# in CI (Questa is licensed proprietary software).

# Helper: compile every file listed in an ohsh .src file into <lib>.
proc compile_src {srcfile lib lang} {
    if {![file exists $srcfile]} { return }
    set fp [open $srcfile r]
    while {[gets $fp line] >= 0} {
        if {[string trim $line] eq ""} { continue }
        puts "Compiling $line into $lib"
        switch -- $lang {
            vhdl    { vcom -2008 -work $lib $line }
            verilog { vlog -work $lib $line }
            sv      { vlog -sv -work $lib $line }
        }
    }
    close $fp
}

# Create / map libraries.
foreach lib {math_lib work} {
    vlib $lib
    vmap $lib $lib
}

# Compile dependency libraries before work.
compile_src build/math_lib_vhdl.src    math_lib vhdl
compile_src build/work_vhdl.src        work     vhdl
compile_src build/work_verilog.src     work     verilog

# Compile a testbench and simulate (adjust the top to taste).
# vcom -2008 -work work ../ghdl/tb_accumulator.vhd
# vsim -c work.tb_accumulator -do "run -all; quit -f"
