# SPDX-License-Identifier: Apache-2.0
# pylint: disable=logging-fstring-interpolation missing-function-docstring line-too-long

import logging
import pathlib

logger = logging.getLogger(__name__)

CONSOLE_HANDLER_NAME = "ohsh-console"

EXIT_SUCCESS = 0
EXIT_UNEXPECTED_ERROR = 1
EXIT_FILE_ERROR = 2
EXIT_JSON_ERROR = 3
EXIT_MODULE_NOT_FOUND = 4
EXIT_INVALID_TOP_DIR = 5
EXIT_MANIFEST_NOT_FOUND = 6
EXIT_MISSING_FILES = 7
EXIT_CIRCULAR_DEPENDENCY = 8


class CircularDependencyError(Exception):
    def __init__(self, cycle):
        self.cycle = cycle
        super().__init__(" -> ".join(cycle))


def extract_dependencies(manifest_data, top_manifest, work):
    """Resolve dependencies recursively into a post-ordered list of (lib, module).

    Dependencies appear before the modules that depend on them and duplicates
    are dropped. A circular dependency has no valid compile order, so it raises
    ``CircularDependencyError`` naming the modules in the cycle.
    """
    collected_deps = []
    dependency_chain = []
    resolved = set()

    def _collect_dependencies_of(manifest, library):
        module_name = manifest.get("module")
        # The same module reached through another library resolves its 'work'
        # dependencies differently, so only skip exact (library, module) repeats.
        if (library, module_name) in resolved:
            return
        logger.debug(f"Extracting dependencies for {module_name}")
        dependency_chain.append(module_name)

        for lib_name, modules in manifest.get("dependencies", {}).items():
            # Replace 'work' with the library this module is being resolved into.
            if lib_name == "work":
                lib_name = library
            for module in modules:
                logger.debug(f"Processing dependency {module} in library {lib_name}")
                if module in dependency_chain:
                    cycle_start = dependency_chain.index(module)
                    raise CircularDependencyError(dependency_chain[cycle_start:] + [module])

                # Recurse first so deeper dependencies are collected before this one.
                dep_manifest = next(
                    (m for m in manifest_data if m.get("module") == module),
                    None,
                )
                if dep_manifest is not None:
                    _collect_dependencies_of(dep_manifest, lib_name)

                dep_tuple = (lib_name, module)
                if dep_tuple not in collected_deps:
                    collected_deps.append(dep_tuple)

        dependency_chain.pop()
        resolved.add((library, module_name))

    _collect_dependencies_of(top_manifest, work)
    return collected_deps


def validate_top_dir(top_dir):
    return pathlib.Path(top_dir).is_dir()


def ensure_abs_path(cwd, top_dir):
    """Return an absolute version of ``top_dir``, resolved against ``cwd``."""
    path = pathlib.Path(top_dir)
    if not path.is_absolute():
        return (pathlib.Path(cwd) / path).resolve()
    return path


def configure_logging(verbose=False, log_file=None):
    """Configure logging for the ``ohsh`` package.

    Handlers are attached to the package logger (``ohsh``) so that messages from
    every submodule are captured. Console output goes to stderr at INFO level
    (DEBUG when ``verbose``). A file handler is only added when ``log_file`` is
    given, so running ``ohsh`` never writes a stray ``debug.log`` into the cwd.
    """
    pkg_logger = logging.getLogger("ohsh")
    pkg_logger.setLevel(logging.DEBUG)
    # Our handlers already emit everything, so a root handler set up by the
    # host application (e.g. logging.basicConfig) would print each line twice.
    pkg_logger.propagate = False

    # Avoid attaching duplicate handlers if called more than once. Look for our
    # own handler by name: other code (e.g. pytest capture) may attach its own.
    if any(h.get_name() == CONSOLE_HANDLER_NAME for h in pkg_logger.handlers):
        return pkg_logger

    formatter = logging.Formatter("ohsh - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.set_name(CONSOLE_HANDLER_NAME)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(formatter)
    pkg_logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        pkg_logger.addHandler(file_handler)

    return pkg_logger


def discover_manifests(top_dir):
    logger.info(f"Discovering manifest files in {top_dir}")
    manifest_files = list(pathlib.Path(top_dir).rglob("manifest*.json"))
    for manifest in manifest_files:
        logger.info(f"Found manifest file: {manifest}")
    return manifest_files
