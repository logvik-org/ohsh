#!/usr/bin/env bash
# GHDL, advanced project: three libraries, compiled in the order ohsh writes to
# libraries.src. The top library is named with -w.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EXAMPLES="$(cd "$HERE/../../.." && pwd)"
BUILD="$HERE/build"
rm -rf "$BUILD"
mkdir -p "$BUILD"
TOP_LIBRARY=dsp_lib
# -P lets each library find the ones analyzed before it in $BUILD.
GHDL_FLAGS=(--std=08 --workdir="$BUILD" -P"$BUILD")

ohsh -t "$EXAMPLES/projects/advanced" -w "$TOP_LIBRARY" -o "$BUILD" accumulator

while IFS= read -r lib; do
  while IFS= read -r f; do
    ghdl -a "${GHDL_FLAGS[@]}" --work="$lib" "$f"
  done < "$BUILD/${lib}_vhdl.src"
done < "$BUILD/libraries.src"

# The testbench goes into the top library, where `work.accumulator` resolves.
ghdl -a "${GHDL_FLAGS[@]}" --work="$TOP_LIBRARY" "$EXAMPLES/testbenches/tb_accumulator.vhd"
ghdl -e "${GHDL_FLAGS[@]}" --work="$TOP_LIBRARY" tb_accumulator
ghdl -r "${GHDL_FLAGS[@]}" --work="$TOP_LIBRARY" tb_accumulator
echo "GHDL advanced example: PASS"
