#!/usr/bin/env bash
# hog, advanced project: runs the project's pre-creation.tcl the way hog would and
# checks the list files it writes with hog's own reader.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EXAMPLES="$(cd "$HERE/../../.." && pwd)"

# hog is cloned once into the shared hog/build directory and reused by both
# examples. Set HOG_ROOT to use an existing checkout instead.
HOG_ROOT="${HOG_ROOT:-$HERE/../build/Hog}"
HOG_VERSION="${HOG_VERSION:-Hog2026.2-6}"
if [ ! -d "$HOG_ROOT/Tcl" ]; then
  git clone --depth 1 --branch "$HOG_VERSION" https://gitlab.com/hog-cern/Hog.git "$HOG_ROOT"
fi

# In a real hog project Top/ sits in the repository root. Here the examples
# directory plays the repository, so the entries read projects/advanced/...
REPO_ROOT="$EXAMPLES"
PROJECT_DIR="$HERE/Top/demo"
rm -rf "$PROJECT_DIR/list"

tclsh "$HERE/../check_hog_lists.tcl" "$HOG_ROOT" "$REPO_ROOT" accumulator "$PROJECT_DIR"
echo "hog advanced example: PASS"
