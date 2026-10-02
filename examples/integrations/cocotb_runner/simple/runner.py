#!/usr/bin/env python3
"""cocotb Python runner, simple project: one SystemVerilog module on Icarus Verilog.

Runs ohsh, reads the source list for the `work` library and hands it to cocotb's
``cocotb_tools.runner`` API (cocotb >= 2.0).
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
PROJECT = EXAMPLES / "projects" / "simple"
TESTBENCHES = EXAMPLES / "testbenches"
BUILD = HERE / "build"
# The runner hands sys.path to the simulator, so this makes the shared cocotb
# tests importable while the simulation itself runs in the build directory.
sys.path.insert(0, str(TESTBENCHES))


def read_src(path: Path) -> list[str]:
    """Read an ohsh .src list into a list of paths (one per line)."""
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    BUILD.mkdir(exist_ok=True)

    # 1. Generate the ordered source list with ohsh. Running it through this
    # Python avoids depending on the `ohsh` command being on PATH.
    subprocess.run(
        [sys.executable, "-m", "ohsh", "-t", str(PROJECT), "-o", str(BUILD), "counter"],
        check=True,
    )
    sources = read_src(BUILD / "work_systemverilog.src")

    # 2. Build and 3. test via the cocotb runner.
    sim = "icarus"
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="counter",
        build_dir=str(BUILD / "sim_build"),
        timescale=("1ns", "1ps"),
        always=True,
    )
    results_xml = runner.test(
        hdl_toplevel="counter",
        test_module="test_counter",
    )

    num_tests, num_failed = get_results(results_xml)
    print(f"cocotb runner, simple: {num_tests} test(s), {num_failed} failure(s)")
    if num_failed:
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
