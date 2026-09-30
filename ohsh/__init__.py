# SPDX-License-Identifier: Apache-2.0
"""ohsh - Ola's HDL Source Handler.

A small, humble companion tool for HDL projects. It scans a project directory
for module manifests (``manifest.json``), recursively resolves dependencies
between modules, and emits per-library lists of source files in correct
compilation order. Feed those lists into your simulator or build flow (cocotb,
VUnit, ghdl, nvc, Questa, Vivado, Quartus, hog, ...).

Example manifest file (``manifest.json``)::

    {
        "module": "module_name",
        "sources": [
            "source1.v",
            "source2.v",
            "source3.v"
        ],
        "dependencies": {
            "work": ["module1", "module2"],
            "lib_name": ["module3"]
        }
    }
"""

__version__ = "0.1.0"
