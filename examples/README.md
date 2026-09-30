# ohsh examples

These examples show ohsh feeding real HDL tools. They all operate on the shared
[`demo_project/`](demo_project) - a tiny multi-library design (a `math_lib`
adder, a `work` accumulator that uses it, and a Verilog counter) described by
`manifest.json` files.

The flow is always the same: run `ohsh` to produce per-library `.src` lists,
then hand those lists to the tool.

| Example | Tool | Status |
|---------|------|--------|
| [cocotb_makefile](integrations/cocotb_makefile/) | cocotb (Makefile) | ✅ run in CI |
| [cocotb_runner](integrations/cocotb_runner/) | cocotb (Python runner) | ✅ run in CI |
| [vunit](integrations/vunit/) | VUnit | ✅ run in CI |
| [ghdl](integrations/ghdl/) | GHDL | ✅ run in CI |
| [nvc](integrations/nvc/) | NVC | ✅ run in CI |
| [uvvm](integrations/uvvm/) | UVVM (GHDL) | ✅ run in CI |
| [hog](integrations/hog/) | hog | documented |
| [questa](integrations/questa/) | Questa / ModelSim | ⚠️ doc (licensed) |
| [vivado](integrations/vivado/) | AMD Vivado | ⚠️ doc (licensed) |
| [quartus](integrations/quartus/) | Intel Quartus | ⚠️ doc (licensed) |

**✅ run in CI** means the example is executed end-to-end on every push by
[`.github/workflows/integration.yml`](../.github/workflows/integration.yml),
with a self-checking testbench that fails the build if the source list is wrong.
**⚠️ doc** examples are validated against the vendor's documented commands but
can't run on a public CI runner because the tools are proprietary/licensed.
