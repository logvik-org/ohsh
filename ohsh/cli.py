# SPDX-License-Identifier: Apache-2.0
# pylint: disable=logging-fstring-interpolation missing-function-docstring line-too-long

import argparse
import pathlib

from . import __version__
from .core import run
from .utils import configure_logging


def log_file_path(value):
    path = pathlib.Path(value)
    if not path.parent.is_dir():
        raise argparse.ArgumentTypeError(f"directory does not exist: {path.parent}")
    return path


def build_parser(cwd):
    parser = argparse.ArgumentParser(
        prog="ohsh",
        description="ohsh - Ola's HDL Source Handler. Resolve HDL module manifests into ordered, per-library compile lists.",
    )
    parser.add_argument("module", help="The name of the module that is treated as the top-level.")
    parser.add_argument(
        "-t",
        "--top-dir",
        default=cwd,
        help="Path to the project top-level directory. Used as base for searching for manifest files. Default is the current working directory.",
    )
    parser.add_argument(
        "-w",
        "--work",
        default="work",
        help="The name of the work library. Default is 'work'.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=cwd,
        help="Output directory for the source file lists. For each library, a file is created with the list of source files in order. Default is the current working directory.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Show progress (-v) or debug details (-vv). By default only warnings and errors are shown.",
    )
    parser.add_argument(
        "--log-file",
        type=log_file_path,
        default=None,
        metavar="PATH",
        help="Also write logs to the given file. By default no log file is written.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main():
    cwd = pathlib.Path.cwd()
    parser = build_parser(cwd)
    args = parser.parse_args()
    # Only the command line configures logging, so programs that call run()
    # directly keep control of where ohsh log messages go.
    configure_logging(verbosity=args.verbose, log_file=args.log_file)
    run(args, cwd)
