# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pathlib

from .utils import (
    EXIT_CANNOT_CREATE_OUTPUT,
    EXIT_CIRCULAR_DEPENDENCY,
    EXIT_DATA_ERROR,
    EXIT_MANIFEST_NOT_FOUND,
    EXIT_MODULE_NOT_FOUND,
    EXIT_NO_INPUT,
    CircularDependencyError,
    InvalidManifestError,
    MissingManifestError,
    discover_manifests,
    extract_dependencies,
    find_manifest,
    order_libraries,
    to_absolute_path,
    validate_manifest,
    validate_top_dir,
)

valid_verilog_endings = [".v", ".sv", ".svp"]
valid_vhdl_endings = [".vhd", ".vhdl", ".vo"]

LIBRARY_ORDER_FILE_NAME = "libraries.src"

logger = logging.getLogger(__name__)


def run(args, cwd):
    module = args.module
    top_dir = args.top_dir
    work = args.work

    # If the top-level directory is a relative path, make it absolute.
    top_dir = to_absolute_path(cwd, top_dir)

    # Check if top-level is a directory and exists
    if not validate_top_dir(top_dir):
        error_message = (
            f"The specified top-level directory {top_dir} does not exist or is not a directory."
        )
        logger.error(error_message)
        exit(EXIT_NO_INPUT)

    # Find all files named "manifest.json" in the current working directory
    all_manifest_files = discover_manifests(top_dir)

    # parse all manifest files
    manifest_data = []
    for manifest_file in all_manifest_files:
        try:
            with open(manifest_file, encoding="utf-8") as file:
                data = json.load(file)
            validate_manifest(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Error parsing JSON from {manifest_file}: {e}")
            exit(EXIT_DATA_ERROR)
        except InvalidManifestError as e:
            logger.error(f"Invalid manifest {manifest_file}: {e}")
            exit(EXIT_DATA_ERROR)
        except OSError as e:
            logger.error(f"File error reading {manifest_file}: {e}")
            exit(EXIT_NO_INPUT)
        data["manifest_path"] = str(manifest_file.resolve())
        manifest_data.append(data)
        logger.debug(f"Parsed manifest file: {manifest_file}")

    # Check if the specified module is found within the list of manifests
    module_found = False
    top_manifest = None
    for manifest in manifest_data:
        if manifest.get("module") == module:
            module_found = True
            top_manifest = manifest

    if not module_found:
        error_message = f"The specified module {module} was not found in any manifest."
        logger.error(error_message)
        exit(EXIT_MODULE_NOT_FOUND)
    else:
        logger.debug(f"Found module {module} in manifest.")

    # Extract dependencies recursively
    try:
        dependencies = extract_dependencies(manifest_data, top_manifest, work)
    except CircularDependencyError as e:
        logger.error(f"Circular dependency detected: {e}")
        exit(EXIT_CIRCULAR_DEPENDENCY)
    except MissingManifestError as e:
        logger.error(f"Missing dependency: {e}")
        exit(EXIT_MANIFEST_NOT_FOUND)

    # Remove duplicate entries
    dependencies = list(dict.fromkeys(dependencies))
    logger.debug(f"Dependencies for module {module}: {dependencies}")

    # Append the top manifest module with the work library to the dependencies list
    dependencies.append((work, module))

    logger.debug(f"Complete module list: {dependencies}")

    library_order = order_libraries(manifest_data, dependencies)
    logger.info(f"Library compile order: {', '.join(library_order)}")

    # Extract source file list from all modules in the final dependencies list
    source_files_by_lib = {}
    for lib_name, module in dependencies:
        # Separate Verilog and VHDL files
        verilog_sources = []
        vhdl_sources = []

        manifest = find_manifest(manifest_data, module)
        manifest_path = pathlib.Path(manifest["manifest_path"]).parent
        sources = [str(manifest_path / source) for source in manifest.get("sources", [])]
        for source in sources:
            if any(source.endswith(ext) for ext in valid_verilog_endings):
                verilog_sources.append(source)
            elif any(source.endswith(ext) for ext in valid_vhdl_endings):
                vhdl_sources.append(source)

        # If the library already exists in the source_files_by_lib dictionary, append the source files
        if lib_name in source_files_by_lib:
            source_files_by_lib[lib_name]["verilog"].extend(verilog_sources)
            source_files_by_lib[lib_name]["vhdl"].extend(vhdl_sources)
        else:  # Otherwise, create a new entry in the dictionary and add the source files
            source_files_by_lib[lib_name] = {
                "verilog": verilog_sources,
                "vhdl": vhdl_sources,
            }

    # Remove duplicate source files while preserving order within each library
    for lib_name, sources in source_files_by_lib.items():
        sources["verilog"] = list(dict.fromkeys(sources["verilog"]))
        sources["vhdl"] = list(dict.fromkeys(sources["vhdl"]))
        logger.debug(
            f"Source files for library {lib_name}: Verilog: {sources['verilog']}, VHDL: {sources['vhdl']}"
        )

    # Check that all source files exist
    missing_files = []
    for source_files in source_files_by_lib.values():
        for source_file in source_files["verilog"] + source_files["vhdl"]:
            if not pathlib.Path(source_file).exists():
                missing_files.append(source_file)

    if missing_files:
        error_message = f"The following source files do not exist: {missing_files}"
        logger.error(error_message)
        exit(EXIT_NO_INPUT)

    source_files_by_lib = {lib_name: source_files_by_lib[lib_name] for lib_name in library_order}

    # Write the source files to output files, one file per library
    output_dir = pathlib.Path(args.output)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Cannot create output directory {output_dir}: {e}")
        exit(EXIT_CANNOT_CREATE_OUTPUT)
    for lib_name, source_files in source_files_by_lib.items():
        verilog_output_file = output_dir / f"{lib_name}_verilog.src"
        vhdl_output_file = output_dir / f"{lib_name}_vhdl.src"

        if source_files["verilog"]:
            with open(verilog_output_file, "w", encoding="utf-8") as f:
                for source_file in source_files["verilog"]:
                    f.write(f"{source_file}\n")
            logger.info(
                f"Wrote {len(source_files['verilog'])} Verilog files for library {lib_name} "
                f"to {verilog_output_file}"
            )
        else:
            logger.debug(f"No Verilog source files for library {lib_name}, skipping file creation.")

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
