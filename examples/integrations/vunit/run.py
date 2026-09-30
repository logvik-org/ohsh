#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""VUnit integration example.

Generates per-library source lists with ohsh and adds them to VUnit libraries,
then runs a VUnit testbench. Verified in CI against the demo project (GHDL
backend).
"""

import subprocess
from pathlib import Path

from vunit import VUnit

HERE = Path(__file__).resolve().parent
DEMO = HERE.parent.parent / "demo_project"
BUILD = HERE / "build"

# ohsh's work library is named "dut_lib" here, because VUnit reserves "work".
DUT_LIB = "dut_lib"


def read_src(path: Path) -> list[str]:
    """Read an ohsh .src list into a list of paths (one per line)."""
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    BUILD.mkdir(exist_ok=True)

    # 1. Resolve the design sources with ohsh.
    subprocess.run(
        ["ohsh", "-t", str(DEMO), "-o", str(BUILD), "-w", DUT_LIB, "accumulator"],
        check=True,
    )

    # 2. Hand the lists to VUnit.
    vu = VUnit.from_argv()

    math = vu.add_library("math_lib")
    math.add_source_files(read_src(BUILD / "math_lib_vhdl.src"))

    dut = vu.add_library(DUT_LIB)
    dut.add_source_files(read_src(BUILD / f"{DUT_LIB}_vhdl.src"))

    tb = vu.add_library("tb_lib")
    tb.add_source_files(HERE / "tb_accumulator_vunit.vhd")

    # 3. Run (VUnit picks the simulator from $VUNIT_SIMULATOR, default ghdl).
    vu.main()


if __name__ == "__main__":
    main()
