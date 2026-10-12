# hog

[hog (HDL on git)](https://hog.readthedocs.io) builds FPGA projects from a git
repository. It does not search for source files. You tell it which files belong
to a project in *list files* under `Top/<project>/list/`.

ohsh can write those list files for you from your manifests, so you no longer
edit them by hand. This page shows how, one step at a time.

## What you need

- A repository that already has a hog project, meaning a directory
  `Top/<project>/` with a `hog.conf` in it.
- An ohsh manifest (`manifest.json`) next to the HDL sources of each module.
  [Getting started](https://ohsh.readthedocs.io/en/latest/getting-started.html)
  explains how to write them, and `ohsh --create` can write them for you.
- ohsh 0.4.0 or newer. Check with `ohsh --version`.

The steps use this repository as the example. The hog project is called `demo`
and its top entity is `top_demo`:

```
my_repo/
├── Hog/                        hog itself, a git submodule
├── Top/
│   └── demo/
│       ├── hog.conf
│       └── list/               hog reads its list files from here
└── src/
    ├── blinky/
    │   ├── blinky.vhd
    │   └── manifest.json       module "blinky"
    └── top_demo/
        ├── top_demo.vhd
        └── manifest.json       module "top_demo", depends on "blinky"
```

## Step 1: Write the list files

Go to the root of the repository and run:

```bash
cd my_repo
ohsh --format hog -t . -o Top/demo/list --relative-to . -w demo top_demo
```

Every part of that command:

| Part | Meaning |
|------|---------|
| `ohsh` | The program. |
| `--format hog` | Write hog list files. Without it ohsh writes its plain lists, which hog cannot read. |
| `-t .` | Where to search for manifests. `.` is the current directory, so ohsh looks through the whole repository. Give a subdirectory such as `-t src` to search less. |
| `-o Top/demo/list` | Where to write the list files. hog reads them from `Top/<project>/list/`, and the project here is `demo`. ohsh creates the directory if it is missing. |
| `--relative-to .` | The root of the repository. hog reads every path in a list file relative to that root, so ohsh has to know where it is. `--format hog` refuses to run without this option. |
| `-w demo` | The name of the library that the top module is compiled into. A manifest calls this library `work`, and this option gives it its real name. Any name works. Naming it after the hog project is common. |
| `top_demo` | The top module, as named in its manifest (`"module": "top_demo"`). ohsh follows its dependencies and leaves out every module it does not need. |

ohsh prints nothing when all goes well. Add `-v` to see what it found and wrote.

## Step 2: Look at what was written

There is now one file per library in `Top/demo/list/`. This example has one
library, so there is one file, `Top/demo/list/demo.src`:

```
src/blinky/blinky.vhd
src/top_demo/top_demo.vhd top=top_demo
```

How to read it:

- **The file name is the library.** hog compiles every file listed in
  `demo.src` into the library `demo`. A project with three libraries gets three
  `.src` files.
- **Each line is one source file**, as a path from the root of the repository.
  VHDL and SystemVerilog files of the same library share one list.
- **`top=top_demo` marks the top entity.** hog needs to know which entity is
  the top of the design, and it reads that from this property. ohsh adds it to
  the file that declares an entity (or Verilog module) with the same name as
  the top module.

If ohsh warns that no source declares the top module, the entity is named
differently from the module in the manifest. No `top=` is written in that case,
and hog falls back to its default, an entity called `top_<project>`.

The command works, but you would have to run it again whenever a manifest
changes. Step 3 makes hog do that for you.

## Step 3: Let hog run ohsh

hog looks for a file called `Top/<project>/pre-creation.tcl`. If it exists, hog
runs it every time it creates the project, before it reads the list files. Put
the ohsh command there and the lists are refreshed without anyone thinking
about it.

Create `Top/demo/pre-creation.tcl` with this content:

```tcl
set repo_path $globalSettings::repo_path
set list_dir [file join [file dirname [info script]] list]

puts [exec env -u PYTHONHOME -u PYTHONPATH \
    ohsh --format hog -t $repo_path -o $list_dir \
    --relative-to $repo_path -w demo top_demo 2>@1]
```

Line by line:

| Line | Meaning |
|------|---------|
| `set repo_path $globalSettings::repo_path` | hog keeps the root of the repository in `globalSettings::repo_path`. This copies it to a shorter name. |
| `set list_dir [file join [file dirname [info script]] list]` | `[info script]` is the path of this file, and `file dirname` gives the directory it is in, `Top/demo`. Adding `list` gives `Top/demo/list`. The file finds its own project this way, so it can be copied to another project unchanged. |
| `exec env -u PYTHONHOME -u PYTHONPATH` | `exec` runs a program. `env -u NAME` runs it with the environment variable `NAME` removed. Vivado sets these two variables to the Python it ships with, and with them set no other Python can start. ohsh would stop with `No module named 'encodings'`. Removing them only affects ohsh, not Vivado. |
| `ohsh --format hog ...` | The command from step 1. `-t` and `--relative-to` get the repository root from hog, because hog does not always start in that directory. `-o` gets the list directory from the line above. |
| `-w demo top_demo` | The only part to change for your project: your library name and your top module. |
| `2>@1` | Sends the warnings of ohsh to the same place as its normal output. Tcl would otherwise treat any warning as a failure and stop the project creation. A real error still stops it, because ohsh then exits with an error code. |
| `puts [...]` | Prints what ohsh said in the hog log. |

Then commit the file:

```bash
git add Top/demo/pre-creation.tcl
git commit -m "Generate hog list files with ohsh"
```

What to expect afterwards:

- ohsh must be installed wherever hog runs. That includes the machine or
  container image your CI uses. If hog cannot find `ohsh`, the project creation
  stops with an error.
- `env` is a Linux and macOS program. On Windows, leave out
  `env -u PYTHONHOME -u PYTHONPATH`.
- The file only runs when the project is created. A project that is already
  open in Vivado or Quartus keeps its old file list until you create it again.

## Step 4: Keep the generated lists out of git

hog now writes the lists itself every time it creates the project, so they are
build output and do not belong in git. The manifests are what you commit.

Add this to the `.gitignore` in the root of the repository:

```
# Written by ohsh from the manifests, see Top/demo/pre-creation.tcl
Top/demo/list/*.src
```

If the lists are already in git, take them out. This keeps the files on disk
and only stops git from tracking them:

```bash
git rm --cached Top/demo/list/*.src
git commit -m "Stop tracking generated hog list files"
```

ohsh only knows about HDL sources. Everything else stays in list files that you
write by hand, and those do belong in git:

- Constraints, in `.con` files. The pattern above does not touch them.
- Simulation sources, in `.sim` files. Not touched either.
- IP cores (`.xci`) and other non-HDL sources, in a `.src` file of their own,
  for example `ips.src`. The pattern above would ignore that file too, so add
  an exception for it on the next line of the `.gitignore`:

  ```
  !Top/demo/list/ips.src
  ```

Three things to keep in mind:

- ohsh overwrites the `.src` files it writes, so do not add your own lines to
  them. Put those in a separate list file such as `ips.src`.
- ohsh does not delete the list file of a library that is no longer used.
  `git clean -fX Top/demo/list` removes every ignored file in the directory,
  which is exactly the generated lists. The next project creation writes the
  current ones.
- A fresh clone has no generated lists until the project is created. A hog
  command that reads the lists without creating the project needs the command
  from step 1 to run first.

## The examples in this directory

Status: **✅ both examples run in CI** (`.github/workflows/integration.yml`).

Each example is laid out like a hog project and has a working
`pre-creation.tcl` to copy:

- [`simple/`](simple): one library. See
  [`simple/Top/demo/pre-creation.tcl`](simple/Top/demo/pre-creation.tcl).
- [`advanced/`](advanced): three libraries, one list file each. See
  [`advanced/Top/demo/pre-creation.tcl`](advanced/Top/demo/pre-creation.tcl).
  hog leaves the compile order to Vivado or Quartus, so there is no
  `libraries.src`.

Run one with `./run.sh` in its directory. The script:

1. Clones hog into `hog/build/Hog`, once. Set `HOG_ROOT` to use an existing
   checkout, or `HOG_VERSION` to pick another release.
2. Runs the example's `pre-creation.tcl` the way hog would, in plain `tclsh`,
   with `PYTHONHOME` set the way Vivado sets it.
3. Reads the list files with hog's own reader (`ReadListFile` in `hog.tcl`) and
   checks that every file lands in its library and that one file carries the
   `top` property.

The lists land in `Top/demo/list/`, which this repository ignores as in step 4.
The `examples` directory plays the role of the repository root here, so the
paths in the lists start with `projects/`.

What the examples do not check is that hog itself calls `pre-creation.tcl`.
That needs a full project creation in Vivado or Quartus, which CI cannot run.

To run the examples you need `tclsh` with tcllib (`apt-get install tcllib`) and
git.
