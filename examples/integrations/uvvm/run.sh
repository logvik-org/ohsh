#!/usr/bin/env bash
# UVVM integration example.
#
# 1. Compile the UVVM utility library (uvvm_util) with GHDL.
# 2. Generate the design source lists with ohsh and compile them.
# 3. Compile and run a UVVM testbench.
#
# Verified in CI against the demo project (see .github/workflows/integration.yml).
#
# Set UVVM_ROOT to an existing UVVM checkout to skip the clone.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEMO="$HERE/../../demo_project"
BUILD="$HERE/build"
STD=08
# UVVM needs the Synopsys + relaxed extensions under GHDL.
GFLAGS=(--workdir="$BUILD" -P"$BUILD" --std="$STD" -fsynopsys -frelaxed)

rm -rf "$BUILD"
mkdir -p "$BUILD"

# 0. Obtain UVVM.
UVVM_ROOT="${UVVM_ROOT:-$BUILD/UVVM}"
if [ ! -d "$UVVM_ROOT/uvvm_util" ]; then
  echo ">> Cloning UVVM into $UVVM_ROOT"
  git clone --depth 1 https://github.com/UVVM/UVVM.git "$UVVM_ROOT"
fi

# 1. Compile uvvm_util in the order given by its own compile_order.txt.
UTIL_SCRIPT="$UVVM_ROOT/uvvm_util/script"
echo ">> Compiling uvvm_util"
while IFS= read -r line; do
  case "$line" in '' | \#*) continue ;; esac
  ( cd "$UTIL_SCRIPT" && ghdl -a "${GFLAGS[@]}" --work=uvvm_util "$line" )
done < "$UTIL_SCRIPT/compile_order.txt"

# 2. Resolve and compile the design, in the order ohsh wrote to libraries.src.
ohsh -t "$DEMO" -o "$BUILD" accumulator

compile_list() {  # <library> <src-file>
  local lib="$1" list="$2"
  [ -f "$list" ] || return 0
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    ghdl -a "${GFLAGS[@]}" --work="$lib" "$f"
  done < "$list"
}
while IFS= read -r lib; do
  compile_list "$lib" "$BUILD/${lib}_vhdl.src"
done < "$BUILD/libraries.src"

# 3. Compile and run the UVVM testbench.
ghdl -a "${GFLAGS[@]}" --work=work "$HERE/tb_accumulator_uvvm.vhd"
ghdl -e "${GFLAGS[@]}" tb_accumulator_uvvm
( cd "$BUILD" && ghdl -r "${GFLAGS[@]}" tb_accumulator_uvvm )

echo "UVVM example: PASS"
