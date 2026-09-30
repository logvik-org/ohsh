# SPDX-License-Identifier: Apache-2.0
"""Unit tests for ohsh.utils."""

import logging
import pathlib

import pytest

from ohsh.utils import (
    CONSOLE_HANDLER_NAME,
    CircularDependencyError,
    MissingManifestError,
    configure_logging,
    discover_manifests,
    extract_dependencies,
    order_libraries,
    to_absolute_path,
    validate_top_dir,
)


def _manifest(module, sources=None, dependencies=None):
    m = {"module": module, "sources": sources or []}
    if dependencies is not None:
        m["dependencies"] = dependencies
    return m


def test_extract_dependencies_order_and_dedup():
    data = [
        _manifest("top", dependencies={"work": ["a", "b"]}),
        _manifest("a", dependencies={"work": ["c"]}),
        _manifest("b", dependencies={"work": ["c"]}),
        _manifest("c"),
    ]
    top = data[0]
    deps = extract_dependencies(data, top, "work")
    # c must come before a and b (compile order), and appear only once.
    assert deps == [("work", "c"), ("work", "a"), ("work", "b")]


def test_extract_dependencies_work_remap_for_nested():
    # A nested dependency declared under "work" should be remapped to the
    # current library name it was reached through (regression for commit d85ca2b).
    data = [
        _manifest("top", dependencies={"mylib": ["a"]}),
        _manifest("a", dependencies={"work": ["b"]}),
        _manifest("b"),
    ]
    deps = extract_dependencies(data, data[0], "work")
    assert deps == [("mylib", "b"), ("mylib", "a")]


