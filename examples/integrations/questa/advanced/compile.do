# Questa / ModelSim, advanced project: compile each library in the order ohsh
# writes to libraries.src, then run the testbench in the top library.
#
# Generate the lists first (from a shell, in this directory):
#   ohsh -t ../../../projects/advanced -w dsp_lib -o build accumulator
# Then run:
#   vsim -c -do compile.do
#
# Not run in CI (Questa / ModelSim is licensed software). Checked against
# the Questa / ModelSim command reference.

# Helper: compile every file listed in an ohsh .src file into <lib>.
proc compile_src {srcfile lib lang} {
    if {![file exists $srcfile]} { return }
    set fp [open $srcfile r]
    while {[gets $fp line] >= 0} {
        if {[string trim $line] eq ""} { continue }
        puts "Compiling $line into $lib"
        switch -- $lang {
            vhdl { vcom -2008 -work $lib $line }
            systemverilog {
                if {[is_systemverilog_only $line]} {
                    vlog -sv -work $lib $line
                } else {
                    vlog -work $lib $line
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

set libraries [read_library_order build/libraries.src]

# Create / map libraries.
foreach lib $libraries {
    vlib $lib
    vmap $lib $lib
}

foreach lib $libraries {
    compile_src build/${lib}_vhdl.src          $lib vhdl
    compile_src build/${lib}_systemverilog.src $lib systemverilog
}

# The testbench goes into the top library, where `work.accumulator` resolves.
vcom -2008 -work dsp_lib ../../../testbenches/tb_accumulator.vhd
vsim -c dsp_lib.tb_accumulator -do "run -all; quit -f"
