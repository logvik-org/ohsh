"""Tests for the --create, --fix and --check manifest actions."""

import json
import pathlib

import pytest

from ohsh.cli import main
from ohsh.utils import EXIT_MANIFEST_OUTDATED, EXIT_MODULE_NOT_FOUND, EXIT_USAGE

ADDER = "entity adder is\nend entity;\n"
ACCUMULATOR = (
    "library math_lib;\n"
    "use work.acc_pkg.all;\n"
    "entity accumulator is\nend entity;\n"
    "architecture rtl of accumulator is\nbegin\n"
    "  u_adder : entity math_lib.adder port map (a => a);\n"
    "end architecture;\n"
)
ACC_PKG = "package acc_pkg is\nend package;\n"


@pytest.fixture
def write_sources(tmp_path):
    def _write(sources):
        for relative_path, text in sources.items():
            source = tmp_path / relative_path
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(text)

    return _write


@pytest.fixture
def run_ohsh(tmp_path, monkeypatch):
    """Run the CLI on ``tmp_path`` and return its exit code."""

    def _run(*argv):
        monkeypatch.setattr("sys.argv", ["ohsh", "-t", str(tmp_path), *argv])
        try:
            main()
        except SystemExit as exc:
            return exc.code or 0
        return 0

    return _run


def _read_manifest(path):
    return json.loads(pathlib.Path(path).read_text())


def _write_manifest(path, manifest, indent=2):
    pathlib.Path(path).write_text(json.dumps(manifest, indent=indent) + "\n")


@pytest.fixture
def accumulator_project(tmp_path, write_sources):
    write_sources(
        {
            "adder/adder.vhd": ADDER,
            "accumulator/hdl/accumulator.vhd": ACCUMULATOR,
            "accumulator/hdl/acc_pkg.vhd": ACC_PKG,
        }
    )
    return tmp_path


def test_create_writes_manifests_with_dependencies_and_ordered_sources(
    accumulator_project, run_ohsh, capsys
):
    assert run_ohsh("--create", "--yes") == 0

    assert _read_manifest(accumulator_project / "adder/manifest.json") == {
        "module": "adder",
        "sources": ["adder.vhd"],
    }
    assert _read_manifest(accumulator_project / "accumulator/manifest.json") == {
        "module": "accumulator",
        "sources": ["hdl/acc_pkg.vhd", "hdl/accumulator.vhd"],
        "dependencies": {"math_lib": ["adder"]},
    }
    assert "Nothing depends on these new modules" in capsys.readouterr().out
    assert run_ohsh("--check") == 0


@pytest.mark.parametrize(
    "answers, created",
    [
        (["y", "n"], ["accumulator"]),
        (["n", "a"], ["adder"]),
        (["maybe", "a"], ["accumulator", "adder"]),
        (["q"], []),
        ([], []),
    ],
)
def test_create_asks_before_each_manifest(
    accumulator_project, run_ohsh, monkeypatch, answers, created
):
    remaining_answers = iter(answers)

    def _answer(prompt):
        try:
            return next(remaining_answers)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr("builtins.input", _answer)
    assert run_ohsh("--create") == 0
    manifests = accumulator_project.rglob("manifest.json")
    assert sorted(path.parent.name for path in manifests) == created


def test_create_leaves_existing_manifests_and_listed_sources_alone(
    accumulator_project, run_ohsh, write_sources, capsys
):
    hand_written = {"module": "my_adder", "sources": ["adder.vhd"]}
    _write_manifest(accumulator_project / "adder/manifest.json", hand_written)
    write_sources({"adder/extra.vhd": "entity extra is\nend entity;\n"})
    _write_manifest(
        accumulator_project / "manifest_acc.json",
        {"module": "acc", "sources": ["accumulator/hdl/accumulator.vhd"]},
    )

    assert run_ohsh("--create", "--yes") == 0

    assert _read_manifest(accumulator_project / "adder/manifest.json") == hand_written
    assert _read_manifest(accumulator_project / "accumulator/manifest.json") == {
        "module": "accumulator",
        "sources": ["hdl/acc_pkg.vhd"],
    }
    capsys.readouterr()
    assert run_ohsh("--create", "--yes") == 0
    assert "already listed" in capsys.readouterr().out


def test_create_skips_excluded_and_hidden_directories(accumulator_project, run_ohsh, write_sources):
    write_sources({".git/hook.v": "module hook;\n", "vendor/ip/ip.v": "module ip;\n"})
    assert run_ohsh("--create", "--yes", "--exclude", "vendor", "--exclude", "accum*") == 0
    manifests = accumulator_project.rglob("manifest.json")
    assert [path.parent.name for path in manifests] == ["adder"]


