# SPDX-License-Identifier: Apache-2.0

import logging
import os
import pathlib
from typing import Any, Dict, Hashable, Iterable, List, Optional, Set, Tuple, TypeVar, Union

logger = logging.getLogger(__name__)

# Annotations use the typing generics and no `X | Y` unions because ohsh runs on
# Python 3.6, where the built-in forms fail at import time.
StrPath = Union[str, "os.PathLike[str]"]
# A parsed manifest file, plus the "manifest_path" key that run() adds.
Manifest = Dict[str, Any]
# A (library, module) pair.
Dependency = Tuple[str, str]

HashableT = TypeVar("HashableT", bound=Hashable)

CONSOLE_HANDLER_NAME = "ohsh-console"
CONSOLE_LEVEL_BY_VERBOSITY = {0: logging.WARNING, 1: logging.INFO}

# Exit codes follow the Unix conventions where one exists: 1 for a general
# error, 2 for usage errors (raised by argparse), and BSD sysexits.h (64-78) for
# bad input and output. Errors specific to ohsh start at 100, clear of those
# ranges and of the 126+ codes that shells reserve.
EXIT_SUCCESS = 0
EXIT_UNEXPECTED_ERROR = 1
EXIT_USAGE = 2
EXIT_DATA_ERROR = 65
EXIT_NO_INPUT = 66
EXIT_CANNOT_CREATE_OUTPUT = 73
EXIT_MODULE_NOT_FOUND = 100
EXIT_MANIFEST_NOT_FOUND = 101
EXIT_CIRCULAR_DEPENDENCY = 102
EXIT_DUPLICATE_MODULE = 103

EXIT_CODE_DESCRIPTIONS = {
    EXIT_SUCCESS: "success",
    EXIT_UNEXPECTED_ERROR: "unexpected error",
    EXIT_USAGE: "invalid command-line arguments",
    EXIT_DATA_ERROR: "a manifest is not valid JSON or has the wrong structure",
    EXIT_NO_INPUT: "top directory, manifest or source file missing or unreadable",
    EXIT_CANNOT_CREATE_OUTPUT: "output directory cannot be created",
    EXIT_MODULE_NOT_FOUND: "top module not found in any manifest",
    EXIT_MANIFEST_NOT_FOUND: "a dependency has no manifest",
    EXIT_CIRCULAR_DEPENDENCY: "modules depend on each other in a loop",
    EXIT_DUPLICATE_MODULE: "a module name is declared in more than one manifest",
}


class CircularDependencyError(Exception):
    def __init__(self, cycle: List[str]) -> None:
        self.cycle = cycle
        super().__init__(" -> ".join(cycle))


class MissingManifestError(Exception):
    def __init__(self, module: str, required_by: str) -> None:
        self.module = module
        self.required_by = required_by
        super().__init__(f"no manifest found for module {module} (required by {required_by})")


class InvalidManifestError(Exception):
    pass


