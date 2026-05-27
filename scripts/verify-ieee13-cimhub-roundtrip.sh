#!/usr/bin/env bash
# Run cimhub-roundtrip for IEEE 13 (requires Blazegraph ingest + lab Java/CIMHub).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

export BLAZEGRAPH_SPARQL_URL="${BLAZEGRAPH_SPARQL_URL:-http://localhost:8889/bigdata/namespace/kb/sparql}"

run_cli() {
  if command -v grid-synth >/dev/null 2>&1; then
    grid-synth cimhub-roundtrip ieee13
  elif [[ -x "${ROOT}/.venv/bin/grid-synth" ]]; then
    "${ROOT}/.venv/bin/grid-synth" cimhub-roundtrip ieee13
  else
    PYTHONPATH="${ROOT}/src" python3 -m alteia_grid_synth.cli cimhub-roundtrip ieee13
  fi
}

if command -v java >/dev/null 2>&1 && [[ -f /opt/cimhub/releases/cimhub-1.1.0.jar ]]; then
  run_cli
else
  IMAGE="${ALTEIA_LAB_IMAGE:-alteia-grid-synth:lab}"
  # shellcheck source=scripts/lib/docker.sh
  source "${ROOT}/scripts/lib/docker.sh"
  resolve_docker || exit 1
  "${DOCKER[@]}" run --rm --network host \
    -u "$(id -u):$(id -g)" \
    -v "${ROOT}:/app" \
    -e BLAZEGRAPH_SPARQL_URL="${BLAZEGRAPH_SPARQL_URL}" \
    -w /app \
    "${IMAGE}" \
    bash -c './scripts/verify-ieee13-cimhub-roundtrip.sh'
  exit 0
fi

DSS_DIR="${ROOT}/work/ieee13/render/opendss"
GLM_DIR="${ROOT}/work/ieee13/render/gridlabd"
if [[ ! -d "${DSS_DIR}" ]] || [[ -z "$(find "${DSS_DIR}" -name '*.dss' -print -quit)" ]]; then
  echo "ERROR: missing OpenDSS roundtrip under ${DSS_DIR}" >&2
  exit 1
fi
if [[ ! -d "${GLM_DIR}" ]] || [[ -z "$(find "${GLM_DIR}" -name '*.glm' -print -quit)" ]]; then
  echo "ERROR: missing GridLAB-D roundtrip under ${GLM_DIR}" >&2
  exit 1
fi

echo "OK: cimhub-roundtrip ieee13"
