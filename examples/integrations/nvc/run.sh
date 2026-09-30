#!/usr/bin/env bash
# NVC integration example.
#
# 1. Generate ordered, per-library source lists with ohsh.
# 2. Analyze each library with `nvc --work=<lib> -a`, in the order ohsh
#    writes to libraries.src. `-L.` lets `work` find `math_lib`.
# 3. Elaborate and run the self-checking testbench.
#
# Verified in CI against the demo project (see .github/workflows/integration.yml).
# Reuses the testbench from the GHDL example.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEMO="$HERE/../../demo_project"
BUILD="$HERE/build"
TB="$HERE/../ghdl/tb_accumulator.vhd"
STD=2008

rm -rf "$BUILD"
mkdir -p "$BUILD"

# 1. Resolve the design sources into per-library .src lists.
ohsh -t "$DEMO" -o "$BUILD" accumulator

# NVC creates library directories in the cwd, so work inside $BUILD.
cd "$BUILD"

analyze_list() {  # <library> <src-file>
  local lib="$1" list="$2"
  [ -f "$list" ] || return 0
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    echo ">> nvc --work=$lib -a $f"
    nvc --std="$STD" -L. --work="$lib" -a "$f"
  done < "$list"
}

# 2. Compile the libraries in the order ohsh wrote to libraries.src.
while IFS= read -r lib; do
  analyze_list "$lib" "$BUILD/${lib}_vhdl.src"
done < "$BUILD/libraries.src"

# Compile the testbench into work.
nvc --std="$STD" -L. --work=work -a "$TB"

# 3. Elaborate and run.
nvc --std="$STD" -L. --work=work -e tb_accumulator
nvc --std="$STD" -L. --work=work -r tb_accumulator

echo "NVC example: PASS"
