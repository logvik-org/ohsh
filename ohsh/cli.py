# SPDX-License-Identifier: Apache-2.0

import argparse
import pathlib

from . import __version__
from .core import run
from .utils import EXIT_CODE_DESCRIPTIONS, configure_logging


def log_file_path(value):
    path = pathlib.Path(value)
    if not path.parent.is_dir():
        raise argparse.ArgumentTypeError(f"directory does not exist: {path.parent}")
    return path


def format_exit_codes():
    lines = [f"  {code:>3}  {description}" for code, description in EXIT_CODE_DESCRIPTIONS.items()]
    return "exit codes:\n" + "\n".join(lines)


def build_parser(cwd):
    parser = argparse.ArgumentParser(
        prog="ohsh",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=format_exit_codes(),
        description="Resolve HDL module manifests into ordered, per-library source lists.",
    )
    parser.add_argument("module", help="name of the top-level module")
    parser.add_argument(
        "-t",
        "--top-dir",
        default=cwd,
        help="directory to search for manifest files (default: current directory)",
    )
    parser.add_argument(
        "-w",
        "--work",
        default="work",
        help="library for the top module, which 'work' in its manifest refers to (default: work)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=cwd,
        help="directory for the .src lists and libraries.src, created if missing (default: current directory)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="show progress (-v) or debug details (-vv), otherwise only warnings and errors",
    )
    parser.add_argument(
        "--log-file",
        type=log_file_path,
        default=None,
        metavar="PATH",
        help="also write debug logs to this file",
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
