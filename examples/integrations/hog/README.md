# hog

Status: **✅ both examples run in CI** (`.github/workflows/integration.yml`). They check the list files with hog's own reader
(`ReadListFile` in `hog.tcl`), which runs in plain `tclsh`. Creating a full hog
project needs Vivado or Quartus, which CI can't run.

[hog (HDL on git)](https://hog.readthedocs.io) drives the FPGA build flow and
reads its sources from list files in `Top/<project>/list/`. hog takes the
library from the list file's name (`math_lib.src` holds the files of
`math_lib`) and reads each entry **relative to the repository root**. ohsh
writes absolute paths, so they have to be converted:

```bash
while IFS= read -r f; do
  realpath --relative-to="$REPO_ROOT" "$f"
done < build/math_lib_vhdl.src > Top/demo/list/math_lib.src
```

Run the examples with `./run.sh` in the example's directory. hog is cloned once
into `hog/build/Hog` (set `HOG_ROOT` to use an existing checkout, or
`HOG_VERSION` to pick another release).

## Simple: [`simple/run.sh`](simple/run.sh)

ohsh runs with `-w demo_lib`, and `demo_lib_vhdl.src` becomes
`list/demo_lib.src`.

## Advanced: [`advanced/run.sh`](advanced/run.sh)

One hog list file per line of `libraries.src`. hog itself takes care of the
compile order inside the Vivado or Quartus project.

## Requirements

`tclsh` with tcllib (`apt-get install tcllib`) and git for the check. Docs:
<https://hog.readthedocs.io>.
