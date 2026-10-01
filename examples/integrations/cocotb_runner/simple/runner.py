#!/usr/bin/env python3
"""cocotb (Python runner) integration example.

Generates source lists with ohsh, reads them, and drives cocotb's
``cocotb_tools.runner`` API (cocotb >= 2.0). Verified in CI against the demo
project.
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
DEMO = HERE.parent.parent / "demo_project"
BUILD = HERE / "build"


def read_src(path: Path) -> list[str]:
    """Read an ohsh .src list into a list of paths (one per line)."""
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    BUILD.mkdir(exist_ok=True)

    # 1. Generate the ordered source list with ohsh. Running it through this
    # Python avoids depending on the `ohsh` command being on PATH.
    subprocess.run(
        [sys.executable, "-m", "ohsh", "-t", str(DEMO), "-o", str(BUILD), "counter"],
        check=True,
    )
    sources = read_src(BUILD / "work_verilog.src")

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
        test_dir=str(HERE),
    )

    num_tests, num_failed = get_results(results_xml)
    print(f"cocotb runner example: {num_tests} test(s), {num_failed} failure(s)")
    if num_failed:
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
