#!/usr/bin/env bash
# hog, advanced project: one hog list file per library in libraries.src.
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
mkdir -p "$LIST_DIR"

# hog reads list-file entries relative to the repository root, while ohsh
# writes absolute paths.
write_hog_list() {  # <ohsh .src file> <hog list file>
  while IFS= read -r f; do
    realpath --relative-to="$REPO_ROOT" "$f"
  done < "$1" > "$2"
}

ohsh -t "$EXAMPLES/projects/advanced" -w dsp_lib -o "$BUILD" accumulator
while IFS= read -r lib; do
  write_hog_list "$BUILD/${lib}_vhdl.src" "$LIST_DIR/$lib.src"
done < "$BUILD/libraries.src"

tclsh "$HERE/../check_hog_lists.tcl" "$HOG_ROOT" "$REPO_ROOT" "$LIST_DIR"/*.src
echo "hog advanced example: PASS"
