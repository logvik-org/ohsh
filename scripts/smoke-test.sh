#!/usr/bin/env bash
# Check that an installed ohsh (not the source tree) works: it reports the
# expected version and resolves the advanced example project.
# Usage: scripts/smoke-test.sh <expected-version>
set -euo pipefail

expected_version="$1"
project="$(cd "$(dirname "$0")/../examples/projects/advanced" && pwd)"
output_dir="$(mktemp -d)"

ohsh --version | grep -Fx "ohsh $expected_version"
ohsh -t "$project" -w dsp_lib -o "$output_dir" accumulator
diff <(printf 'util_lib\nmath_lib\ndsp_lib\n') "$output_dir/libraries.src"
echo "Smoke test passed for ohsh $expected_version"
