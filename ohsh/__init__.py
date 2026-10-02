# SPDX-License-Identifier: Apache-2.0
"""ohsh.

Finds the ``manifest.json`` files under a project directory, resolves the
dependencies of a top-level module, and writes each library's source files in
compile order, plus the order to compile the libraries in.

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

__version__ = "0.1.1"
