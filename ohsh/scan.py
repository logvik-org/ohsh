# SPDX-License-Identifier: Apache-2.0
"""Find the design units an HDL source declares and uses.

This matches text patterns and does not parse the language, so it misses what
only a compiler can see (generated names, encrypted sources) and the result is
a good first answer for a person to review.
"""

import pathlib
import re
from typing import NamedTuple, Optional, Set, Tuple

from .core import find_language

# A (library, unit) pair. The library is None when the source does not name one.
UnitReference = Tuple[Optional[str], str]


class ScannedSource(NamedTuple):
    """Unit names are lower case. A macro is named `` `name `` and a file ``"name"``."""

    declared_units: Set[str]
    references: Set[UnitReference]


_VHDL_COMMENT = re.compile(r"--[^\n]*|/\*.*?\*/", re.S)
_VHDL_DECLARATION = re.compile(
    r"^\s*(?:entity|package|context|configuration)\s+(\w+)\s+(?:is|of)\b", re.M
)
# A package body, architecture or configuration is compiled into the library of
# the unit it belongs to.
_VHDL_SECONDARY_UNIT = re.compile(
    r"\b(?:package\s+body|(?:architecture|configuration)\s+\w+\s+of)\s+(\w+)"
)
_VHDL_LIBRARY_CLAUSE = re.compile(r"\blibrary\s+([\w\s,]+);")
_VHDL_QUALIFIED_NAME = re.compile(r"\b(\w+)\.(\w+)")
_VHDL_COMPONENT_INSTANCE = re.compile(r":\s*(?:component\s+)?(\w+)\s+(?:generic|port)\s+map\b")

_VERILOG_COMMENT = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)
_VERILOG_DECLARATION = re.compile(
    r"^\s*(?:module|macromodule|package|interface|program)\s+(?:static\s+|automatic\s+)?(\w+)",
    re.M,
)
_VERILOG_INSTANCE = re.compile(r"^\s*(\w+)\s*#\s*\(|^\s*(\w+)\s+\w+\s*[(\[]", re.M)
_VERILOG_PACKAGE_USE = re.compile(r"(\w+)::")
_VERILOG_MACRO = re.compile(r"`(define\s+)?(\w+)")
_VERILOG_INCLUDE = re.compile(r'`include\s+"([^"]+)"')


def _file_unit(file_name: str) -> str:
    return f'"{pathlib.PurePosixPath(file_name).name}"'


def _scan_vhdl(text: str) -> ScannedSource:
    text = _VHDL_COMMENT.sub("", text)
    # A record field is written like a library unit (name.name), so only names
    # that follow a library the file declares count as references.
    libraries = {"work"}
    for clause in _VHDL_LIBRARY_CLAUSE.findall(text):
        libraries.update(name.strip() for name in clause.split(","))
    references: Set[UnitReference] = {
        (library, unit)
        for library, unit in _VHDL_QUALIFIED_NAME.findall(text)
        if library in libraries
    }
    references.update((None, unit) for unit in _VHDL_COMPONENT_INSTANCE.findall(text))
    references.update(("work", unit) for unit in _VHDL_SECONDARY_UNIT.findall(text))
    return ScannedSource(set(_VHDL_DECLARATION.findall(text)), references)


def _scan_verilog(text: str) -> ScannedSource:
    text = _VERILOG_COMMENT.sub("", text)
    declared_units = set(_VERILOG_DECLARATION.findall(text))
    used_units = {unit for instance in _VERILOG_INSTANCE.findall(text) for unit in instance if unit}
    used_units.update(_VERILOG_PACKAGE_USE.findall(text))
    used_units.update(_file_unit(file_name) for file_name in _VERILOG_INCLUDE.findall(text))
    for define, macro in _VERILOG_MACRO.findall(text):
        (declared_units if define else used_units).add(f"`{macro}")
    return ScannedSource(declared_units, {(None, unit) for unit in used_units})


_SCANNERS = {"vhdl": _scan_vhdl, "systemverilog": _scan_verilog}


def scan_source(source: pathlib.Path) -> ScannedSource:
    """Return what ``source`` declares and uses, or nothing for a file ohsh cannot read."""
    language = find_language(str(source))
    if language is None or not source.is_file():
        return ScannedSource(set(), set())
    # VHDL ignores case and Verilog does not. Lower case everywhere lets one
    # language find units of the other, at the cost of merging Verilog names
    # that differ only in case.
    text = source.read_text(encoding="utf-8", errors="replace").lower()
    scanned = _SCANNERS[language](text)
    scanned.declared_units.add(_file_unit(source.name.lower()))
    return scanned