class _CountingManifest(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dependency_reads = 0

    def get(self, key, default=None):
        if key == "dependencies":
            self.dependency_reads += 1
        return super().get(key, default)


def test_extract_dependencies_walks_shared_module_once():
    shared = _CountingManifest(_manifest("c"))
    data = [
        _manifest("top", dependencies={"work": ["a", "b"]}),
        _manifest("a", dependencies={"work": ["c"]}),
        _manifest("b", dependencies={"work": ["c"]}),
        shared,
    ]
    extract_dependencies(data, data[0], "work")
    assert shared.dependency_reads == 1


def test_extract_dependencies_same_module_in_two_libraries():
    data = [
        _manifest("top", dependencies={"work": ["a"], "lib2": ["a"]}),
        _manifest("a", dependencies={"work": ["b"]}),
        _manifest("b"),
    ]
    deps = extract_dependencies(data, data[0], "work")
    assert deps == [("work", "b"), ("work", "a"), ("lib2", "b"), ("lib2", "a")]


def test_extract_dependencies_circular_raises_with_cycle_path():
    data = [
        _manifest("top", dependencies={"work": ["a"]}),
        _manifest("a", dependencies={"work": ["b"]}),
        _manifest("b", dependencies={"work": ["a"]}),
    ]
    with pytest.raises(CircularDependencyError) as excinfo:
        extract_dependencies(data, data[0], "work")
    assert excinfo.value.cycle == ["a", "b", "a"]


def test_extract_dependencies_self_dependency_raises():
    data = [_manifest("a", dependencies={"work": ["a"]})]
    with pytest.raises(CircularDependencyError):
        extract_dependencies(data, data[0], "work")


def test_extract_dependencies_missing_manifest_names_requiring_module():
    data = [
        _manifest("top", dependencies={"work": ["a"]}),
        _manifest("a", dependencies={"work": ["ghost"]}),
    ]
    with pytest.raises(MissingManifestError) as excinfo:
        extract_dependencies(data, data[0], "work")
    assert excinfo.value.module == "ghost"
    assert excinfo.value.required_by == "a"


def _library_order(data, work="work"):
    deps = extract_dependencies(data, data[0], work) + [(work, data[0]["module"])]
    return order_libraries(data, deps)


def test_order_libraries_puts_used_library_first():
    # libA is reached first (through "a"), but "c" in libA uses libB, so libB
    # must be compiled before libA.
    data = [
        _manifest("top", dependencies={"libA": ["a", "c"]}),
        _manifest("a"),
        _manifest("c", dependencies={"libB": ["b"]}),
        _manifest("b"),
    ]
    assert _library_order(data) == ["libB", "libA", "work"]


def test_order_libraries_maps_work_to_own_library():
    data = [
        _manifest("top", dependencies={"mylib": ["a"]}),
        _manifest("a", dependencies={"work": ["b"]}),
        _manifest("b"),
    ]
    assert _library_order(data) == ["mylib", "work"]


def test_order_libraries_warns_on_library_loop(caplog):
    data = [
        _manifest("top", dependencies={"libA": ["a"], "libB": ["c"]}),
        _manifest("a", dependencies={"libB": ["b"]}),
        _manifest("b"),
        _manifest("c", dependencies={"libA": ["d"]}),
        _manifest("d"),
    ]
    order = _library_order(data)
    assert sorted(order) == ["libA", "libB", "work"]
    assert order[-1] == "work"
    assert "libB -> libA -> libB" in caplog.text


def test_validate_top_dir(tmp_path):
    assert validate_top_dir(tmp_path) is True
    assert validate_top_dir(tmp_path / "nope") is False


def test_to_absolute_path_resolves_relative(tmp_path):
    # Regression: this used to build the absolute path and then discard it.
    result = to_absolute_path(tmp_path, "sub/dir")
    assert isinstance(result, pathlib.Path)
    assert result.is_absolute()
    assert result == (tmp_path / "sub/dir").resolve()


def test_to_absolute_path_keeps_absolute(tmp_path):
    result = to_absolute_path(tmp_path, str(tmp_path))
    assert pathlib.Path(result).is_absolute()


def test_discover_manifests_globs_recursively(make_module):
    make_module("a", ["a.v"])
    make_module("b", ["b.vhd"], name="manifest_extra.json")
    top = pathlib.Path(str(make_module("c", ["c.v"]))).parent
    found = {p.name for p in discover_manifests(top)}
    assert "manifest.json" in found
    assert "manifest_extra.json" in found


def test_configure_logging_no_logfile_by_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    configure_logging()
    # No stray debug.log written into the cwd.
    assert not (tmp_path / "debug.log").exists()
    logger = logging.getLogger("ohsh")
    assert logger.handlers, "console handler should be attached"


def test_configure_logging_writes_logfile_when_requested(tmp_path):
    log_path = tmp_path / "run.log"
    logger = configure_logging(verbosity=2, log_file=str(log_path))
    logger.info("hello from ohsh")
    for handler in logger.handlers:
        handler.flush()
    assert log_path.exists()
    assert "hello from ohsh" in log_path.read_text()


def test_configure_logging_does_not_propagate_to_root():
    logger = configure_logging()
    assert logger.propagate is False


def test_configure_logging_ignores_foreign_handlers(tmp_path):
    logging.getLogger("ohsh").addHandler(logging.NullHandler())
    log_path = tmp_path / "run.log"
    configure_logging(log_file=str(log_path))
    assert log_path.exists()


def test_configure_logging_is_idempotent():
    configure_logging()
    configure_logging()
    handler_names = [h.get_name() for h in logging.getLogger("ohsh").handlers]
    assert handler_names.count(CONSOLE_HANDLER_NAME) == 1


@pytest.mark.parametrize(
    ("verbosity", "level"),
    [(0, logging.WARNING), (1, logging.INFO), (2, logging.DEBUG), (3, logging.DEBUG)],
)
def test_configure_logging_console_level_follows_verbosity(verbosity, level):
    logger = configure_logging(verbosity=verbosity)
    console = next(h for h in logger.handlers if h.get_name() == CONSOLE_HANDLER_NAME)
    assert console.level == level
