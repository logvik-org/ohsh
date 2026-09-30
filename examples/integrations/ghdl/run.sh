#!/usr/bin/env bash
# GHDL integration example.
#
# 1. Generate ordered, per-library source lists with ohsh.
# 2. Analyze each library with `ghdl -a --work=<lib>`, in the order ohsh
#    writes to libraries.src.
# 3. Elaborate and run the self-checking testbench.
#
# Verified in CI against the demo project (see .github/workflows/integration.yml).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEMO="$HERE/../../demo_project"
BUILD="$HERE/build"
STD=08

rm -rf "$BUILD"
mkdir -p "$BUILD"

# 1. Resolve the design sources into per-library .src lists.
ohsh -t "$DEMO" -o "$BUILD" accumulator

# Common GHDL flags: store libraries in $BUILD and also search it for
# secondary libraries (so `work` can find `math_lib`).
GHDL_FLAGS=(--workdir="$BUILD" -P"$BUILD" --std="$STD")

analyze_list() {  # <library> <src-file>
  local lib="$1" list="$2"
  [ -f "$list" ] || return 0
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    echo ">> ghdl -a --work=$lib $f"
    ghdl -a "${GHDL_FLAGS[@]}" --work="$lib" "$f"
  done < "$list"
}

# 2. Compile the libraries in the order ohsh wrote to libraries.src.
while IFS= read -r lib; do
  analyze_list "$lib" "$BUILD/${lib}_vhdl.src"
done < "$BUILD/libraries.src"

# Compile the testbench (not part of the design manifest) into work.
ghdl -a "${GHDL_FLAGS[@]}" --work=work "$HERE/tb_accumulator.vhd"

# 3. Elaborate and run.
ghdl -e "${GHDL_FLAGS[@]}" tb_accumulator
ghdl -r "${GHDL_FLAGS[@]}" tb_accumulator

echo "GHDL example: PASS"
