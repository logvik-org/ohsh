# SPDX-License-Identifier: Apache-2.0
"""Create manifests for a source tree and keep existing ones in line with their sources."""

import argparse
import fnmatch
import json
import logging
import os
import pathlib
import re
import sys
from collections import Counter
from typing import Dict, Iterable, List, NamedTuple, Set, Tuple

from .core import (
    find_language,
    find_manifest,
    index_manifests_by_module,
    load_manifests,
    resolve_top_dir,
)
from .scan import ScannedSource, scan_source
from .utils import EXIT_MANIFEST_OUTDATED, Dependency, Manifest

# A directory with one of these names holds the sources of the module in its parent.
SOURCE_DIRECTORY_NAMES = {"hdl", "rtl", "src"}
NEW_MANIFEST_NAME = "manifest.json"
NEW_MANIFEST_INDENT = 2

logger = logging.getLogger(__name__)


class ManifestReview(NamedTuple):
    sorted_sources: List[str]
    missing_dependencies: List[Dependency]
    unreferenced_dependencies: List[Dependency]
    # Unit name to the modules that declare it, when ohsh cannot tell which one is meant.
    ambiguous_units: Dict[str, List[str]]


def _source_paths(manifest: Manifest) -> List[pathlib.Path]:
    manifest_dir = pathlib.Path(manifest["manifest_path"]).parent
    return [manifest_dir / source for source in manifest.get("sources", [])]


def _scan_modules(manifests: Iterable[Manifest]) -> Dict[str, List[ScannedSource]]:
    """Return the scan of every source of every module, in the order the manifest lists them."""
    scans_by_path: Dict[pathlib.Path, ScannedSource] = {}
    scans_by_module: Dict[str, List[ScannedSource]] = {}
    for manifest in manifests:
        scans = []
        for source in _source_paths(manifest):
            if not source.is_file():
                logger.warning(f"Source file {source} of module {manifest['module']} is missing")
            path = source.resolve()
            if path not in scans_by_path:
                scans_by_path[path] = scan_source(path)
            scans.append(scans_by_path[path])
        scans_by_module[manifest["module"]] = scans
    return scans_by_module


def _index_modules_by_unit(scans_by_module: Dict[str, List[ScannedSource]]) -> Dict[str, Set[str]]:
    modules_by_unit: Dict[str, Set[str]] = {}
    for module, scans in scans_by_module.items():
        for scan in scans:
            for unit in scan.declared_units:
                modules_by_unit.setdefault(unit, set()).add(module)
    return modules_by_unit


def _declared_dependencies(manifest: Manifest) -> List[Dependency]:
    return [
        (library, module)
        for library, modules in manifest.get("dependencies", {}).items()
        for module in modules
    ]


def _sort_sources(sources: List[str], scans: List[ScannedSource]) -> List[str]:
    """Return ``sources`` with every file after the files of the same module it uses.

    An order that is already valid comes back unchanged. So does one where the
    files use each other in a loop, which no order can satisfy.
    """
    indexes_by_unit: Dict[str, List[int]] = {}
    for index, scan in enumerate(scans):
        for unit in scan.declared_units:
            indexes_by_unit.setdefault(unit, []).append(index)

    ordered: List[int] = []
    in_progress: Set[int] = set()

    def _place_after_its_dependencies(index: int) -> bool:
        if index in ordered:
            return True
        if index in in_progress:
            return False
        in_progress.add(index)
        used_units = {unit for _, unit in scans[index].references} - scans[index].declared_units
        for used_index in sorted({i for unit in used_units for i in indexes_by_unit.get(unit, [])}):
            if not _place_after_its_dependencies(used_index):
                return False
        ordered.append(index)
        return True

    if not all(_place_after_its_dependencies(index) for index in range(len(sources))):
        logger.warning(f"Sources {sources} use each other in a loop, leaving their order as it is")
        return list(sources)
    return [sources[index] for index in ordered]


