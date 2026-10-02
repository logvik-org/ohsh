# Why ohsh

## The problem

Every HDL tool needs to know which source files make up a design and in which
order to compile them. A module has to be compiled after the modules and
packages it uses, and a library after the libraries it uses. Each tool wants that
information in its own form: a Makefile variable for cocotb, a Python list for
VUnit, a Tcl script for Vivado or Quartus, list files for hog.

So projects often keep the same file list several times, by hand, once per tool.
When a module gets a new dependency, every list has to change, in the right
order. Reusing a module in another project means finding out which files it
pulls in.

## What ohsh does

ohsh moves that knowledge next to the code. Each module carries a small
`manifest.json` that says which files it consists of and which modules it uses.
Given a top module, ohsh follows those dependencies and answers one question:
*which files, in which order, for which libraries?*

The answer is plain text: one `.src` file per library and language, with one
absolute path per line, and `libraries.src` with the library order. Any tool,
script or Makefile can read that, so the same manifests serve your simulator,
your testbench framework and your synthesis flow.

Because a manifest lives with its module, a module can be copied or shared
between projects and still describe itself.

## What ohsh is not

ohsh is a companion to your build flow, not a replacement for it. It does not:

- run simulators or synthesis tools,
- create or manage tool projects,
- parse your HDL. It trusts the manifests and only checks that the listed files
  exist.

Tools such as [hog](https://hog.readthedocs.io), Vivado, Quartus, Questa,
cocotb and [VUnit](https://vunit.github.io) keep doing what they do. ohsh hands
them the file lists. Some of these tools can sort the files of a project
themselves, but they still need to be told which files belong to the design,
and ohsh gives them that from the same manifests.

## Design choices

- **Small and predictable.** One command, a handful of options, documented exit
  codes.
- **No runtime dependencies.** ohsh uses only the Python standard library, so it
  installs anywhere Python runs, including locked-down lab and CI machines.
- **Plain output.** Text files instead of a plugin per tool, so supporting a new
  tool needs a few lines of shell, not a change to ohsh.
- **Loud failures.** A missing module, a broken manifest, a duplicate name or a
  dependency loop stops ohsh with a clear message instead of producing a list
  that fails later in the tool.
