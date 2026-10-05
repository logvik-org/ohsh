"""Tests for the regular-expression source scanner."""

from ohsh.scan import scan_source


def _scan(tmp_path, file_name, text):
    source = tmp_path / file_name
    source.write_text(text)
    return scan_source(source)


def test_vhdl_declarations_ignore_case_and_package_bodies(tmp_path):
    scanned = _scan(
        tmp_path,
        "Alu.vhd",
        "ENTITY Alu IS\nend entity;\npackage alu_pkg is\nend package;\npackage body alu_pkg is\n",
    )
    assert scanned.declared_units == {"alu", "alu_pkg", '"alu.vhd"'}


def test_vhdl_references_name_their_library(tmp_path):
    scanned = _scan(
        tmp_path,
        "top.vhd",
        "library ieee, math_lib;\n"
        "use math_lib.math_pkg.all;\n"
        "u_adder : entity work.adder port map (a => a);\n"
        "u_fifo : fifo generic map (depth => 4) port map (a => a);\n",
    )
    assert ("math_lib", "math_pkg") in scanned.references
    assert ("work", "adder") in scanned.references
    assert (None, "fifo") in scanned.references


def test_vhdl_bodies_reference_the_unit_they_belong_to(tmp_path):
    scanned = _scan(
        tmp_path,
        "bodies.vhd",
        "package body alu_pkg is\nend package body;\n"
        "architecture rtl of alu is\nbegin\nend architecture;\n"
        "configuration alu_cfg of alu_tb is\nend configuration;\n",
    )
    assert scanned.references == {("work", "alu_pkg"), ("work", "alu"), ("work", "alu_tb")}
    assert scanned.declared_units == {"alu_cfg", '"bodies.vhd"'}


def test_vhdl_record_fields_and_comments_are_not_references(tmp_path):
    scanned = _scan(
        tmp_path,
        "top.vhd",
        "-- u : entity work.commented_out port map (a);\n"
        "/* use work.block_commented.all; */\n"
        "ready <= bus_if.adder;\n",
    )
    assert scanned.references == set()


def test_verilog_declarations_and_references(tmp_path):
    scanned = _scan(
        tmp_path,
        "top.sv",
        '`include "defs/top_defs.svh"\n'
        "`define DEPTH 4\n"
        "// adder commented (\n"
        "module top import math_pkg::*; (input clk);\n"
        "  adder #(.W(`WIDTH)) u_adder (.clk(clk));\n"
        "  Fifo u_fifo [1:0] (.clk(clk));\n"
        "endmodule\n",
    )
    assert scanned.declared_units == {"top", "`depth", '"top.sv"'}
    assert {
        (None, "adder"),
        (None, "fifo"),
        (None, "math_pkg"),
        (None, "`width"),
        (None, '"top_defs.svh"'),
    } <= scanned.references


def test_unreadable_sources_scan_as_empty(tmp_path):
    assert _scan(tmp_path, "notes.txt", "entity notes is") == (set(), set())
    assert scan_source(tmp_path / "missing.vhd") == (set(), set())