def test_create_makes_clashing_directory_names_unique(tmp_path, run_ohsh, write_sources):
    write_sources(
        {
            "adder/adder.vhd": ADDER,
            "adder/tb/adder_tb.vhd": "entity adder_tb is\nend entity;\n",
            "fifo/tb/fifo_tb.vhd": "entity fifo_tb is\nend entity;\n",
            "top.v": "module top;\n",
        }
    )
    _write_manifest(tmp_path / "adder/manifest.json", {"module": "adder", "sources": []})

    assert run_ohsh("--create", "--yes") == 0

    assert _read_manifest(tmp_path / "adder/tb/manifest.json")["module"] == "adder_tb"
    assert _read_manifest(tmp_path / "fifo/tb/manifest.json")["module"] == "fifo_tb"
    assert _read_manifest(tmp_path / "manifest.json")["module"] == tmp_path.name


def test_check_reports_missing_dependencies_and_source_order(accumulator_project, run_ohsh, capsys):
    _write_manifest(
        accumulator_project / "adder/manifest.json", {"module": "adder", "sources": ["adder.vhd"]}
    )
    _write_manifest(
        accumulator_project / "accumulator/manifest.json",
        {"module": "accumulator", "sources": ["hdl/accumulator.vhd", "hdl/acc_pkg.vhd"]},
    )

    assert run_ohsh("--check") == EXIT_MANIFEST_OUTDATED

    report = capsys.readouterr().out
    assert "missing dependency: adder (library math_lib)" in report
    assert "sources out of order, expected: hdl/acc_pkg.vhd, hdl/accumulator.vhd" in report
    assert "1 of 2 manifests need fixing" in report


def test_fix_adds_dependencies_sorts_sources_and_keeps_the_rest(
    accumulator_project, run_ohsh, capsys
):
    _write_manifest(
        accumulator_project / "adder/manifest.json", {"module": "adder", "sources": ["adder.vhd"]}
    )
    adder_manifest_before = (accumulator_project / "adder/manifest.json").read_text()
    manifest_path = accumulator_project / "accumulator/manifest.json"
    _write_manifest(
        manifest_path,
        {
            "module": "accumulator",
            "owner": "someone",
            "dependencies": {"vendor_lib": ["encrypted_ip"]},
            "sources": ["hdl/accumulator.vhd", "hdl/acc_pkg.vhd"],
        },
        indent=4,
    )

    assert run_ohsh("--fix") == 0

    assert "Fixed accumulator/manifest.json" in capsys.readouterr().out
    assert _read_manifest(manifest_path) == {
        "module": "accumulator",
        "owner": "someone",
        "dependencies": {"vendor_lib": ["encrypted_ip"], "math_lib": ["adder"]},
        "sources": ["hdl/acc_pkg.vhd", "hdl/accumulator.vhd"],
    }
    assert '\n    "module"' in manifest_path.read_text()
    assert (accumulator_project / "adder/manifest.json").read_text() == adder_manifest_before
    assert run_ohsh("--check") == 0
    assert "note: no source ohsh can read uses the dependency encrypted_ip" in (
        capsys.readouterr().out
    )


def test_fix_puts_a_package_before_its_body_and_its_users(tmp_path, run_ohsh, write_sources):
    write_sources(
        {
            "alu/alu.vhd": "use work.alu_pkg.all;\nentity alu is\nend entity;\n",
            "alu/alu_pkg_body.vhd": "package body alu_pkg is\nend package body;\n",
            "alu/alu_pkg.vhd": "package alu_pkg is\nend package;\n",
            "alu/alu_rtl.vhd": "architecture rtl of alu is\nbegin\nend architecture;\n",
        }
    )
    sources = ["alu_rtl.vhd", "alu.vhd", "alu_pkg_body.vhd", "alu_pkg.vhd"]
    _write_manifest(tmp_path / "alu/manifest.json", {"module": "alu", "sources": sources})

    assert run_ohsh("--fix") == 0

    assert _read_manifest(tmp_path / "alu/manifest.json")["sources"] == [
        "alu_pkg.vhd",
        "alu.vhd",
        "alu_rtl.vhd",
        "alu_pkg_body.vhd",
    ]


def test_reference_without_library_accepts_any_declared_library(tmp_path, run_ohsh, write_sources):
    write_sources(
        {
            "adder/adder.vhd": ADDER,
            "top/top.vhd": "entity top is\nend entity;\nu : adder port map (a => a);\n",
            "top2/top2.v": "module top2;\n  adder u_adder (.a(a));\nendmodule\n",
        }
    )
    _write_manifest(tmp_path / "adder/manifest.json", {"module": "adder", "sources": ["adder.vhd"]})
    _write_manifest(
        tmp_path / "top/manifest.json",
        {"module": "top", "sources": ["top.vhd"], "dependencies": {"math_lib": ["adder"]}},
    )
    _write_manifest(tmp_path / "top2/manifest.json", {"module": "top2", "sources": ["top2.v"]})

    assert run_ohsh("--fix") == 0

    assert _read_manifest(tmp_path / "top/manifest.json")["dependencies"] == {"math_lib": ["adder"]}
    assert _read_manifest(tmp_path / "top2/manifest.json")["dependencies"] == {"work": ["adder"]}


