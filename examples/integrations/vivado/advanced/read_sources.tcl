# AMD Vivado, advanced project: read each library's files in non-project mode,
# in the order ohsh writes to libraries.src.
#
# Generate the lists first (from a shell, in this directory):
#   ohsh -t ../../../projects/advanced -w dsp_lib -o build accumulator
# Then run:
#   vivado -mode batch -source read_sources.tcl
#
# Not run in CI (Vivado is licensed software). Checked against the Vivado
# Tcl command reference (UG835).

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

# Library names in the order ohsh wrote them to libraries.src.
proc read_library_order {path} {
    set fp [open $path r]
    set libraries [split [string trim [read $fp]] "\n"]
    close $fp
    return $libraries
}

# VHDL goes into named libraries, in library order. Verilog is global.
foreach lib [read_library_order build/libraries.src] {
    read_src build/${lib}_vhdl.src    vhdl    $lib
    read_src build/${lib}_verilog.src verilog $lib
}

# Continue with synthesis, for example:
#   synth_design -top accumulator -part <your part>
