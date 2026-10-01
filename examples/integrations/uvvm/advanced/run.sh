#!/usr/bin/env bash
# UVVM (on GHDL), advanced project: the design's three libraries are compiled in
# the order ohsh writes to libraries.src, next to UVVM's uvvm_util.
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

TOP_LIBRARY=dsp_lib
ohsh -t "$EXAMPLES/projects/advanced" -w "$TOP_LIBRARY" -o "$BUILD" accumulator

while IFS= read -r lib; do
  while IFS= read -r f; do
    ghdl -a "${GHDL_FLAGS[@]}" --work="$lib" "$f"
  done < "$BUILD/${lib}_vhdl.src"
done < "$BUILD/libraries.src"

# The testbench goes into the top library, where `work.accumulator` resolves.
ghdl -a "${GHDL_FLAGS[@]}" --work="$TOP_LIBRARY" "$EXAMPLES/testbenches/tb_accumulator_uvvm.vhd"
ghdl -e "${GHDL_FLAGS[@]}" --work="$TOP_LIBRARY" tb_accumulator_uvvm
(cd "$BUILD" && ghdl -r "${GHDL_FLAGS[@]}" --work="$TOP_LIBRARY" tb_accumulator_uvvm)
echo "UVVM advanced example: PASS"