def _review_manifest(
    manifest: Manifest,
    scans_by_module: Dict[str, List[ScannedSource]],
    modules_by_unit: Dict[str, Set[str]],
) -> ManifestReview:
    module = manifest["module"]
    scans = scans_by_module[module]
    declared = _declared_dependencies(manifest)
    own_units = {unit for scan in scans for unit in scan.declared_units}
    missing: List[Dependency] = []
    referenced: Set[Dependency] = set()
    ambiguous_units: Dict[str, List[str]] = {}

    # References that name a library go first, so one without a library can
    # settle for the library a dependency was just added under.
    references = sorted(
        {reference for scan in scans for reference in scan.references},
        key=lambda reference: (reference[0] is None, reference),
    )
    for library, unit in references:
        candidates = modules_by_unit.get(unit, set()) - {module}
        if unit in own_units or not candidates:
            continue
        satisfying = [
            dependency
            for dependency in declared + missing
            if dependency[1] in candidates and library in (None, dependency[0])
        ]
        if satisfying:
            referenced.update(satisfying)
        elif len(candidates) == 1:
            missing.append((library or "work", next(iter(candidates))))
        else:
            ambiguous_units[unit] = sorted(candidates)

    return ManifestReview(
        sorted_sources=_sort_sources(manifest.get("sources", []), scans),
        missing_dependencies=missing,
        unreferenced_dependencies=[d for d in declared if d not in referenced],
        ambiguous_units=ambiguous_units,
    )


def _review_manifests(manifests: List[Manifest]) -> Dict[str, ManifestReview]:
    scans_by_module = _scan_modules(manifests)
    modules_by_unit = _index_modules_by_unit(scans_by_module)
    return {
        manifest["module"]: _review_manifest(manifest, scans_by_module, modules_by_unit)
        for manifest in manifests
    }


def _apply_review(manifest: Manifest, review: ManifestReview) -> None:
    if "sources" in manifest:
        manifest["sources"] = review.sorted_sources
    for library, module in review.missing_dependencies:
        manifest.setdefault("dependencies", {}).setdefault(library, []).append(module)


def _describe_dependency(dependency: Dependency) -> str:
    library, module = dependency
    return f"{module} (library {library})"


def _describe_problems(manifest: Manifest, review: ManifestReview) -> List[str]:
    problems = [
        f"missing dependency: {_describe_dependency(dependency)}"
        for dependency in review.missing_dependencies
    ]
    if review.sorted_sources != manifest.get("sources", []):
        problems.append(f"sources out of order, expected: {', '.join(review.sorted_sources)}")
    return problems


def _describe_notes(review: ManifestReview) -> List[str]:
    notes = [
        f"note: no source ohsh can read uses the dependency {_describe_dependency(dependency)}"
        for dependency in review.unreferenced_dependencies
    ]
    notes += [
        f"note: {unit} is declared by modules {', '.join(modules)}, add the one you mean by hand"
        for unit, modules in sorted(review.ambiguous_units.items())
    ]
    return notes


def _print_report(title: str, lines: List[str]) -> None:
    print(title)
    for line in lines:
        print(f"  {line}")


def _relative_manifest_path(manifest: Manifest, top_dir: pathlib.Path) -> str:
    return os.path.relpath(manifest["manifest_path"], str(top_dir))


def _detect_indent(manifest_text: str) -> int:
    indented_line = re.search(r"^( +)\S", manifest_text, re.M)
    return len(indented_line.group(1)) if indented_line else NEW_MANIFEST_INDENT


def _format_manifest(manifest: Manifest, indent: int) -> str:
    content = {key: value for key, value in manifest.items() if key != "manifest_path"}
    return json.dumps(content, indent=indent)


def _write_manifest(manifest: Manifest, indent: int) -> None:
    with open(manifest["manifest_path"], "w", encoding="utf-8") as file:
        file.write(_format_manifest(manifest, indent) + "\n")


def _load_sorted_manifests(top_dir: pathlib.Path) -> List[Manifest]:
    manifests = load_manifests(top_dir)
    # Called for its check: it exits when two manifests declare the same module.
    index_manifests_by_module(manifests)
    return sorted(manifests, key=lambda manifest: str(manifest["manifest_path"]))


def _select_manifests(
    manifests: List[Manifest], reviews: Dict[str, ManifestReview], args: argparse.Namespace
) -> List[Manifest]:
    """Return the manifests ``args`` asks for: all of them, or ``args.module`` and what it needs.

    Dependencies the module lacks count as needed too, so the selection is the
    same before and after a fix. ``args.no_deps`` leaves out all dependencies.
    """
    if args.module is None:
        return manifests
    manifests_by_module = {manifest["module"]: manifest for manifest in manifests}
    selected = {find_manifest(manifests_by_module, args.module)["module"]}
    pending = [] if args.no_deps else [args.module]
    while pending:
        module = pending.pop()
        dependencies = (
            _declared_dependencies(manifests_by_module[module])
            + reviews[module].missing_dependencies
        )
        for _, dependency in dependencies:
            if dependency in manifests_by_module and dependency not in selected:
                selected.add(dependency)
                pending.append(dependency)
    return [manifest for manifest in manifests if manifest["module"] in selected]


