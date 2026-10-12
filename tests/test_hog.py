"""Tests for the hog list files written by ``--format hog``."""

import pytest

from ohsh.cli import main
from ohsh.utils import EXIT_USAGE


def _write_hog_lists(monkeypatch, top_dir, output, module, *, work="work"):
    argv = ["ohsh", "--format", "hog", "-t", str(top_dir), "-o", str(output)]
    monkeypatch.setattr("sys.argv", [*argv, "--relative-to", str(top_dir), "-w", work, module])
    main()


def test_hog_writes_one_list_per_library_with_relative_paths(tmp_path, make_module, monkeypatch):
    make_module("adder", ["adder.vhd"])
    make_module("top", ["top.vhd"], {"math_lib": ["adder"]})
    out = tmp_path / "Top" / "demo" / "list"
    _write_hog_lists(monkeypatch, tmp_path, out, "top", work="dsp_lib")
    assert sorted(path.name for path in out.iterdir()) == ["dsp_lib.src", "math_lib.src"]
    assert (out / "math_lib.src").read_text().splitlines() == ["adder/adder.vhd"]


def test_hog_marks_the_file_declaring_the_top_entity(tmp_path, make_module, monkeypatch):
    top_dir = make_module("top", ["top_pkg.vhd", "top.vhd"])
    (top_dir / "top_pkg.vhd").write_text("package top_pkg is\nend package;\n")
    (top_dir / "top.vhd").write_text("entity Top is\nend entity;\n")
    out = tmp_path / "list"
    _write_hog_lists(monkeypatch, tmp_path, out, "top")
    assert (out / "work.src").read_text().splitlines() == [
        "top/top_pkg.vhd",
        "top/top.vhd top=top",
    ]


def test_hog_marks_a_verilog_top_module(tmp_path, make_module, monkeypatch):
    top_dir = make_module("top", ["top.sv"])
    (top_dir / "top.sv").write_text("module top;\nendmodule\n")
    out = tmp_path / "list"
    _write_hog_lists(monkeypatch, tmp_path, out, "top")
    assert (out / "work.src").read_text().splitlines() == ["top/top.sv top=top"]


def test_hog_puts_both_languages_of_a_library_in_one_list(tmp_path, make_module, monkeypatch):
    make_module("top", ["top.vhd", "helper.sv"])
    out = tmp_path / "list"
    _write_hog_lists(monkeypatch, tmp_path, out, "top")
    assert sorted((out / "work.src").read_text().splitlines()) == ["top/helper.sv", "top/top.vhd"]


def test_hog_warns_when_no_source_declares_the_top(tmp_path, make_module, monkeypatch, capsys):
    make_module("top", ["top.vhd"])
    out = tmp_path / "list"
    _write_hog_lists(monkeypatch, tmp_path, out, "top")
    assert "top_<project>" in capsys.readouterr().err
    assert (out / "work.src").read_text().splitlines() == ["top/top.vhd"]


def test_hog_needs_relative_to(tmp_path, make_module, monkeypatch):
    make_module("top", ["top.vhd"])
    monkeypatch.setattr("sys.argv", ["ohsh", "--format", "hog", "-t", str(tmp_path), "top"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == EXIT_USAGE
