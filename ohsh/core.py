# SPDX-License-Identifier: Apache-2.0

import argparse
import json
import logging
import pathlib
import sys
from typing import Dict, List, NoReturn, Optional

from .utils import (
    EXIT_CANNOT_CREATE_OUTPUT,
    EXIT_CIRCULAR_DEPENDENCY,
    EXIT_DATA_ERROR,
    EXIT_DUPLICATE_MODULE,
    EXIT_MANIFEST_NOT_FOUND,
    EXIT_MODULE_NOT_FOUND,
    EXIT_NO_INPUT,
    CircularDependencyError,
    Dependency,
    InvalidManifestError,
    Manifest,
    MissingManifestError,
    StrPath,
    discover_manifests,
    extract_dependencies,
    find_duplicate_modules,
    order_libraries,
    remove_duplicates_keeping_first,
    to_absolute_path,
    validate_manifest,
    validate_top_dir,
)

EXTENSIONS_BY_LANGUAGE = {
    "systemverilog": {".v", ".sv", ".svp", ".vh", ".svh"},
    "vhdl": {".vhd", ".vhdl", ".vo"},
}
LANGUAGE_DISPLAY_NAMES = {"systemverilog": "SystemVerilog", "vhdl": "VHDL"}

LIBRARY_ORDER_FILE_NAME = "libraries.src"

# Source file paths of one library, keyed by language.
SourcesByLanguage = Dict[str, List[str]]

logger = logging.getLogger(__name__)


def exit_with_error(message: str, code: int) -> NoReturn:
    logger.error(message)
    sys.exit(code)


def load_manifests(top_dir: pathlib.Path) -> List[Manifest]:
    manifests: List[Manifest] = []
    for manifest_file in discover_manifests(top_dir):
        try:
            with open(manifest_file, encoding="utf-8") as file:
                manifest = json.load(file)
            validate_manifest(manifest)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            exit_with_error(f"Error parsing JSON from {manifest_file}: {e}", EXIT_DATA_ERROR)
        except InvalidManifestError as e:
            exit_with_error(f"Invalid manifest {manifest_file}: {e}", EXIT_DATA_ERROR)
        except OSError as e:
            exit_with_error(f"File error reading {manifest_file}: {e}", EXIT_NO_INPUT)
        manifest["manifest_path"] = str(manifest_file.resolve())
        manifests.append(manifest)
        logger.debug(f"Parsed manifest file: {manifest_file}")
    return manifests


def resolve_top_dir(cwd: pathlib.Path, top_dir: StrPath) -> pathlib.Path:
    absolute_top_dir = to_absolute_path(cwd, top_dir)
    if not validate_top_dir(absolute_top_dir):
        exit_with_error(
            f"The specified top-level directory {absolute_top_dir} does not exist "
            "or is not a directory.",
            EXIT_NO_INPUT,
        )
    return absolute_top_dir


def index_manifests_by_module(manifests: List[Manifest]) -> Dict[str, Manifest]:
    duplicates = find_duplicate_modules(manifests)
    if duplicates:
        listing = "\n".join(
            f"  {name}: {', '.join(sorted(paths))}" for name, paths in sorted(duplicates.items())
        )
        exit_with_error(
            f"Each module must be declared in exactly one manifest, but these are not:\n{listing}",
            EXIT_DUPLICATE_MODULE,
        )
    return {manifest["module"]: manifest for manifest in manifests}


def find_manifest(manifests_by_module: Dict[str, Manifest], module: str) -> Manifest:
    manifest = manifests_by_module.get(module)
    if manifest is None:
        exit_with_error(
            f"The specified module {module} was not found in any manifest.",
            EXIT_MODULE_NOT_FOUND,
        )
    logger.debug(f"Found module {module} in manifest.")
    return manifest


def _resolve_module_list(
    manifests_by_module: Dict[str, Manifest], top_module: str, work: str
) -> List[Dependency]:
    """Return every module needed to build ``top_module``, ending with ``top_module`` itself."""
    top_manifest = find_manifest(manifests_by_module, top_module)

    try:
        dependencies = extract_dependencies(manifests_by_module, top_manifest, work)
    except CircularDependencyError as e:
        exit_with_error(f"Circular dependency detected: {e}", EXIT_CIRCULAR_DEPENDENCY)
    except MissingManifestError as e:
        exit_with_error(f"Missing dependency: {e}", EXIT_MANIFEST_NOT_FOUND)

    dependencies = remove_duplicates_keeping_first(dependencies)
    logger.debug(f"Dependencies for module {top_module}: {dependencies}")

    module_list = dependencies + [(work, top_module)]
    logger.debug(f"Complete module list: {module_list}")
    return module_list


