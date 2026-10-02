#!/usr/bin/env bash
# Run the integration examples that need only free tools, the same set CI runs.
# An example fails if it exits with an error or prints a deprecation warning.
#
#   scripts/run-examples.sh                          # all of them
#   scripts/run-examples.sh ghdl/simple vunit/advanced
#
# Needs ohsh and the `examples` extra on PATH (`make examples` takes care of
# that), plus Icarus Verilog, GHDL, NVC, git, and tclsh with tcllib.
set -uo pipefail

INTEGRATIONS="$(cd "$(dirname "$0")/../examples/integrations" && pwd)"
ALL_EXAMPLES=(
  cocotb_makefile/simple cocotb_makefile/advanced
  cocotb_runner/simple cocotb_runner/advanced
  vunit/simple vunit/advanced
  ghdl/simple ghdl/advanced
  nvc/simple nvc/advanced
  uvvm/simple uvvm/advanced
  hog/simple hog/advanced
)
export VUNIT_SIMULATOR="${VUNIT_SIMULATOR:-ghdl}"

command_for() {
  case "$1" in
    cocotb_makefile/*) echo "make" ;;
    cocotb_runner/*) echo "python runner.py" ;;
    vunit/*) echo "python run.py" ;;
    *) echo "bash run.sh" ;;
  esac
}

# In GitHub Actions, each example gets its own collapsible section in the log.
start_section() {
  if [ "${GITHUB_ACTIONS:-}" = true ]; then echo "::group::$1"; else echo "=== $1"; fi
}
end_section() {
  if [ "${GITHUB_ACTIONS:-}" = true ]; then echo "::endgroup::"; fi
}

run_example() {  # <example>
  local example="$1" output status command
  read -ra command <<< "$(command_for "$example")"
  output="$(mktemp)"
  (cd "$INTEGRATIONS/$example" && "${command[@]}") 2>&1 | tee "$output"
  status=${PIPESTATUS[0]}
  if [ "$status" -eq 0 ] && grep -iqE "DeprecationWarning|is deprecated" "$output"; then
    echo "$example printed a deprecation warning"
    status=1
  fi
  rm -f "$output"
  return "$status"
}

examples=("$@")
if [ ${#examples[@]} -eq 0 ]; then
  examples=("${ALL_EXAMPLES[@]}")
fi

failed=()
for example in "${examples[@]}"; do
  if [ ! -d "$INTEGRATIONS/$example" ]; then
    echo "Unknown example: $example" >&2
    failed+=("$example")
    continue
  fi
  start_section "$example"
  run_example "$example" || failed+=("$example")
  end_section
done

echo
echo "Ran ${#examples[@]} example(s), ${#failed[@]} failed."
for example in "${failed[@]}"; do
  echo "  FAILED: $example"
done
[ ${#failed[@]} -eq 0 ]
