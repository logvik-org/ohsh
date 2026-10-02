# ohsh examples

Each integration has two examples:

- **simple**: the [simple project](projects), where every module is in one
  library. Shows the least you need to feed ohsh output to the tool.
- **advanced**: the [advanced project](projects), with three libraries, a VHDL
  package used across them, the top library named with `-w`, and a Verilog
  header. Shows how to compile libraries in the order of `libraries.src`.

The flow is always the same: run ohsh to get the per-library `.src` lists and
`libraries.src`, then hand them to the tool. The testbenches shared by the
examples are in [`testbenches/`](testbenches).

| Tool | Simple | Advanced | Verified |
|------|--------|----------|----------|
| [cocotb (Makefile)](integrations/cocotb_makefile) | [simple](integrations/cocotb_makefile/simple) | [advanced](integrations/cocotb_makefile/advanced) | ✅ CI |
| [cocotb (Python runner)](integrations/cocotb_runner) | [simple](integrations/cocotb_runner/simple) | [advanced](integrations/cocotb_runner/advanced) | ✅ CI |
| [VUnit](integrations/vunit) | [simple](integrations/vunit/simple) | [advanced](integrations/vunit/advanced) | ✅ CI |
| [GHDL](integrations/ghdl) | [simple](integrations/ghdl/simple) | [advanced](integrations/ghdl/advanced) | ✅ CI |
| [NVC](integrations/nvc) | [simple](integrations/nvc/simple) | [advanced](integrations/nvc/advanced) | ✅ CI |
| [UVVM](integrations/uvvm) | [simple](integrations/uvvm/simple) | [advanced](integrations/uvvm/advanced) | ✅ CI |
| [hog](integrations/hog) | [simple](integrations/hog/simple) | [advanced](integrations/hog/advanced) | ✅ CI (list files) |
| [Questa / ModelSim](integrations/questa) | [simple](integrations/questa/simple) | [advanced](integrations/questa/advanced) | ⚠️ doc |
| [Vivado](integrations/vivado) | [simple](integrations/vivado/simple) | [advanced](integrations/vivado/advanced) | ⚠️ doc |
| [Quartus](integrations/quartus) | [simple](integrations/quartus/simple) | [advanced](integrations/quartus/advanced) | ⚠️ doc |

**✅ CI** means both examples run on every pull request in
[`.github/workflows/integration.yml`](../.github/workflows/integration.yml),
with self-checking testbenches that fail if a source list is wrong. For hog, CI
checks the generated list files with hog's own reader. **⚠️ doc** examples are
checked against the vendor's documented commands, but can't run on a public CI
runner because the tools are licensed.

## Running the examples

The Python frameworks (cocotb, VUnit) come with the `examples` extra, pinned to
the versions CI uses:

```bash
source scripts/setup-dev.sh        # from the repo root: installs dev + examples
# or, in an environment you manage yourself:
pip install -e ".[examples]"
```

To run every example that CI runs, use `make examples` from the repo root, or
pick some with `scripts/run-examples.sh ghdl/simple vunit/advanced`.

The simulators are system tools: Icarus Verilog for the cocotb Verilog
examples, GHDL for the GHDL, VUnit and UVVM examples, and NVC for the NVC and
advanced cocotb examples. The hog examples need `tclsh` with tcllib. Each
example's README says which tools it needs.
