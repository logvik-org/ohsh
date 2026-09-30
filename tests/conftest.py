# SPDX-License-Identifier: Apache-2.0
"""Shared pytest fixtures for the ohsh test suite."""

import json
import logging

import pytest


@pytest.fixture(autouse=True)
def reset_ohsh_logger():
    """Reset handlers and propagation on the ``ohsh`` logger around each test.

    ``configure_logging`` is idempotent (it returns early once handlers exist),
    so tests must start from a clean slate to exercise it deterministically.
    """
    logger = logging.getLogger("ohsh")
    saved_handlers = logger.handlers[:]
    saved_propagate = logger.propagate
    logger.handlers.clear()
    logger.propagate = True
    yield
    logger.handlers.clear()
    logger.handlers.extend(saved_handlers)
    logger.propagate = saved_propagate


@pytest.fixture
def make_module(tmp_path):
    """Return a helper that writes a module manifest + its source files.

    Each module lives in its own directory under ``tmp_path`` and gets a
    ``manifest.json`` plus empty source files so existence checks pass.
    """

    def _make(module, sources, dependencies=None, *, name="manifest.json", create_sources=True):
        mod_dir = tmp_path / module
        mod_dir.mkdir(parents=True, exist_ok=True)
        manifest = {"module": module, "sources": sources}
        if dependencies is not None:
            manifest["dependencies"] = dependencies
        (mod_dir / name).write_text(json.dumps(manifest))
        if create_sources:
            for src in sources:
                (mod_dir / src).touch()
        return mod_dir

    return _make
