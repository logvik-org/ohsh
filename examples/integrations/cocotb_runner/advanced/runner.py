#!/usr/bin/env python3
"""cocotb Python runner, advanced project (cocotb >= 2.0).

1. The VHDL accumulator, spread over three libraries, on NVC. Each library is
   built with ``runner.build(hdl_library=...)`` in the order ohsh wrote to
   libraries.src.
2. The Verilog counter, whose settings come from a ``.vh`` header, on Icarus
   Verilog. The header is listed in the manifest, so ohsh puts it in the source
   list before the file that uses it.
"""

import subprocess
import sys
from pathlib import Path

try:
    from cocotb_tools.runner import get_results, get_runner

    import ohsh  # noqa: F401  (only checked here, run below as `python -m ohsh`)
except ImportError as error:
    sys.exit(
        f"{error.name} is not installed for {sys.executable}. "
        'From the repo root: pip install -e ".[examples]"'
    )

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parents[2]
PROJECT = EXAMPLES / "projects" / "advanced"
TESTBENCHES = EXAMPLES / "testbenches"
BUILD = HERE / "build"
# The runner hands sys.path to the simulator, so this makes the shared cocotb
# tests importable while the simulation itself runs in the build directory.
sys.path.insert(0, str(TESTBENCHES))
TOP_LIBRARY = "dsp_lib"


def read_src(path: Path) -> list[str]:
    """Read an ohsh .src list into a list of paths (one per line)."""
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def run_ohsh(top: str, output: Path, *extra_args: str) -> None:
    # Running ohsh through this Python avoids depending on the `ohsh` command
    # being on PATH.
    subprocess.run(
        [sys.executable, "-m", "ohsh", "-t", str(PROJECT), "-o", str(output), *extra_args, top],
        check=True,
    )


def test_vhdl_accumulator() -> Path:
    build = BUILD / "accumulator"
    run_ohsh("accumulator", build, "-w", TOP_LIBRARY)

    runner = get_runner("nvc")
    for library in read_src(build / "libraries.src"):
        runner.build(
            hdl_library=library,
            sources=read_src(build / f"{library}_vhdl.src"),
            build_dir=str(build / "sim_build"),
            always=True,
        )
    return runner.test(
        hdl_toplevel="accumulator",
        hdl_toplevel_library=TOP_LIBRARY,
        test_module="test_accumulator",
    )


def test_verilog_counter() -> Path:
    build = BUILD / "counter"
    run_ohsh("counter", build)

    runner = get_runner("icarus")
    runner.build(
        sources=read_src(build / "work_verilog.src"),
        hdl_toplevel="counter",
        build_dir=str(build / "sim_build"),
        timescale=("1ns", "1ps"),
        always=True,
    )
    return runner.test(hdl_toplevel="counter", test_module="test_counter")


def main() -> None:
    total_failed = 0
    for results_xml in (test_vhdl_accumulator(), test_verilog_counter()):
        num_tests, num_failed = get_results(results_xml)
        print(
            f"cocotb runner, advanced: {results_xml.parent.parent.name}: "
            f"{num_tests} test(s), {num_failed} failure(s)"
        )
        total_failed += num_failed
    if total_failed:
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
