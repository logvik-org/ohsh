# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys
from typing import NoReturn

from .utils import (
    EXIT_CANNOT_CREATE_OUTPUT,
    EXIT_CIRCULAR_DEPENDENCY,
    EXIT_DATA_ERROR,
    EXIT_DUPLICATE_MODULE,
    EXIT_MANIFEST_NOT_FOUND,
    EXIT_MODULE_NOT_FOUND,
    EXIT_NO_INPUT,
    CircularDependencyError,
    InvalidManifestError,
    Manifest,
    MissingManifestError,
    discover_manifests,
    extract_dependencies,
    find_duplicate_modules,
    order_libraries,
    remove_duplicates_keeping_first,
    to_absolute_path,
    validate_manifest,
    validate_top_dir,
)

SYSTEMVERILOG_EXTENSIONS = {".v", ".sv", ".svp", ".vh", ".svh"}
VHDL_EXTENSIONS = {".vhd", ".vhdl", ".vo"}

LIBRARY_ORDER_FILE_NAME = "libraries.src"

logger = logging.getLogger(__name__)


def _exit_with_error(message: str, code: int) -> NoReturn:
    logger.error(message)
    sys.exit(code)


def run(args: argparse.Namespace, cwd: pathlib.Path) -> None:
    """Resolve ``args.module`` and write its source lists to ``args.output``.

    ``args`` holds the options defined by ``cli.build_parser``. On any error the
    process exits with one of the ``EXIT_*`` codes.
    """
    module = args.module
    top_dir = args.top_dir
    work = args.work

    # If the top-level directory is a relative path, make it absolute.
    top_dir = to_absolute_path(cwd, top_dir)

    # Check if top-level is a directory and exists
    if not validate_top_dir(top_dir):
        _exit_with_error(
            f"The specified top-level directory {top_dir} does not exist or is not a directory.",
            EXIT_NO_INPUT,
        )

    # Find all files named "manifest.json" in the current working directory
    all_manifest_files = discover_manifests(top_dir)

    # parse all manifest files
    manifest_data: list[Manifest] = []
    for manifest_file in all_manifest_files:
        try:
            with open(manifest_file, encoding="utf-8") as file:
                data = json.load(file)
            validate_manifest(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            _exit_with_error(f"Error parsing JSON from {manifest_file}: {e}", EXIT_DATA_ERROR)
        except InvalidManifestError as e:
            _exit_with_error(f"Invalid manifest {manifest_file}: {e}", EXIT_DATA_ERROR)
        except OSError as e:
            _exit_with_error(f"File error reading {manifest_file}: {e}", EXIT_NO_INPUT)
        data["manifest_path"] = str(manifest_file.resolve())
        manifest_data.append(data)
        logger.debug(f"Parsed manifest file: {manifest_file}")

    # Every lookup by module name below relies on the names being unique.
    duplicates = find_duplicate_modules(manifest_data)
    if duplicates:
        listing = "\n".join(
            f"  {name}: {', '.join(sorted(paths))}" for name, paths in sorted(duplicates.items())
        )
        _exit_with_error(
            f"Each module must be declared in exactly one manifest, but these are not:\n{listing}",
            EXIT_DUPLICATE_MODULE,
        )

    manifests_by_module = {manifest["module"]: manifest for manifest in manifest_data}

    top_manifest = manifests_by_module.get(module)
    if top_manifest is None:
        _exit_with_error(
            f"The specified module {module} was not found in any manifest.", EXIT_MODULE_NOT_FOUND
        )
    logger.debug(f"Found module {module} in manifest.")

    # Extract dependencies recursively
    try:
        dependencies = extract_dependencies(manifests_by_module, top_manifest, work)
    except CircularDependencyError as e:
        _exit_with_error(f"Circular dependency detected: {e}", EXIT_CIRCULAR_DEPENDENCY)
    except MissingManifestError as e:
        _exit_with_error(f"Missing dependency: {e}", EXIT_MANIFEST_NOT_FOUND)

    # Remove duplicate entries
    dependencies = remove_duplicates_keeping_first(dependencies)
    logger.debug(f"Dependencies for module {module}: {dependencies}")

    # Append the top manifest module with the work library to the dependencies list
    dependencies.append((work, module))

    logger.debug(f"Complete module list: {dependencies}")

    library_order = order_libraries(manifests_by_module, dependencies)
    logger.info(f"Library compile order: {', '.join(library_order)}")

    # Extract source file list from all modules in the final dependencies list
    source_files_by_lib: dict[str, dict[str, list[str]]] = {}
    for lib_name, module in dependencies:
        # Separate SystemVerilog and VHDL files
        systemverilog_sources = []
        vhdl_sources = []

        manifest = manifests_by_module[module]
        manifest_path = pathlib.Path(manifest["manifest_path"]).parent
        module_sources = [str(manifest_path / source) for source in manifest.get("sources", [])]
        for source in module_sources:
            extension = pathlib.Path(source).suffix.lower()
            if extension in SYSTEMVERILOG_EXTENSIONS:
                systemverilog_sources.append(source)
            elif extension in VHDL_EXTENSIONS:
                vhdl_sources.append(source)
            else:
                logger.warning(f"Skipping {source} in module {module}: unknown file extension")

        # If the library already exists in the source_files_by_lib dictionary, append the source files
        if lib_name in source_files_by_lib:
            source_files_by_lib[lib_name]["systemverilog"].extend(systemverilog_sources)
            source_files_by_lib[lib_name]["vhdl"].extend(vhdl_sources)
        else:  # Otherwise, create a new entry in the dictionary and add the source files
            source_files_by_lib[lib_name] = {
                "systemverilog": systemverilog_sources,
                "vhdl": vhdl_sources,
            }

    # Two modules in one library may list the same file, which must be compiled only once.
    # `sources` is the dict stored in source_files_by_lib, not a copy, so assigning to its
    # keys updates source_files_by_lib itself.
    for lib_name, sources in source_files_by_lib.items():
        sources["systemverilog"] = remove_duplicates_keeping_first(sources["systemverilog"])
        sources["vhdl"] = remove_duplicates_keeping_first(sources["vhdl"])
        logger.debug(
            f"Source files for library {lib_name}: SystemVerilog: {sources['systemverilog']}, VHDL: {sources['vhdl']}"
        )

    # Check that all source files exist
    missing_files = []
    for source_files in source_files_by_lib.values():
        for source_file in source_files["systemverilog"] + source_files["vhdl"]:
            if not pathlib.Path(source_file).exists():
                missing_files.append(source_file)

    if missing_files:
        _exit_with_error(f"The following source files do not exist: {missing_files}", EXIT_NO_INPUT)

    source_files_by_lib = {lib_name: source_files_by_lib[lib_name] for lib_name in library_order}

    # Write the source files to output files, one file per library
    output_dir = pathlib.Path(args.output)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        _exit_with_error(
            f"Cannot create output directory {output_dir}: {e}", EXIT_CANNOT_CREATE_OUTPUT
        )
    for lib_name, source_files in source_files_by_lib.items():
        systemverilog_output_file = output_dir / f"{lib_name}_systemverilog.src"
        vhdl_output_file = output_dir / f"{lib_name}_vhdl.src"

        if source_files["systemverilog"]:
            with open(systemverilog_output_file, "w", encoding="utf-8") as f:
                for source_file in source_files["systemverilog"]:
                    f.write(f"{source_file}\n")
            logger.info(
                f"Wrote {len(source_files['systemverilog'])} SystemVerilog files for library {lib_name} "
                f"to {systemverilog_output_file}"
            )
        else:
            logger.debug(
                f"No SystemVerilog source files for library {lib_name}, skipping file creation."
            )

        if source_files["vhdl"]:
            with open(vhdl_output_file, "w", encoding="utf-8") as f:
                for source_file in source_files["vhdl"]:
                    f.write(f"{source_file}\n")
            logger.info(
                f"Wrote {len(source_files['vhdl'])} VHDL files for library {lib_name} "
                f"to {vhdl_output_file}"
            )
        else:
            logger.debug(f"No VHDL source files for library {lib_name}, skipping file creation.")

    library_order_file = output_dir / LIBRARY_ORDER_FILE_NAME
    with open(library_order_file, "w", encoding="utf-8") as f:
        for lib_name in library_order:
            f.write(f"{lib_name}\n")
    logger.info(f"Wrote library compile order to {library_order_file}")
