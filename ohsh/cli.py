# SPDX-License-Identifier: Apache-2.0

import argparse
import pathlib

from . import __version__
from .authoring import check_manifests, create_manifests, fix_manifests
from .core import run
from .utils import configure_logging


def log_file_path(value: str) -> pathlib.Path:
    path = pathlib.Path(value)
    if not path.parent.is_dir():
        raise argparse.ArgumentTypeError(f"directory does not exist: {path.parent}")
    return path


# In the order they run when several are given: each one works on what the one before left.
MANIFEST_ACTIONS = [
    ("create", create_manifests),
    ("fix", fix_manifests),
    ("check", check_manifests),
]


def build_parser(cwd: pathlib.Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ohsh",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Resolve HDL module manifests into ordered, per-library source lists.",
    )
    parser.add_argument(
        "module",
        nargs="?",
        help="name of the top-level module to resolve. With --fix or --check, the module "
        "to work on, along with its dependencies (default: every module)",
    )
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
    actions = parser.add_argument_group(
        "manifest actions",
        "Work on the manifests under --top-dir instead of writing source lists. "
        "They read the sources to find which design units each file declares and uses.",
    )
    actions.add_argument(
        "--create",
        action="store_true",
        help="write a manifest for every source directory that has none, asking before each file",
    )
    actions.add_argument(
        "--fix",
        action="store_true",
        help="add missing dependencies to the manifests and sort their sources into compile order",
    )
    actions.add_argument(
        "--check",
        action="store_true",
        help="report manifests that --fix would change and exit with code 104 if there are any",
    )
    actions.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="with --create, skip directories whose name or path under --top-dir matches "
        "this glob pattern (repeatable)",
    )
    actions.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="with --create, write every manifest without asking",
    )
    actions.add_argument(
        "--no-deps",
        action="store_true",
        help="with --fix or --check and a module, leave the dependencies of that module alone",
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


def main() -> None:
    cwd = pathlib.Path.cwd()
    parser = build_parser(cwd)
    args = parser.parse_args()
    requested_actions = [action for name, action in MANIFEST_ACTIONS if getattr(args, name)]
    if args.module is None and not requested_actions:
        parser.error("give a module to resolve, or at least one of --create, --fix and --check")
    if args.create and args.module is not None:
        parser.error("--create takes no module, it works on every directory under --top-dir")
    if args.no_deps and (args.module is None or not requested_actions):
        parser.error("--no-deps needs a module and --fix or --check")
    # Only the command line configures logging, so programs that call run()
    # directly keep control of where ohsh log messages go.
    configure_logging(verbosity=args.verbose, log_file=args.log_file)
    for action in requested_actions:
        action(args, cwd)
    if not requested_actions:
        run(args, cwd)
