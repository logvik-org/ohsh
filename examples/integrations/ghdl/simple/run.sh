#!/usr/bin/env bash
# GHDL, simple project: every module is in the default `work` library.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EXAMPLES="$(cd "$HERE/../../.." && pwd)"
BUILD="$HERE/build"
rm -rf "$BUILD"
mkdir -p "$BUILD"
GHDL_FLAGS=(--std=08 --workdir="$BUILD")

ohsh -t "$EXAMPLES/projects/simple" -o "$BUILD" accumulator

while IFS= read -r f; do
  ghdl -a "${GHDL_FLAGS[@]}" "$f"
done < "$BUILD/work_vhdl.src"

ghdl -a "${GHDL_FLAGS[@]}" "$EXAMPLES/testbenches/tb_accumulator.vhd"
ghdl -e "${GHDL_FLAGS[@]}" tb_accumulator
ghdl -r "${GHDL_FLAGS[@]}" tb_accumulator
echo "GHDL simple example: PASS"
