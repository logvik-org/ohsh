"""Tests for the ohsh command-line interface."""

import logging
import pathlib

import pytest

from ohsh import __version__
from ohsh.cli import build_parser
from ohsh.core import run
from ohsh.utils import CONSOLE_HANDLER_NAME, EXIT_CODE_DESCRIPTIONS, EXIT_USAGE


def test_parser_defaults():
    parser = build_parser(pathlib.Path("/base"))
    args = parser.parse_args(["mytop"])
    assert args.module == "mytop"
    assert args.work == "work"
    assert args.verbose == 0
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
    assert args.verbose == 1
    assert args.log_file == pathlib.Path("x.log")


def test_module_is_required():
    parser = build_parser(pathlib.Path("/base"))
    with pytest.raises(SystemExit) as exc:
        parser.parse_args([])
    assert exc.value.code == EXIT_USAGE


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


def test_main_writes_log_file_when_requested(tmp_path, make_module, monkeypatch):
    from ohsh import cli

    make_module("top", ["top.v"], dependencies={})
    out = tmp_path / "out"
    out.mkdir()
    log_path = tmp_path / "run.log"
    argv = ["ohsh", "-t", str(tmp_path), "-o", str(out), "--log-file", str(log_path), "top"]
    monkeypatch.setattr("sys.argv", argv)
    cli.main()
    assert "Found module top" in log_path.read_text()


def test_run_leaves_logging_unconfigured(tmp_path, make_module):
    make_module("top", ["top.v"], dependencies={})
    args = build_parser(tmp_path).parse_args(["-o", str(tmp_path), "top"])
    run(args, tmp_path)
    pkg_logger = logging.getLogger("ohsh")
    assert pkg_logger.propagate is True
    assert CONSOLE_HANDLER_NAME not in [h.get_name() for h in pkg_logger.handlers]


def test_log_file_in_missing_directory_is_a_usage_error(tmp_path, capsys):
    parser = build_parser(tmp_path)
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--log-file", str(tmp_path / "nope" / "run.log"), "top"])
    assert exc.value.code == 2
    assert "directory does not exist" in capsys.readouterr().err


def test_verbose_flag_counts():
    args = build_parser(pathlib.Path("/base")).parse_args(["-vv", "top"])
    assert args.verbose == 2


def test_help_lists_every_exit_code(capsys):
    with pytest.raises(SystemExit):
        build_parser(pathlib.Path("/base")).parse_args(["--help"])
    help_text = capsys.readouterr().out
    for code, description in EXIT_CODE_DESCRIPTIONS.items():
        assert f"{code:>3}  {description}" in help_text
