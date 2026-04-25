#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT/src"

python3 -m py_compile src/star_index/*.py scripts/*.py tests/*.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/generate_examples.py

python3 -m star_index validate \
  --xml "$ROOT/examples/sample-output/sample-user-stars.xml" \
  --raw-json "$ROOT/examples/sample-output/sample-user-stars.raw.json" \
  --summary "$ROOT/examples/sample-output/sample-user-stars.summary.md" \
  --manifest "$ROOT/examples/sample-output/sample-user-stars.manifest.json" \
  --bundle-dir "$ROOT/examples/sample-output/corpus"

if command -v openspec >/dev/null 2>&1; then
  openspec validate agent-ready-oss-corpus --strict
else
  echo "Skipping openspec validation; openspec is not installed."
fi