def _review_selected_manifests(
    args: argparse.Namespace, top_dir: pathlib.Path
) -> List[Tuple[Manifest, ManifestReview]]:
    manifests = _load_sorted_manifests(top_dir)
    # Every manifest is reviewed, because which module declares a unit can only
    # be known from all of them.
    reviews = _review_manifests(manifests)
    return [
        (manifest, reviews[manifest["module"]])
        for manifest in _select_manifests(manifests, reviews, args)
    ]


def check_manifests(args: argparse.Namespace, cwd: pathlib.Path) -> None:
    """Report the manifests under ``args.top_dir`` that do not match their sources.

    With ``args.module`` set, only that module and its dependencies are checked.
    Exits with ``EXIT_MANIFEST_OUTDATED`` when a manifest lacks a dependency or
    lists its sources in an order that does not compile. Notes do not fail the check.
    """
    top_dir = resolve_top_dir(cwd, args.top_dir)
    reviewed_manifests = _review_selected_manifests(args, top_dir)

    outdated_count = 0
    for manifest, review in reviewed_manifests:
        problems = _describe_problems(manifest, review)
        outdated_count += bool(problems)
        lines = problems + _describe_notes(review)
        if lines:
            _print_report(_relative_manifest_path(manifest, top_dir), lines)

    if outdated_count:
        print(
            f"{outdated_count} of {len(reviewed_manifests)} manifests need fixing, run ohsh --fix"
        )
        sys.exit(EXIT_MANIFEST_OUTDATED)
    print(f"All {len(reviewed_manifests)} manifests match their sources")


def fix_manifests(args: argparse.Namespace, cwd: pathlib.Path) -> None:
    """Add missing dependencies to the manifests under ``args.top_dir`` and sort their sources.

    With ``args.module`` set, only that module and its dependencies are fixed.
    Dependencies are only ever added: a source ohsh cannot read may need one
    that looks unused.
    """
    top_dir = resolve_top_dir(cwd, args.top_dir)
    for manifest, review in _review_selected_manifests(args, top_dir):
        problems = _describe_problems(manifest, review)
        if not problems:
            continue
        manifest_path = pathlib.Path(manifest["manifest_path"])
        indent = _detect_indent(manifest_path.read_text(encoding="utf-8"))
        _apply_review(manifest, review)
        _write_manifest(manifest, indent)
        _print_report(f"Fixed {_relative_manifest_path(manifest, top_dir)}", problems)


def _is_excluded(directory: pathlib.Path, top_dir: pathlib.Path, patterns: List[str]) -> bool:
    relative_path = directory.relative_to(top_dir).as_posix()
    return directory.name.startswith(".") or any(
        fnmatch.fnmatch(directory.name, pattern) or fnmatch.fnmatch(relative_path, pattern)
        for pattern in patterns
    )


def _module_directory(source: pathlib.Path) -> pathlib.Path:
    directory = source.parent
    return directory.parent if directory.name in SOURCE_DIRECTORY_NAMES else directory


def _group_unlisted_sources(
    top_dir: pathlib.Path, listed_sources: Set[pathlib.Path], exclude_patterns: List[str]
) -> Dict[pathlib.Path, List[pathlib.Path]]:
    """Return the HDL sources no manifest lists, by the directory of the module they belong to.

    Directories that already hold a manifest are left alone.
    """
    sources_by_directory: Dict[pathlib.Path, List[pathlib.Path]] = {}
    for walked_directory, subdirectory_names, file_names in os.walk(str(top_dir)):
        directory = pathlib.Path(walked_directory)
        subdirectory_names[:] = sorted(
            name
            for name in subdirectory_names
            if not _is_excluded(directory / name, top_dir, exclude_patterns)
        )
        for file_name in sorted(file_names):
            source = directory / file_name
            if find_language(file_name) and source.resolve() not in listed_sources:
                sources_by_directory.setdefault(_module_directory(source), []).append(source)
    return {
        directory: sources
        for directory, sources in sources_by_directory.items()
        if not any(directory.glob("manifest*.json"))
    }


