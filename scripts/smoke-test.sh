#!/usr/bin/env bash
# Check that an installed ohsh (not the source tree) works: it reports the
# expected version and resolves the demo project.
# Usage: scripts/smoke-test.sh <expected-version>
set -euo pipefail

expected_version="$1"
demo_project="$(cd "$(dirname "$0")/../examples/demo_project" && pwd)"
output_dir="$(mktemp -d)"

ohsh --version | grep -Fx "ohsh $expected_version"
ohsh -t "$demo_project" -o "$output_dir" accumulator
diff <(printf 'math_lib\nwork\n') "$output_dir/libraries.src"
echo "Smoke test passed for ohsh $expected_version"