def find_language(source: str) -> Optional[str]:
    extension = pathlib.Path(source).suffix.lower()
    for language, extensions in EXTENSIONS_BY_LANGUAGE.items():
        if extension in extensions:
            return language
    return None


def _collect_sources_by_library(
    manifests_by_module: Dict[str, Manifest], module_list: List[Dependency]
) -> Dict[str, SourcesByLanguage]:
    sources_by_library: Dict[str, SourcesByLanguage] = {}
    for lib_name, module in module_list:
        manifest = manifests_by_module[module]
        manifest_dir = pathlib.Path(manifest["manifest_path"]).parent
        library_sources = sources_by_library.setdefault(
            lib_name, {language: [] for language in EXTENSIONS_BY_LANGUAGE}
        )
        for relative_source in manifest.get("sources", []):
            source = str(manifest_dir / relative_source)
            language = find_language(source)
            if language is None:
                logger.warning(f"Skipping {source} in module {module}: unknown file extension")
                continue
            library_sources[language].append(source)

    # Two modules in one library may list the same file, which must be compiled only once.
    for lib_name, library_sources in sources_by_library.items():
        for language, sources in library_sources.items():
            library_sources[language] = remove_duplicates_keeping_first(sources)
        listing = ", ".join(
            f"{LANGUAGE_DISPLAY_NAMES[language]}: {sources}"
            for language, sources in library_sources.items()
        )
        logger.debug(f"Source files for library {lib_name}: {listing}")
    return sources_by_library


def _exit_if_sources_missing(sources_by_library: Dict[str, SourcesByLanguage]) -> None:
    missing_files = [
        source
        for library_sources in sources_by_library.values()
        for sources in library_sources.values()
        for source in sources
        if not pathlib.Path(source).exists()
    ]
    if missing_files:
        exit_with_error(f"The following source files do not exist: {missing_files}", EXIT_NO_INPUT)


def _write_lines(output_file: pathlib.Path, lines: List[str]) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(f"{line}\n")


def _write_source_lists(
    output_dir: pathlib.Path,
    sources_by_library: Dict[str, SourcesByLanguage],
    library_order: List[str],
) -> None:
    """Write one source list per library and language, plus the library compile order."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        exit_with_error(
            f"Cannot create output directory {output_dir}: {e}", EXIT_CANNOT_CREATE_OUTPUT
        )

    for lib_name in library_order:
        for language, sources in sources_by_library[lib_name].items():
            display_name = LANGUAGE_DISPLAY_NAMES[language]
            if not sources:
                logger.debug(
                    f"No {display_name} source files for library {lib_name}, "
                    "skipping file creation."
                )
                continue
            output_file = output_dir / f"{lib_name}_{language}.src"
            _write_lines(output_file, sources)
            logger.info(
                f"Wrote {len(sources)} {display_name} files for library {lib_name} to {output_file}"
            )

    library_order_file = output_dir / LIBRARY_ORDER_FILE_NAME
    _write_lines(library_order_file, library_order)
    logger.info(f"Wrote library compile order to {library_order_file}")


def run(args: argparse.Namespace, cwd: pathlib.Path) -> None:
    """Resolve ``args.module`` and write its source lists to ``args.output``.

    ``args`` holds the options defined by ``cli.build_parser``. On any error the
    process exits with one of the ``EXIT_*`` codes.
    """
    top_dir = resolve_top_dir(cwd, args.top_dir)
    manifests_by_module = index_manifests_by_module(load_manifests(top_dir))
    module_list = _resolve_module_list(manifests_by_module, args.module, args.work)

    library_order = order_libraries(manifests_by_module, module_list)
    logger.info(f"Library compile order: {', '.join(library_order)}")

    sources_by_library = _collect_sources_by_library(manifests_by_module, module_list)
    _exit_if_sources_missing(sources_by_library)
    _write_source_lists(pathlib.Path(args.output), sources_by_library, library_order)
