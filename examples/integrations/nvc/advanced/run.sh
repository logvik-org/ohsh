#!/usr/bin/env bash
# NVC, advanced project: three libraries, compiled in the order ohsh writes to
# libraries.src. The top library is named with -w.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EXAMPLES="$(cd "$HERE/../../.." && pwd)"
BUILD="$HERE/build"
rm -rf "$BUILD"
mkdir -p "$BUILD"
TOP_LIBRARY=dsp_lib
# NVC keeps its libraries in the current directory, and -L. lets each library
# find the ones analyzed before it.
cd "$BUILD"

ohsh -t "$EXAMPLES/projects/advanced" -w "$TOP_LIBRARY" -o "$BUILD" accumulator

while IFS= read -r lib; do
  while IFS= read -r f; do
    nvc --std=2008 -L. --work="$lib" -a "$f"
  done < "$BUILD/${lib}_vhdl.src"
done < "$BUILD/libraries.src"

# The testbench goes into the top library, where `work.accumulator` resolves.
nvc --std=2008 -L. --work="$TOP_LIBRARY" -a "$EXAMPLES/testbenches/tb_accumulator.vhd"
nvc --std=2008 -L. --work="$TOP_LIBRARY" -e tb_accumulator
nvc --std=2008 -L. --work="$TOP_LIBRARY" -r tb_accumulator
echo "NVC advanced example: PASS"
