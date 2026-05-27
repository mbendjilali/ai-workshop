#!/usr/bin/env bash
# P0 IEEE 13 spine verification gate — required before marking Epic 1 OpenDSS stories done.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${ALTEIA_LAB_IMAGE:-alteia-grid-synth:lab}"
# shellcheck source=scripts/lib/docker.sh
source "${ROOT}/scripts/lib/docker.sh"

preflight_feeder_writable() {
  local ini="${ROOT}/feeders/ieee13/opendsscmd.ini"
  if [[ -f "${ini}" ]] && [[ ! -w "${ini}" ]]; then
    echo "WARN: removing root-owned ${ini} (leftover from pre -u Docker runs)" >&2
    resolve_docker || return 1
    "${DOCKER[@]}" run --rm \
      -v "${ROOT}:/app" \
      -w /app/feeders/ieee13 \
      "${IMAGE}" \
      rm -f opendsscmd.ini
  fi
}

preflight_feeder_writable

echo "==> P0 spine verification (IEEE 13 export + mRID stability + hub stages + pytest)"
with_docker_access bash -c "
  set -euo pipefail
  cd '${ROOT}'
  ./scripts/verify-ieee13-export-cim100.sh
  ./scripts/verify-ieee13-mrid-stability.sh
  ./scripts/verify-ieee13-ingest-blazegraph.sh
  ./scripts/verify-ieee13-cimhub-roundtrip.sh
  ./scripts/verify-ieee13-pf-diff.sh
  if [[ -x .venv/bin/pytest ]]; then
    .venv/bin/pytest tests/ -q
  else
    python3 -m pytest tests/ -q
  fi
"

echo "==> P0 spine verification passed."
