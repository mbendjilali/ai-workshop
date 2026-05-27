#!/usr/bin/env bash
# Verify IEEE 13 mRID stability: two OpenDSS UUID exports with the same uuids.dat must match.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/lib/docker.sh
source "${ROOT}/scripts/lib/docker.sh"
FEEDER_DIR="${ROOT}/feeders/ieee13"
PROBE_NAME="mrid_stability.dss"
WORK_DIR="${FEEDER_DIR}/work"
IMAGE="${ALTEIA_LAB_IMAGE:-alteia-grid-synth:lab}"

run_opendss_in_feeder() {
  if command -v opendsscmd >/dev/null 2>&1; then
    (cd "${FEEDER_DIR}" && opendsscmd "${PROBE_NAME}")
    return 0
  fi
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    # shellcheck disable=SC2046
    docker run --rm $(docker_user_mapping_args) \
      -v "${ROOT}:/app" \
      -w "/app/feeders/ieee13" \
      "${IMAGE}" \
      opendsscmd "${PROBE_NAME}"
    return 0
  fi
  echo "ERROR: opendsscmd not on PATH and Docker unavailable — cannot run mRID stability probe" >&2
  return 2
}

rm -rf "${WORK_DIR}"
mkdir -p "${WORK_DIR}"

echo "Running mRID stability probe in ${FEEDER_DIR} ..."
run_opendss_in_feeder

OUT1="${WORK_DIR}/_mrid_probe_1.dat"
OUT2="${WORK_DIR}/_mrid_probe_2.dat"

for f in "${OUT1}" "${OUT2}"; do
  if [[ ! -f "${f}" ]]; then
    echo "ERROR: expected export missing: ${f}" >&2
    exit 1
  fi
done

if cmp -s "${OUT1}" "${OUT2}"; then
  echo "OK: mRID exports are byte-identical ($(wc -c < "${OUT1}" | tr -d ' ') bytes)"
  exit 0
fi

echo "ERROR: mRID export files differ" >&2
diff -u "${OUT1}" "${OUT2}" | head -40 >&2 || true
exit 1
