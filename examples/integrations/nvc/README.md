# NVC integration

Status: **✅ verified in CI** (`.github/workflows/integration.yml`).

[`run.sh`](run.sh) mirrors the GHDL example but uses [NVC](https://www.nickg.me.uk/nvc/):

1. `ohsh` generates `math_lib_vhdl.src` / `work_vhdl.src` from the
   [demo project](../../demo_project).
2. Each library is analyzed with `nvc --work=<lib> -a` (dependencies first);
   `-L.` adds the build dir to the library search path so `work` finds
   `math_lib`.
3. The shared self-checking testbench
   ([`../ghdl/tb_accumulator.vhd`](../ghdl/tb_accumulator.vhd)) is analyzed,
   elaborated (`-e`), and run (`-r`).

```bash
./run.sh
```

NVC is not in the default Ubuntu repositories; CI installs it with the
[`nickg/setup-nvc`](https://github.com/marketplace/actions/setup-nvc) action.
Docs: <https://www.nickg.me.uk/nvc/manual.html>.
