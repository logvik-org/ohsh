#!/usr/bin/env bash
# UVVM (on GHDL), simple project: the design is in the default `work` library and
# the testbench uses uvvm_util.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EXAMPLES="$(cd "$HERE/../../.." && pwd)"
BUILD="$HERE/build"
rm -rf "$BUILD"
mkdir -p "$BUILD"
# UVVM is cloned once into the shared uvvm/build directory and reused by both
# examples. Set UVVM_ROOT to use an existing checkout instead.
UVVM_ROOT="${UVVM_ROOT:-$HERE/../build/UVVM}"
UVVM_VERSION="${UVVM_VERSION:-2026.03.20}"
# UVVM needs GHDL's Synopsys and relaxed extensions. The design and testbench
# use the same flags so all libraries are compatible.
GHDL_FLAGS=(--std=08 --workdir="$BUILD" -P"$BUILD" -fsynopsys -frelaxed)

if [ ! -d "$UVVM_ROOT/uvvm_util" ]; then
  git clone --depth 1 --branch "$UVVM_VERSION" https://github.com/UVVM/UVVM.git "$UVVM_ROOT"
fi

# uvvm_util is compiled in the order of UVVM's own compile_order.txt, whose
# paths are relative to its script directory.
while IFS= read -r line; do
  case "$line" in '' | \#*) continue ;; esac
  (cd "$UVVM_ROOT/uvvm_util/script" && ghdl -a "${GHDL_FLAGS[@]}" --work=uvvm_util "$line")
done < "$UVVM_ROOT/uvvm_util/script/compile_order.txt"

ohsh -t "$EXAMPLES/projects/simple" -o "$BUILD" accumulator

while IFS= read -r f; do
  ghdl -a "${GHDL_FLAGS[@]}" "$f"
done < "$BUILD/work_vhdl.src"

ghdl -a "${GHDL_FLAGS[@]}" "$EXAMPLES/testbenches/tb_accumulator_uvvm.vhd"
ghdl -e "${GHDL_FLAGS[@]}" tb_accumulator_uvvm
(cd "$BUILD" && ghdl -r "${GHDL_FLAGS[@]}" tb_accumulator_uvvm)
echo "UVVM simple example: PASS"
