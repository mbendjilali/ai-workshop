#!/usr/bin/env bash
# Run pf-diff for IEEE 13 (requires gold seed + CIMHub roundtrip OpenDSS).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

run_cli() {
  if command -v grid-synth >/dev/null 2>&1; then
    grid-synth pf-diff ieee13
  elif [[ -x "${ROOT}/.venv/bin/grid-synth" ]]; then
    "${ROOT}/.venv/bin/grid-synth" pf-diff ieee13
  else
    PYTHONPATH="${ROOT}/src" python3 -m alteia_grid_synth.cli pf-diff ieee13
  fi
}

if command -v opendsscmd >/dev/null 2>&1; then
  run_cli
else
  IMAGE="${ALTEIA_LAB_IMAGE:-alteia-grid-synth:lab}"
  # shellcheck source=scripts/lib/docker.sh
  source "${ROOT}/scripts/lib/docker.sh"
  resolve_docker || exit 1
  "${DOCKER[@]}" run --rm --network host \
    -u "$(id -u):$(id -g)" \
    -v "${ROOT}:/app" \
    -w /app \
    "${IMAGE}" \
    bash -c './scripts/verify-ieee13-pf-diff.sh'
  exit 0
fi

REPORT="${ROOT}/work/ieee13/validation/pf-diff-report.json"
if [[ ! -f "${REPORT}" ]]; then
  echo "ERROR: pf-diff report missing: ${REPORT}" >&2
  exit 1
fi

echo "OK: pf-diff ieee13 -> ${REPORT}"
