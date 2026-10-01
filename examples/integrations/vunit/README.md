# VUnit integration

Status: **✅ verified in CI** (`.github/workflows/integration.yml`, GHDL backend).

[`run.py`](run.py) generates the source lists with `ohsh` and adds them to VUnit
libraries:

```python
subprocess.run(["ohsh", "-t", DEMO, "-o", BUILD, "-w", "dut_lib", "accumulator"], check=True)

vu = VUnit.from_argv()
for library in read_src(BUILD / "libraries.src"):
    sources = read_src(BUILD / f"{library}_vhdl.src")
    vu.add_library(library).add_source_files(sources, allow_empty=True)
vu.add_library("tb_lib").add_source_files(HERE / "tb_accumulator_vunit.vhd")
vu.main()
```

Run it:

```bash
VUNIT_SIMULATOR=ghdl python run.py
```

Notes:
- `add_source_files()` accepts a list of paths, so an ohsh `.src` list drops
  right in. VUnit re-derives compile order from the files itself.
- ohsh is invoked with `-w dut_lib` because VUnit reserves the name `work`.
- [`tb_accumulator_vunit.vhd`](tb_accumulator_vunit.vhd) is a standard VUnit
  testbench (`runner_cfg` generic, `check_equal`).

Requires VUnit (`pip install -e ".[examples]"`) and a simulator (GHDL in CI). Docs:
<https://vunit.github.io/py/ui.html>.