def test_unit_declared_by_two_modules_is_left_to_the_user(
    tmp_path, run_ohsh, write_sources, capsys
):
    write_sources(
        {
            "adder/adder.vhd": ADDER,
            "adder_fork/adder.vhd": ADDER,
            "top/top.vhd": "u : entity work.adder port map (a => a);\n",
            "top_fork/top.vhd": "u : entity work.adder port map (a => a);\n",
        }
    )
    for module in ("adder", "adder_fork"):
        _write_manifest(
            tmp_path / module / "manifest.json", {"module": module, "sources": ["adder.vhd"]}
        )
    _write_manifest(tmp_path / "top/manifest.json", {"module": "top", "sources": ["top.vhd"]})
    _write_manifest(
        tmp_path / "top_fork/manifest.json",
        {"module": "top_fork", "sources": ["top.vhd"], "dependencies": {"work": ["adder_fork"]}},
    )

    assert run_ohsh("--check") == 0

    report = capsys.readouterr().out
    assert "top/manifest.json\n  note: adder is declared by modules adder, adder_fork" in report
    assert "top_fork" not in report


def test_sources_that_use_each_other_keep_their_order(tmp_path, run_ohsh, write_sources, capsys):
    write_sources(
        {
            "loop/a.vhd": "entity a is\nend entity;\nu : entity work.b port map (x => x);\n",
            "loop/b.vhd": "entity b is\nend entity;\nu : entity work.a port map (x => x);\n",
        }
    )
    _write_manifest(
        tmp_path / "loop/manifest.json",
        {"module": "loop", "sources": ["b.vhd", "a.vhd", "gone.vhd"]},
    )

    assert run_ohsh("--check") == 0
    warnings = capsys.readouterr().err
    assert "use each other in a loop" in warnings
    assert "gone.vhd of module loop is missing" in warnings


def test_module_or_action_is_required(run_ohsh):
    assert run_ohsh() == EXIT_USAGE


def test_actions_run_in_order(accumulator_project, run_ohsh):
    assert run_ohsh("--check", "--fix", "--create", "--yes") == 0
    assert (accumulator_project / "accumulator/manifest.json").exists()


@pytest.mark.parametrize(
    "argv",
    [
        ["--create", "accumulator"],
        ["--fix", "--no-deps"],
        ["--no-deps", "accumulator"],
    ],
)
def test_options_that_do_not_go_together_are_usage_errors(run_ohsh, argv):
    assert run_ohsh(*argv) == EXIT_USAGE


@pytest.fixture
def outdated_project(accumulator_project, write_sources):
    """Three modules whose manifests all need fixing: accumulator uses adder, counter stands alone."""
    write_sources(
        {
            "adder/adder.vhd": "use work.adder_pkg.all;\n" + ADDER,
            "adder/adder_pkg.vhd": "package adder_pkg is\nend package;\n",
            "counter/counter.vhd": "use work.counter_pkg.all;\nentity counter is\nend entity;\n",
            "counter/counter_pkg.vhd": "package counter_pkg is\nend package;\n",
        }
    )
    sources_by_module = {
        "accumulator": ["hdl/accumulator.vhd", "hdl/acc_pkg.vhd"],
        "adder": ["adder.vhd", "adder_pkg.vhd"],
        "counter": ["counter.vhd", "counter_pkg.vhd"],
    }
    for module, sources in sources_by_module.items():
        _write_manifest(
            accumulator_project / module / "manifest.json", {"module": module, "sources": sources}
        )
    return accumulator_project


def _fixed_modules(capsys):
    report = capsys.readouterr().out
    return sorted(
        line.split("/")[0][len("Fixed ") :] for line in report.splitlines() if "Fixed" in line
    )


def test_fix_with_a_module_also_fixes_its_dependencies(outdated_project, run_ohsh, capsys):
    assert run_ohsh("--fix", "accumulator") == 0

    assert _fixed_modules(capsys) == ["accumulator", "adder"]
    assert _read_manifest(outdated_project / "adder/manifest.json")["sources"] == [
        "adder_pkg.vhd",
        "adder.vhd",
    ]
    assert not (outdated_project / "out").exists()
    assert run_ohsh("--check", "accumulator") == 0
    assert "All 2 manifests match their sources" in capsys.readouterr().out
    assert run_ohsh("--check") == EXIT_MANIFEST_OUTDATED


def test_no_deps_limits_fix_and_check_to_the_module(outdated_project, run_ohsh, capsys):
    assert run_ohsh("--check", "--no-deps", "accumulator") == EXIT_MANIFEST_OUTDATED
    assert "1 of 1 manifests need fixing" in capsys.readouterr().out

    assert run_ohsh("--fix", "--no-deps", "accumulator") == 0

    assert _fixed_modules(capsys) == ["accumulator"]
    assert run_ohsh("--check", "accumulator") == EXIT_MANIFEST_OUTDATED
    assert "1 of 2 manifests need fixing" in capsys.readouterr().out


def test_fix_and_check_reject_an_unknown_module(outdated_project, run_ohsh):
    assert run_ohsh("--check", "nonexistent") == EXIT_MODULE_NOT_FOUND
    assert run_ohsh("--fix", "nonexistent") == EXIT_MODULE_NOT_FOUND
