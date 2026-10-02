#!/usr/bin/env bash
# NVC, simple project: every module is in the default `work` library.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EXAMPLES="$(cd "$HERE/../../.." && pwd)"
BUILD="$HERE/build"
rm -rf "$BUILD"
mkdir -p "$BUILD"
# NVC keeps its libraries in the current directory.
cd "$BUILD"

ohsh -t "$EXAMPLES/projects/simple" -o "$BUILD" accumulator

while IFS= read -r f; do
  nvc --std=2008 -a "$f"
done < "$BUILD/work_vhdl.src"

nvc --std=2008 -a "$EXAMPLES/testbenches/tb_accumulator.vhd"
nvc --std=2008 -e tb_accumulator
nvc --std=2008 -r tb_accumulator
echo "NVC simple example: PASS"
