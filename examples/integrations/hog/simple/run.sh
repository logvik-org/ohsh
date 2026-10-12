#!/usr/bin/env bash
# hog, simple project: one library, written by ohsh as list/demo_lib.src.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EXAMPLES="$(cd "$HERE/../../.." && pwd)"
BUILD="$HERE/build"
rm -rf "$BUILD"
mkdir -p "$BUILD"

# hog is cloned once into the shared hog/build directory and reused by both
# examples. Set HOG_ROOT to use an existing checkout instead.
HOG_ROOT="${HOG_ROOT:-$HERE/../build/Hog}"
HOG_VERSION="${HOG_VERSION:-Hog2026.2-6}"
if [ ! -d "$HOG_ROOT/Tcl" ]; then
  git clone --depth 1 --branch "$HOG_VERSION" https://gitlab.com/hog-cern/Hog.git "$HOG_ROOT"
fi

# In a real hog project this is your repository root, and the list files go in
# Top/<project>/list/. Here the examples directory plays the repository.
REPO_ROOT="$EXAMPLES"
LIST_DIR="$BUILD/Top/demo/list"

# hog reads list-file entries relative to the repository root.
ohsh --format hog -t "$EXAMPLES/projects/simple" -w demo_lib -o "$LIST_DIR" \
  --relative-to "$REPO_ROOT" accumulator

tclsh "$HERE/../check_hog_lists.tcl" "$HOG_ROOT" "$REPO_ROOT" accumulator "$LIST_DIR"/*.src
echo "hog simple example: PASS"
