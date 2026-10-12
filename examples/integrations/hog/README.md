# hog

Status: **✅ both examples run in CI** (`.github/workflows/integration.yml`). They check the list files with hog's own reader
(`ReadListFile` in `hog.tcl`), which runs in plain `tclsh`: every file must land
in its library, and one file must carry the `top` property. Creating a full hog
project needs Vivado or Quartus, which CI can't run.

[hog (HDL on git)](https://hog.readthedocs.io) drives the FPGA build flow and
reads its sources from list files in `Top/<project>/list/`. `--format hog`
writes those files directly:

```bash
ohsh --format hog -t . -o Top/demo/list --relative-to . -w dsp_lib accumulator
```

This writes one `<library>.src` per library, which differs from the plain
format in three ways that hog requires:

- hog takes the library from the list file's name, so `math_lib.src` holds
  every source of `math_lib`, VHDL and SystemVerilog together.
- hog reads each entry relative to the repository root, so `--relative-to` is
  required and takes that root.
- hog takes the top module from a `top=<entity>` property, and assumes
  `top_<project>` when no entry has one. ohsh puts the property on the file
  that declares the top module:

```
projects/advanced/acc_register/acc_register.vhd
projects/advanced/accumulator/accumulator.vhd top=accumulator
```

ohsh only knows HDL sources. IP cores, constraints and simulation lists stay in
hand-written list files next to the generated ones. ohsh overwrites the
`<library>.src` files it writes, so keep hand-written entries out of them. It
does not remove the list of a library that is no longer used.

## Keeping the lists up to date

hog sources `Top/<project>/pre-creation.tcl` before it reads the list files, so
calling ohsh from there regenerates them every time the project is created:

```tcl
set repo_path $globalSettings::repo_path
exec ohsh --format hog -t $repo_path -o $repo_path/Top/demo/list \
  --relative-to $repo_path -w dsp_lib accumulator
```

If the committed lists were out of date, the regenerated ones leave the
repository modified, and hog reports that with a critical warning. This hook
is not part of the CI check below.

## Examples

Run the examples with `./run.sh` in the example's directory. hog is cloned once
into `hog/build/Hog` (set `HOG_ROOT` to use an existing checkout, or
`HOG_VERSION` to pick another release).

- [`simple/run.sh`](simple/run.sh): one library, `-w demo_lib`.
- [`advanced/run.sh`](advanced/run.sh): three libraries, one list file each.
  hog itself takes care of the compile order inside the Vivado or Quartus
  project.

## Requirements

`tclsh` with tcllib (`apt-get install tcllib`) and git for the check. Docs:
<https://hog.readthedocs.io>.
