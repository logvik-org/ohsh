# Integrations

ohsh's `.src` lists are just text - one absolute path per line - so they drop
into almost any flow. Runnable, self-checking examples live in
[`examples/`](https://github.com/logvik-org/oshsh/tree/main/examples). The ones marked ✅ are **executed in CI** against a
demo project. The vendor-tool ones (⚠️) are validated against official docs but
can't run on a public CI runner.

| Tool | Example | Verified |
|------|---------|----------|
| [cocotb (Makefile)](https://github.com/logvik-org/oshsh/tree/main/examples/integrations/cocotb_makefile) | `Makefile` | ✅ CI |
| [cocotb (Python runner)](https://github.com/logvik-org/oshsh/tree/main/examples/integrations/cocotb_runner) | `runner.py` | ✅ CI |
| [VUnit](https://github.com/logvik-org/oshsh/tree/main/examples/integrations/vunit) | `run.py` | ✅ CI |
| [GHDL](https://github.com/logvik-org/oshsh/tree/main/examples/integrations/ghdl) | `run.sh` | ✅ CI |
| [NVC](https://github.com/logvik-org/oshsh/tree/main/examples/integrations/nvc) | `run.sh` | ✅ CI |
| [UVVM](https://github.com/logvik-org/oshsh/tree/main/examples/integrations/uvvm) | `run.sh` | ✅ CI |
| [hog](https://github.com/logvik-org/oshsh/tree/main/examples/integrations/hog) | `README.md` | doc |
| [Questa / ModelSim](https://github.com/logvik-org/oshsh/tree/main/examples/integrations/questa) | `compile.do` | ⚠️ doc |
| [Vivado](https://github.com/logvik-org/oshsh/tree/main/examples/integrations/vivado) | `read_sources.tcl` | ⚠️ doc |
| [Quartus](https://github.com/logvik-org/oshsh/tree/main/examples/integrations/quartus) | `add_sources.tcl` | ⚠️ doc |

For example, feeding ohsh output to GHDL:

```bash
ohsh -t my_project -o build top
while IFS= read -r lib; do
  [ -f "build/${lib}_vhdl.src" ] || continue
  while IFS= read -r f; do ghdl -a --work="$lib" --std=08 "$f"; done < "build/${lib}_vhdl.src"
done < build/libraries.src
ghdl -e --std=08 top && ghdl -r --std=08 top
```
