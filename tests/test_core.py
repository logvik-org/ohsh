# SPDX-License-Identifier: Apache-2.0
"""End-to-end tests for ohsh.core.run via the CLI parser."""

import json
import pathlib

from ohsh.cli import build_parser
from ohsh.core import run
from ohsh.utils import (
    EXIT_CANNOT_CREATE_OUTPUT,
    EXIT_CIRCULAR_DEPENDENCY,
    EXIT_DATA_ERROR,
    EXIT_MANIFEST_NOT_FOUND,
    EXIT_MODULE_NOT_FOUND,
    EXIT_NO_INPUT,
)


def _run(top_dir, module, output, *, work="work", extra=None):
    """Invoke run() the way the CLI does and return the SystemExit code (or 0)."""
    argv = ["-t", str(top_dir), "-o", str(output), "-w", work, *(extra or []), module]
    args = build_parser(pathlib.Path.cwd()).parse_args(argv)
    try:
        run(args, pathlib.Path.cwd())
    except SystemExit as exc:
        return exc.code or 0
    return 0


def test_run_writes_ordered_src_files(tmp_path, make_module):
    make_module("adder", ["adder.vhd"], dependencies={})
    make_module("top", ["top.v", "top_pkg.vhd"], dependencies={"math_lib": ["adder"]})
    out = tmp_path / "out"
    out.mkdir()

    code = _run(tmp_path, "top", out)
    assert code == 0

    work_v = (out / "work_verilog.src").read_text().splitlines()
    work_vhd = (out / "work_vhdl.src").read_text().splitlines()
    math_vhd = (out / "math_lib_vhdl.src").read_text().splitlines()

    assert work_v == [str(tmp_path / "top" / "top.v")]
    assert work_vhd == [str(tmp_path / "top" / "top_pkg.vhd")]
    assert math_vhd == [str(tmp_path / "adder" / "adder.vhd")]
    # A dependency-only library with no Verilog gets no Verilog .src file.
    assert not (out / "math_lib_verilog.src").exists()


def test_run_writes_library_order(tmp_path, make_module):
    make_module("adder", ["adder.vhd"], dependencies={})
    make_module("top", ["top.vhd"], dependencies={"math_lib": ["adder"]})
    out = tmp_path / "out"
    out.mkdir()
    assert _run(tmp_path, "top", out) == 0
    assert (out / "libraries.src").read_text().splitlines() == ["math_lib", "work"]


def test_run_creates_missing_output_dir(tmp_path, make_module):
    make_module("top", ["top.vhd"], dependencies={})
    out = tmp_path / "build" / "lists"
    assert _run(tmp_path, "top", out) == 0
    assert (out / "work_vhdl.src").exists()


def test_run_output_path_is_a_file(tmp_path, make_module):
    make_module("top", ["top.vhd"], dependencies={})
    out = tmp_path / "not_a_dir"
    out.write_text("")
    assert _run(tmp_path, "top", out) == EXIT_CANNOT_CREATE_OUTPUT


def test_run_classifies_extensions(tmp_path, make_module):
    make_module(
        "top",
        ["a.v", "b.sv", "c.svp", "d.vhd", "e.vhdl", "f.vo"],
        dependencies={},
    )
    out = tmp_path / "out"
    out.mkdir()
    assert _run(tmp_path, "top", out) == 0

    verilog = (out / "work_verilog.src").read_text()
    vhdl = (out / "work_vhdl.src").read_text()
    for name in ("a.v", "b.sv", "c.svp"):
        assert name in verilog
    for name in ("d.vhd", "e.vhdl", "f.vo"):
        assert name in vhdl


def test_run_no_debug_log_side_effect(tmp_path, make_module, monkeypatch):
    make_module("top", ["top.v"], dependencies={})
    out = tmp_path / "out"
    out.mkdir()
    monkeypatch.chdir(tmp_path)
    assert _run(tmp_path, "top", out) == 0
    assert not (tmp_path / "debug.log").exists()


def test_run_invalid_top_dir(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    assert _run(tmp_path / "does_not_exist", "top", out) == EXIT_NO_INPUT


def test_run_module_not_found(tmp_path, make_module):
    make_module("top", ["top.v"], dependencies={})
    out = tmp_path / "out"
    out.mkdir()
    assert _run(tmp_path, "nonexistent", out) == EXIT_MODULE_NOT_FOUND


def test_run_circular_dependency(tmp_path, make_module):
    make_module("a", ["a.vhd"], dependencies={"work": ["b"]})
    make_module("b", ["b.vhd"], dependencies={"work": ["a"]})
    out = tmp_path / "out"
    out.mkdir()
    assert _run(tmp_path, "a", out) == EXIT_CIRCULAR_DEPENDENCY
    assert not list(out.iterdir())


def test_run_missing_dependency_manifest(tmp_path, make_module, caplog):
    make_module("top", ["top.v"], dependencies={"work": ["ghost"]})
    out = tmp_path / "out"
    out.mkdir()
    assert _run(tmp_path, "top", out) == EXIT_MANIFEST_NOT_FOUND
    assert "ghost (required by top)" in caplog.text


def test_run_bad_json(tmp_path):
    (tmp_path / "manifest.json").write_text("{ not valid json ")
    out = tmp_path / "out"
    out.mkdir()
    assert _run(tmp_path, "top", out) == EXIT_DATA_ERROR


def test_run_missing_source_file(tmp_path):
    # Manifest references a source that does not exist on disk.
    mod = tmp_path / "top"
    mod.mkdir()
    (mod / "manifest.json").write_text(
        json.dumps({"module": "top", "sources": ["ghost.v"], "dependencies": {}})
    )
    out = tmp_path / "out"
    out.mkdir()
    assert _run(tmp_path, "top", out) == EXIT_NO_INPUT