def _name_modules(
    directories: List[pathlib.Path], top_dir: pathlib.Path, taken_names: Set[str]
) -> Dict[pathlib.Path, str]:
    """Name each module after its directory, adding parent directories until the name is unique."""
    parts = {d: d.relative_to(top_dir).parts or (top_dir.name,) for d in directories}
    depths = {directory: 1 for directory in directories}

    def _name(directory: pathlib.Path) -> str:
        return "_".join(parts[directory][-depths[directory] :])

    while True:
        name_counts = Counter(_name(directory) for directory in directories)
        clashing = [
            directory
            for directory in directories
            if (name_counts[_name(directory)] > 1 or _name(directory) in taken_names)
            and depths[directory] < len(parts[directory])
        ]
        if not clashing:
            return {directory: _name(directory) for directory in directories}
        for directory in clashing:
            depths[directory] += 1


def _propose_manifests(
    top_dir: pathlib.Path, existing_manifests: List[Manifest], exclude_patterns: List[str]
) -> List[Tuple[Manifest, List[str]]]:
    """Return a manifest and the notes about it for each source directory without one."""
    listed_sources = {
        source.resolve() for manifest in existing_manifests for source in _source_paths(manifest)
    }
    sources_by_directory = _group_unlisted_sources(top_dir, listed_sources, exclude_patterns)
    names = _name_modules(
        list(sources_by_directory), top_dir, {manifest["module"] for manifest in existing_manifests}
    )
    proposals: List[Manifest] = [
        {
            "module": names[directory],
            "sources": [source.relative_to(directory).as_posix() for source in sources],
            "manifest_path": str(directory / NEW_MANIFEST_NAME),
        }
        for directory, sources in sources_by_directory.items()
    ]
    reviews = _review_manifests(existing_manifests + proposals)
    for proposal in proposals:
        _apply_review(proposal, reviews[proposal["module"]])
        for modules in proposal.get("dependencies", {}).values():
            modules.sort()
    return [(proposal, _describe_notes(reviews[proposal["module"]])) for proposal in proposals]


def _ask_to_create(manifest_path: str) -> str:
    while True:
        try:
            answer = input(f"Create {manifest_path}? [y]es, [n]o, [a]ll, [q]uit: ").strip().lower()
        except EOFError:
            return "q"
        if answer[:1] in ("y", "n", "a", "q"):
            return answer[:1]


def _print_modules_nothing_depends_on(created: List[Manifest], manifests: List[Manifest]) -> None:
    used_modules = {
        module for manifest in manifests for _, module in _declared_dependencies(manifest)
    }
    unused = sorted(m["module"] for m in created if m["module"] not in used_modules)
    if unused:
        print(
            f"Nothing depends on these new modules (top-levels or testbenches): {', '.join(unused)}"
        )


def create_manifests(args: argparse.Namespace, cwd: pathlib.Path) -> None:
    """Offer a manifest for every source directory under ``args.top_dir`` that has none.

    Each manifest is shown and only written after the user agrees, unless
    ``args.yes`` is set. Existing manifests are never changed.
    """
    top_dir = resolve_top_dir(cwd, args.top_dir)
    existing_manifests = _load_sorted_manifests(top_dir)
    proposals = _propose_manifests(top_dir, existing_manifests, args.exclude)
    if not proposals:
        print("Every HDL source is already listed in a manifest or sits next to one")
        return

    created: List[Manifest] = []
    should_create_all = args.yes
    for proposal, notes in proposals:
        manifest_path = _relative_manifest_path(proposal, top_dir)
        _print_report(
            manifest_path, _format_manifest(proposal, NEW_MANIFEST_INDENT).splitlines() + notes
        )
        answer = "y" if should_create_all else _ask_to_create(manifest_path)
        if answer == "q":
            break
        should_create_all = should_create_all or answer == "a"
        if answer != "n":
            _write_manifest(proposal, NEW_MANIFEST_INDENT)
            created.append(proposal)

    print(f"Created {len(created)} of {len(proposals)} proposed manifests")
    _print_modules_nothing_depends_on(created, existing_manifests + created)
