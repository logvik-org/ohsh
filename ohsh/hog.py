# SPDX-License-Identifier: Apache-2.0
"""Write the list files of a hog (HDL on git) project.

hog reads ``Top/<project>/list/<library>.src``, takes the library from the file
name, and resolves each entry against the repository root.
"""

import argparse
import logging
import os
import pathlib
from typing import List, Optional

from .core import create_output_dir, resolve_relative_base, resolve_sources, write_lines
from .scan import scan_source

logger = logging.getLogger(__name__)


def _find_source_declaring(unit: str, sources: List[str]) -> Optional[str]:
    for source in sources:
        if unit.lower() in scan_source(pathlib.Path(source)).declared_units:
            return source
    return None


def write_hog_lists(args: argparse.Namespace, cwd: pathlib.Path) -> None:
    """Resolve ``args.module`` and write one hog list file per library to ``args.output``.

    ``args`` holds the options defined by ``cli.build_parser``, with
    ``relative_to`` set to the root of the hog repository.
    """
    library_order, sources_by_library = resolve_sources(args, cwd)
    repository_root = resolve_relative_base(args, cwd)
    output_dir = pathlib.Path(args.output)
    create_output_dir(output_dir)

    # hog leaves the compile order to the vendor tool, so the languages of a
    # library can share one list.
    sources_by_library_name = {
        lib_name: [
            source for sources in sources_by_library[lib_name].values() for source in sources
        ]
        for lib_name in library_order
    }
    top_source = _find_source_declaring(args.module, sources_by_library_name[args.work])
    if top_source is None:
        logger.warning(
            f"No source of library {args.work} declares {args.module}, so no file is marked "
            f"top={args.module} and hog will look for a top named top_<project>."
        )

    for lib_name, sources in sources_by_library_name.items():
        entries = []
        for source in sources:
            # Tcl reads forward slashes on every platform.
            entry = pathlib.PurePath(os.path.relpath(source, repository_root)).as_posix()
            if source == top_source:
                entry += f" top={args.module}"
            entries.append(entry)
        list_file = output_dir / f"{lib_name}.src"
        write_lines(list_file, entries)
        logger.info(f"Wrote {len(entries)} files for library {lib_name} to {list_file}")
