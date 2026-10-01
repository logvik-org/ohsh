# Questa / ModelSim do-file: compile ohsh-generated source lists into libraries,
# in the order ohsh writes to libraries.src, then run the testbench.
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

# Library names in the order ohsh wrote them to libraries.src.
proc read_library_order {path} {
    set fp [open $path r]
    set libraries [split [string trim [read $fp]] "\n"]
    close $fp
    return $libraries
}

set libraries [read_library_order build/libraries.src]

# Create / map libraries.
foreach lib $libraries {
    vlib $lib
    vmap $lib $lib
}

foreach lib $libraries {
    compile_src build/${lib}_vhdl.src    $lib vhdl
    compile_src build/${lib}_verilog.src $lib verilog
}

# Compile a testbench and simulate (adjust the top to taste).
# vcom -2008 -work work ../ghdl/tb_accumulator.vhd
# vsim -c work.tb_accumulator -do "run -all; quit -f"
