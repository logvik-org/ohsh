# hog integration

Status: **documented** - shows how ohsh complements
[hog (HDL on git)](https://hog.readthedocs.io).

ohsh and hog solve different problems and pair nicely:

- **ohsh** answers *"given my module manifests, what source files (per library)
  are needed for this top, and in what order?"*
- **hog** drives the full FPGA build/CI flow (Vivado/Quartus projects,
  versioning, bitstream generation) and reads its file lists from `*.src` files
  under a project's `list/` directory.

hog's list files contain one source path per line (optionally with a
`lib_name.src` filename to assign a VHDL library) - the same shape ohsh emits.
So ohsh output can seed or regenerate hog list files.

## Example

Generate per-library lists with ohsh:

```bash
ohsh -t ../../demo_project -o build accumulator
# -> build/math_lib_vhdl.src, build/work_vhdl.src
```

A hog project keeps its lists in `Top/<project>/list/`. hog uses the list
*filename* to choose the library, e.g. `math_lib.src`. Map ohsh output to hog
list files (paths can be made relative to the hog repo root as hog expects):

```bash
mkdir -p Top/demo/list
cp build/math_lib_vhdl.src Top/demo/list/math_lib.src
cp build/work_vhdl.src     Top/demo/list/work.src
```

hog then reads `Top/demo/list/*.src` when creating the project. This keeps the
authoritative dependency information in your `manifest.json` files (resolved by
ohsh) while letting hog own the project/build/CI machinery.

> Note: hog list-file conventions evolve across hog versions - check the
> [hog documentation](https://hog.readthedocs.io) for the exact `list/` format
> your version expects. This example illustrates the data flow, not a pinned API.
