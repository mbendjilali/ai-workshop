#!/usr/bin/env bash
# Run export-cim100 for IEEE 13 and validate combined CDPSM XML.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

if command -v grid-synth >/dev/null 2>&1; then
  grid-synth export-cim100 ieee13
elif [[ -x "${ROOT}/.venv/bin/grid-synth" ]]; then
  "${ROOT}/.venv/bin/grid-synth" export-cim100 ieee13
else
  PYTHONPATH="${ROOT}/src" python3 -m alteia_grid_synth.cli export-cim100 ieee13
fi

OUT="${ROOT}/work/ieee13/cim/ieee13cdpsm.xml"
if [[ ! -f "${OUT}" ]]; then
  echo "ERROR: expected output missing: ${OUT}" >&2
  exit 1
fi

echo "OK: ${OUT} ($(wc -c < "${OUT}" | tr -d ' ') bytes)"
