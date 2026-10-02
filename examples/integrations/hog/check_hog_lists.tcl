# Check that hog reads ohsh-generated list files as intended: every file listed
# exists and lands in the library named after its list file. This uses hog's own
# ReadListFile, so it runs in plain tclsh without Vivado or Quartus.
#
# Usage: tclsh check_hog_lists.tcl <hog_root> <repo_root> <list_file>...

# hog only loads tcllib's cmdline itself when running inside Quartus.
package require cmdline

lassign $argv hog_root repo_root
set list_files [lrange $argv 2 end]
set argv {}
source [file join $hog_root Tcl hog.tcl]

proc count_entries {list_file} {
    set fp [open $list_file r]
    set lines [split [string trim [read $fp]] "\n"]
    close $fp
    return [llength [lsearch -all -inline -not -exact $lines ""]]
}

set failures 0
foreach list_file $list_files {
    set library [file tail $list_file]
    set expected [count_entries $list_file]
    lassign [ReadListFile $list_file $repo_root] libraries properties filesets
    set found 0
    if {[dict exists $libraries $library]} {
        set found [llength [dict get $libraries $library]]
    }
    if {$found == $expected} {
        puts "OK: hog reads $found file(s) into library [file rootname $library]"
    } else {
        puts "FAIL: $list_file lists $expected file(s), hog found $found"
        incr failures
    }
}
exit [expr {$failures > 0}]
