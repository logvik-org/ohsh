# hog

Status: **✅ both examples run in CI** (`.github/workflows/integration.yml`). They run each
project's `pre-creation.tcl` in plain `tclsh` and check the list files with hog's
own reader (`ReadListFile` in `hog.tcl`): every file must land in its library,
and one file must carry the `top` property. That hog itself calls the hook is not
checked, because creating a full hog project needs Vivado or Quartus, which CI
can't run.

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
calling ohsh from there regenerates them every time the project is created.
Both examples have one to copy, for instance
[`advanced/Top/demo/pre-creation.tcl`](advanced/Top/demo/pre-creation.tcl):

```tcl
set repo_path $globalSettings::repo_path
set list_dir [file join [file dirname [info script]] list]

puts [exec ohsh --format hog -t $repo_path/projects/advanced -o $list_dir \
    --relative-to $repo_path -w dsp_lib accumulator 2>@1]
```

It finds the list directory from its own location, so only the ohsh arguments
(`-t`, `-w` and the top module) need changing. ohsh must be installed wherever
hog runs, including the CI image.

If the committed lists were out of date, the regenerated ones leave the
repository modified, and hog reports that with a critical warning.

The hook only runs when the project is created, and the warning does not stop
the build. To make out-of-date lists fail CI before hog starts, regenerate them
in a job of their own and fail on any difference:

```bash
ohsh --format hog -t . -o Top/demo/list --relative-to . -w dsp_lib accumulator
if [ -n "$(git status --porcelain Top/demo/list)" ]; then
  git status --short Top/demo/list
  echo "hog list files are out of date: run ohsh and commit the result" >&2
  exit 1
fi
```

`git status` is used instead of `git diff` so that the list of a newly added
library, which git does not track yet, is caught too.

## Examples

Each example is laid out like a hog project, with its hook in `Top/demo/`.
`./run.sh` in the example's directory sources that hook the way hog would and
checks the lists it writes. hog is cloned once into `hog/build/Hog` (set
`HOG_ROOT` to use an existing checkout, or `HOG_VERSION` to pick another
release).

- [`simple/`](simple): one library, `-w demo_lib`.
- [`advanced/`](advanced): three libraries, one list file each. hog itself
  takes care of the compile order inside the Vivado or Quartus project.

The lists land in `Top/demo/list/`, which this repository ignores. In a real
project they are committed.

## Requirements

`tclsh` with tcllib (`apt-get install tcllib`) and git for the check. Docs:
<https://hog.readthedocs.io>.
