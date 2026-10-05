# Create, fix and check manifests

Writing manifests by hand gets tedious in a large project. ohsh can read the
HDL sources and write or update the manifests from what it finds.
[Getting started](getting-started.md) shows the three options below on a small
project. This page is the reference for them.

```{note}
The result is best effort. ohsh searches the sources for text patterns and does
not compile them, so some projects need manual changes afterwards. The aim is
less manual work, not none. See [Limitations](#limitations).
```

| Option     | What it does                                                           |
|------------|------------------------------------------------------------------------|
| `--create` | Writes a manifest for every source directory that has none.            |
| `--fix`    | Adds missing dependencies to the manifests and sorts their sources.    |
| `--check`  | Reports what `--fix` would change, without changing anything.          |

## `--create`

`--create` writes a `manifest.json` for each directory that contains HDL files
and has no manifest yet.

```bash
ohsh --create -t project
```

ohsh prints the content of every manifest and asks before writing it:

```
accumulator/manifest.json
  {
    "module": "accumulator",
    "sources": [
      "accumulator.vhd"
    ],
    "dependencies": {
      "work": [
        "adder"
      ]
    }
  }
Create accumulator/manifest.json? [y]es, [n]o, [a]ll, [q]uit:
```

`y` writes the file, `n` skips it, `a` writes it and all the following ones, and
`q` stops. With `--yes`, ohsh writes everything without asking. When it is done,
it prints the new modules that no other module depends on. These are normally
the top-levels and testbenches.

ohsh divides the sources into modules by these rules:

- A directory with HDL files is one module, named after the directory. If that
  name is taken, ohsh puts the name of the parent directory in front, so
  `adder/tb` becomes `adder_tb`.
- Files in a subdirectory called `hdl`, `rtl` or `src` belong to the module of
  the parent directory.
- Directories that have a manifest are skipped, and so are files that a
  manifest already lists. `--create` does not modify existing manifests, so you
  can run it again after adding a directory.
- Hidden directories are skipped. `--exclude` skips others. It takes a
  directory name or a path relative to `--top-dir`, with `*` as a wildcard, and
  can be given several times:

  ```bash
  ohsh --create --exclude ip --exclude 'submodules/UVVM'
  ```

One module per directory will not suit every project. Rename, merge or split
the modules afterwards where needed.

## `--fix`

`--fix` compares each manifest with its sources and updates it in two ways:

- It adds a dependency on every module whose design units the sources use.
- It reorders `sources` so that a file comes after the files of the same module
  that it uses, for example after a package.

```bash
ohsh --fix
```

ohsh prints the manifests it changed. It does not rewrite the others, and keys
it does not know stay in the file.

`--fix` does not remove dependencies. ohsh cannot read every source (see
[Limitations](#limitations)), so it cannot tell whether a dependency is unused.

## `--check`

`--check` makes the same comparison as `--fix` and writes nothing:

```
accumulator/manifest.json
  missing dependency: adder (library math_lib)
  sources out of order, expected: acc_pkg.vhd, accumulator.vhd
  note: no source ohsh can read uses the dependency old_fifo (library work)
1 of 4 manifests need fixing, run ohsh --fix
```

The exit code is 104 if a manifest lacks a dependency or lists its sources in
the wrong order, and 0 otherwise. This is meant for CI or a pre-commit hook.

Lines starting with `note:` are things ohsh is unsure about, such as a
dependency it found no use of. They do not affect the exit code.

## Limit `--fix` and `--check` to one module

By default both go through all manifests under `--top-dir`. With a module name
they only handle that module and the modules it depends on, directly or
indirectly:

```bash
ohsh --fix accumulator
ohsh --check accumulator
```

`--no-deps` restricts them further, to the manifest of the named module:

```bash
ohsh --fix --no-deps accumulator
```

`--create` does not accept a module name.

## How ohsh reads the sources

ohsh removes the comments from each file and then searches it with regular
expressions for the design units it declares and the ones it uses.

| Language               | Declares                                                    | Uses                                                                            |
|------------------------|-------------------------------------------------------------|---------------------------------------------------------------------------------|
| VHDL                   | `entity`, `package`, `context`, `configuration`             | `library.unit` names, component instances, and the unit a body belongs to       |
| Verilog, SystemVerilog | `module`, `package`, `interface`, `program`, `` `define ``  | module instances, `pkg::` names, `` `include `` files and macros                |

In VHDL, ohsh recognises three ways of using a unit:

- A name with the library in front, as in these two lines:

  ```vhdl
  use work.acc_pkg.all;
  u_adder : entity math_lib.adder port map (a => a, b => b);
  ```

  Here the file uses the package `acc_pkg` from `work` and the entity `adder`
  from `math_lib`. Packages need nothing special: the `use` clause is enough
  for ohsh to put the package file first, or to add a dependency when another
  module declares the package.

  For a library other than `work`, the file must also contain
  `library math_lib;`. Without that line ohsh ignores the name, because a
  record field such as `my_record.adder` looks exactly the same.

- A component instance, where the unit is named without a library:

  ```vhdl
  u_adder : adder port map (a => a, b => b);
  ```

- A package body, architecture or configuration, which uses the unit it
  belongs to:

  ```vhdl
  package body acc_pkg is
  architecture rtl of accumulator is
  ```

  So a package body in its own file comes after the package, and an
  architecture in its own file after its entity.

If a file uses a unit that another module declares, that module becomes a
dependency. The library is taken from the source where it is written, as in
`math_lib.adder`. Verilog has no libraries, and a VHDL component instance does
not name one. In those cases ohsh accepts the library under which the manifest
already lists the module, and uses `work` for a new dependency.

Names are compared without regard to case in both languages, so a VHDL file can
refer to a Verilog module and the other way round.

## Limitations

ohsh does not parse or compile the code, so some things are out of its reach.

It does not detect:

- Units in encrypted or generated files. ohsh sees neither what such a file
  declares nor what it uses.
- Names that only exist after preprocessing or elaboration, such as a macro
  that expands to a module name, or a unit selected by a VHDL configuration.
- A Verilog instance whose module name is not the first thing on its line.
- SystemVerilog interface ports, such as `my_if.master bus`.

It can get these wrong:

- A Verilog line of the form `name other (` is taken as an instance of `name`
  if some module declares a unit called `name`.
- Verilog names that differ only in case, such as `Fifo` and `fifo`, are
  treated as the same unit.
- A VHDL component instance may end up under the wrong library, as described
  above.

In two cases ohsh notices the problem and leaves the decision to you:

- Two modules declare a unit with the same name, for example two versions of a
  library or two variants of a module. `--check` prints a note with the
  candidates. Add the right one to the manifest and the note disappears.
- Files of one module use each other in a loop. ohsh logs a warning and does
  not touch the order of `sources`.

## When the result is wrong

If ohsh missed a dependency, the compiler reports a unit it cannot find. Add
the dependency to the manifest by hand. `--fix` will not remove it.

If ohsh added a dependency that is not needed, that is a bug in ohsh. Please
[report it](#report-problems) so the cause can be removed. Until then, keep the
dependency in the manifest: the build compiles one module too many and still
works, while `--check` asks for the dependency again when it is removed.

A manifest without sources, which only collects other modules, gets a note
from `--check` for each of its dependencies. That is expected and needs no
action.

## Report problems

If `--create`, `--fix` or `--check` gives a wrong result that is not listed
under [Limitations](#limitations), please
[open an issue](https://github.com/logvik-org/ohsh/issues). Include the source
lines involved and the manifest ohsh wrote or complained about. Cases like
these are how the pattern matching gets better.
