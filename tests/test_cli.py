"""Tests for the ohsh command-line interface."""

import logging
import pathlib
import runpy
import subprocess
import sys

import pytest

from ohsh import __version__
from ohsh.cli import build_parser, main
from ohsh.core import run
from ohsh.utils import CONSOLE_HANDLER_NAME, EXIT_NO_INPUT, EXIT_USAGE


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
    make_module("top", ["top.v"], dependencies={})
    out = tmp_path / "out"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["ohsh", "-t", str(tmp_path), "-o", str(out), "top"])
    main()
    assert (out / "work_systemverilog.src").read_text().strip().endswith("top.v")


def test_main_writes_log_file_when_requested(tmp_path, make_module, monkeypatch):
    make_module("top", ["top.v"], dependencies={})
    out = tmp_path / "out"
    log_path = tmp_path / "run.log"
    argv = ["ohsh", "-t", str(tmp_path), "-o", str(out), "--log-file", str(log_path), "top"]
    monkeypatch.setattr("sys.argv", argv)
    main()
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
    assert exc.value.code == EXIT_USAGE
    assert "directory does not exist" in capsys.readouterr().err


def test_verbose_flag_counts():
    args = build_parser(pathlib.Path("/base")).parse_args(["-vv", "top"])
    assert args.verbose == 2


def test_python_dash_m_ohsh_runs_the_cli(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["ohsh", "--version"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("ohsh", run_name="__main__")
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == f"ohsh {__version__}"


def test_errors_exit_cleanly_without_site_builtins(tmp_path):
    # Regression for #7: the builtin exit() only exists when the site module is
    # loaded, so `python -S` used to crash with a NameError instead of exiting.
    package_root = pathlib.Path(__file__).resolve().parents[1]
    script = (
        f"import sys; sys.path.insert(0, {str(package_root)!r}); "
        f"sys.argv = ['ohsh', '-t', {str(tmp_path / 'missing')!r}, 'top']; "
        "from ohsh.cli import main; main()"
    )
    completed = subprocess.run([sys.executable, "-S", "-c", script], capture_output=True, text=True)
    assert completed.returncode == EXIT_NO_INPUT
    assert "does not exist" in completed.stderr
