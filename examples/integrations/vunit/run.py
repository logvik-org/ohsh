#!/usr/bin/env python3
"""VUnit integration example.

Generates per-library source lists with ohsh and adds them to VUnit libraries,
then runs a VUnit testbench. Verified in CI against the demo project (GHDL
backend).
"""

import subprocess
import sys
from pathlib import Path

try:
    from vunit import VUnit

    import ohsh  # noqa: F401  (only checked here, run below as `python -m ohsh`)
except ImportError as error:
    sys.exit(
        f"{error.name} is not installed for {sys.executable}. "
        'From the repo root: pip install -e ".[examples]"'
    )

HERE = Path(__file__).resolve().parent
DEMO = HERE.parent.parent / "demo_project"
BUILD = HERE / "build"

# ohsh's work library is named "dut_lib" here, because VUnit reserves "work".
DUT_LIB = "dut_lib"


def read_src(path: Path) -> list[str]:
    """Read an ohsh .src file into a list of its non-empty lines."""
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    BUILD.mkdir(exist_ok=True)

    # 1. Resolve the design sources with ohsh. Running it through this Python
    # avoids depending on the `ohsh` command being on PATH.
    subprocess.run(
        [
            sys.executable,
            "-m",
            "ohsh",
            "-t",
            str(DEMO),
            "-o",
            str(BUILD),
            "-w",
            DUT_LIB,
            "accumulator",
        ],
        check=True,
    )

    # 2. Hand the lists to VUnit.
    vu = VUnit.from_argv()

    for library in read_src(BUILD / "libraries.src"):
        sources = read_src(BUILD / f"{library}_vhdl.src")
        vu.add_library(library).add_source_files(sources, allow_empty=True)

    tb = vu.add_library("tb_lib")
    tb.add_source_files(HERE / "tb_accumulator_vunit.vhd")

    # 3. Run (VUnit picks the simulator from $VUNIT_SIMULATOR, default ghdl).
    vu.main()


if __name__ == "__main__":
    main()
