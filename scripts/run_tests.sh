#!/usr/bin/env bash
# Run all validation suites. Extra args go to robot, e.g. scripts/run_tests.sh --include counts
set -u
cd "$(dirname "$0")/.."
OUT="${RESULTS_DIR:-results}"
PYTHON="${PYTHON:-python}"

"$PYTHON" scripts/wait_for_db.py || exit 2
"$PYTHON" -m robot --pythonpath . --outputdir "$OUT" "$@" tests
rc=$?
"$PYTHON" scripts/summarize_results.py "$OUT/output.xml" "$OUT"
exit $rc
