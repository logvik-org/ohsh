#!/usr/bin/env python3
"""VUnit, simple project: every module in one library.

VUnit reserves the library name `work`, so ohsh is run with ``-w dut_lib`` to
put the design in a library with another name.
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
EXAMPLES = HERE.parents[2]
BUILD = HERE / "build"
TESTBENCH = EXAMPLES / "testbenches" / "tb_accumulator_vunit.vhd"


def read_src(path: Path) -> list[str]:
    """Read an ohsh .src file into a list of its non-empty lines."""
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def run_ohsh(project: str, top_library: str) -> None:
    # Running ohsh through this Python avoids depending on the `ohsh` command
    # being on PATH.
    subprocess.run(
        [
            sys.executable,
            "-m",
            "ohsh",
            "-t",
            str(EXAMPLES / "projects" / project),
            "-w",
            top_library,
            "-o",
            str(BUILD),
            "accumulator",
        ],
        check=True,
    )


def create_vunit() -> VUnit:
    vu = VUnit.from_argv(compile_builtins=False)
    vu.add_vhdl_builtins()
    return vu


def main() -> None:
    run_ohsh("simple", "dut_lib")
    vu = create_vunit()
    dut_lib = vu.add_library("dut_lib")
    dut_lib.add_source_files(read_src(BUILD / "dut_lib_vhdl.src"))
    # The testbench goes into the same library, where `work.accumulator` resolves.
    dut_lib.add_source_files(TESTBENCH)
    vu.main()


if __name__ == "__main__":
    main()
