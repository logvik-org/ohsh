# Integrations

ohsh's `.src` lists are just text - one absolute path per line - so they drop
into almost any flow. Runnable, self-checking examples live in
[`examples/`](https://github.com/logvik-org/ohsh/tree/main/examples). Each tool has a simple example (one library) and an
advanced one (three libraries compiled in the order of `libraries.src`). The
ones marked ✅ run in CI. The vendor-tool ones (⚠️) are checked against the
vendor's documentation but can't run on a public CI runner.

| Tool | Simple | Advanced | Verified |
|------|--------|----------|----------|
| [cocotb (Makefile)](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/cocotb_makefile) | [simple](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/cocotb_makefile/simple) | [advanced](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/cocotb_makefile/advanced) | ✅ CI |
| [cocotb (Python runner)](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/cocotb_runner) | [simple](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/cocotb_runner/simple) | [advanced](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/cocotb_runner/advanced) | ✅ CI |
| [VUnit](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/vunit) | [simple](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/vunit/simple) | [advanced](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/vunit/advanced) | ✅ CI |
| [GHDL](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/ghdl) | [simple](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/ghdl/simple) | [advanced](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/ghdl/advanced) | ✅ CI |
| [NVC](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/nvc) | [simple](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/nvc/simple) | [advanced](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/nvc/advanced) | ✅ CI |
| [UVVM](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/uvvm) | [simple](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/uvvm/simple) | [advanced](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/uvvm/advanced) | ✅ CI |
| [hog](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/hog) | [simple](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/hog/simple) | [advanced](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/hog/advanced) | ✅ CI (list files) |
| [Questa / ModelSim](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/questa) | [simple](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/questa/simple) | [advanced](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/questa/advanced) | ⚠️ doc |
| [Vivado](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/vivado) | [simple](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/vivado/simple) | [advanced](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/vivado/advanced) | ⚠️ doc |
| [Quartus](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/quartus) | [simple](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/quartus/simple) | [advanced](https://github.com/logvik-org/ohsh/tree/main/examples/integrations/quartus/advanced) | ⚠️ doc |

For example, feeding ohsh output to GHDL:

```bash
ohsh -t my_project -o build top
while IFS= read -r lib; do
  [ -f "build/${lib}_vhdl.src" ] || continue
  while IFS= read -r f; do ghdl -a --work="$lib" --std=08 "$f"; done < "build/${lib}_vhdl.src"
done < build/libraries.src
ghdl -e --std=08 top && ghdl -r --std=08 top
```
