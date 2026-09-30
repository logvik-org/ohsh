# SPDX-License-Identifier: Apache-2.0
"""Tests for the ohsh command-line interface."""

import pathlib

import pytest

from ohsh import __version__
from ohsh.cli import build_parser


def test_parser_defaults():
    parser = build_parser(pathlib.Path("/base"))
    args = parser.parse_args(["mytop"])
    assert args.module == "mytop"
    assert args.work == "work"
    assert args.verbose is False
    assert args.log_file is None
    assert pathlib.Path(args.top_dir) == pathlib.Path("/base")


def test_parser_all_options():
    parser = build_parser(pathlib.Path("/base"))
    args = parser.parse_args(
        ["-t", "/proj", "-w", "mylib", "-o", "/out", "-v", "--log-file", "x.log", "top"]
    )
    assert args.top_dir == "/proj"
    assert args.work == "mylib"
    assert args.output == "/out"
    assert args.verbose is True
    assert args.log_file == "x.log"


def test_module_is_required():
    parser = build_parser(pathlib.Path("/base"))
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_version_flag(capsys):
    parser = build_parser(pathlib.Path("/base"))
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_main_entry_point(tmp_path, make_module, monkeypatch):
    from ohsh import cli

    make_module("top", ["top.v"], dependencies={})
    out = tmp_path / "out"
    out.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["ohsh", "-t", str(tmp_path), "-o", str(out), "top"])
    cli.main()
    assert (out / "work_verilog.src").read_text().strip().endswith("top.v")