def _is_list_of_strings(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def validate_manifest(manifest: object) -> None:
    """Raise ``InvalidManifestError`` naming the first structural problem in ``manifest``.

    ``sources`` and ``dependencies`` are optional. Unknown keys are ignored.
    """
    if not isinstance(manifest, dict):
        raise InvalidManifestError("the top level must be a JSON object")
    if not isinstance(manifest.get("module"), str) or not manifest["module"]:
        raise InvalidManifestError('"module" must be a non-empty string')
    if not _is_list_of_strings(manifest.get("sources", [])):
        raise InvalidManifestError('"sources" must be a list of file names')
    dependencies = manifest.get("dependencies", {})
    if not isinstance(dependencies, dict) or not all(
        _is_list_of_strings(modules) for modules in dependencies.values()
    ):
        raise InvalidManifestError('"dependencies" must map library names to lists of module names')


def remove_duplicates_keeping_first(items: Iterable[HashableT]) -> List[HashableT]:
    # A dict keeps its keys unique and in insertion order, which a set would not.
    return list(dict.fromkeys(items))


def find_duplicate_modules(manifest_data: List[Manifest]) -> Dict[str, List[str]]:
    """Return {module: [manifest paths]} for every module declared more than once."""
    paths_by_module: Dict[str, List[str]] = {}
    for manifest in manifest_data:
        paths_by_module.setdefault(manifest["module"], []).append(manifest["manifest_path"])
    return {module: paths for module, paths in paths_by_module.items() if len(paths) > 1}


def resolve_library_name(declared_library: str, current_library: str) -> str:
    # In a manifest, 'work' means the library the module itself is compiled into.
    return current_library if declared_library == "work" else declared_library


def extract_dependencies(
    manifests_by_module: Dict[str, Manifest], top_manifest: Manifest, work: str
) -> List[Dependency]:
    """Return every module ``top_manifest`` depends on, directly or indirectly.

    The result is a list of (library, module) pairs in compile order: each module
    comes after all the modules it depends on, and each pair appears once. The
    top module itself is not included. A circular dependency has no valid compile
    order, so it raises ``CircularDependencyError`` naming the modules in the cycle.
    A dependency without a manifest raises ``MissingManifestError``.
    """
    collected_deps: List[Dependency] = []
    dependency_chain: List[str] = []
    resolved: Set[Dependency] = set()

    def _collect_dependencies_of(manifest: Manifest, library: str) -> None:
        module_name: str = manifest["module"]
        # The same module reached through another library resolves its 'work'
        # dependencies differently, so only skip exact (library, module) repeats.
        if (library, module_name) in resolved:
            return
        logger.debug(f"Extracting dependencies for {module_name}")
        dependency_chain.append(module_name)

        for lib_name, modules in manifest.get("dependencies", {}).items():
            lib_name = resolve_library_name(lib_name, library)
            for module in modules:
                logger.debug(f"Processing dependency {module} in library {lib_name}")
                if module in dependency_chain:
                    cycle_start = dependency_chain.index(module)
                    raise CircularDependencyError(dependency_chain[cycle_start:] + [module])

                # Recurse first so deeper dependencies are collected before this one.
                dep_manifest = manifests_by_module.get(module)
                if dep_manifest is None:
                    raise MissingManifestError(module, required_by=module_name)
                _collect_dependencies_of(dep_manifest, lib_name)

                dep_tuple = (lib_name, module)
                if dep_tuple not in collected_deps:
                    collected_deps.append(dep_tuple)

        dependency_chain.pop()
        resolved.add((library, module_name))

    _collect_dependencies_of(top_manifest, work)
    return collected_deps


def order_libraries(
    manifests_by_module: Dict[str, Manifest], dependencies: List[Dependency]
) -> List[str]:
    """Return the libraries used in ``dependencies`` in compile order.

    Each library comes after the libraries its modules depend on. When libraries
    depend on each other in a loop, no such order exists: a warning names the loop
    and a best-effort order is returned, which tools that sort files themselves
    can still use.
    """
    libraries = remove_duplicates_keeping_first(library for library, _ in dependencies)
    used_libraries: Dict[str, Set[str]] = {library: set() for library in libraries}
    for library, module in dependencies:
        manifest = manifests_by_module[module]
        for declared_library, modules in manifest.get("dependencies", {}).items():
            used_library = resolve_library_name(declared_library, library)
            if modules and used_library != library:
                used_libraries[library].add(used_library)

    ordered: List[str] = []
    while len(ordered) < len(libraries):
        remaining = [library for library in libraries if library not in ordered]
        ready = [library for library in remaining if used_libraries[library] <= set(ordered)]
        if not ready:
            loop = _find_library_loop(remaining[0], used_libraries, ordered)
            logger.warning(
                f"Libraries depend on each other in a loop ({' -> '.join(loop)}), so no "
                "library order is valid. Writing a best-effort order: tools that compile "
                "one library at a time may fail."
            )
            ready = remaining
        ordered.append(ready[0])
    return ordered


def _find_library_loop(
    start: str, used_libraries: Dict[str, Set[str]], ordered: List[str]
) -> List[str]:
    # Every library still unordered uses at least one other unordered library,
    # so following those edges from any of them must eventually revisit one.
    path = [start]
    while True:
        next_library = min(used_libraries[path[-1]] - set(ordered))
        if next_library in path:
            return path[path.index(next_library) :] + [next_library]
        path.append(next_library)


def validate_top_dir(top_dir: StrPath) -> bool:
    return pathlib.Path(top_dir).is_dir()


def to_absolute_path(cwd: StrPath, path: StrPath) -> pathlib.Path:
    """Return ``path`` as an absolute path, resolving a relative one against ``cwd``."""
    path = pathlib.Path(path)
    if not path.is_absolute():
        return (pathlib.Path(cwd) / path).resolve()
    return path


def configure_logging(verbosity: int = 0, log_file: Optional[StrPath] = None) -> logging.Logger:
    """Configure logging for the ``ohsh`` package.

    Handlers are attached to the package logger (``ohsh``) so that messages from
    every submodule are captured. Console output goes to stderr and shows
    warnings and errors only, INFO messages with ``verbosity`` 1, and DEBUG
    messages with 2 or more. A file handler, which always records DEBUG, is only
    added when ``log_file`` is given.
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
    console_handler.setLevel(CONSOLE_LEVEL_BY_VERBOSITY.get(verbosity, logging.DEBUG))
    console_handler.setFormatter(formatter)
    pkg_logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        pkg_logger.addHandler(file_handler)

    return pkg_logger


def discover_manifests(top_dir: StrPath) -> List[pathlib.Path]:
    logger.debug(f"Discovering manifest files in {top_dir}")
    manifest_files = list(pathlib.Path(top_dir).rglob("manifest*.json"))
    for manifest in manifest_files:
        logger.debug(f"Found manifest file: {manifest}")
    logger.info(f"Found {len(manifest_files)} manifest files in {top_dir}")
    return manifest_files
