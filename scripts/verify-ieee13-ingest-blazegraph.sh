#!/usr/bin/env bash
# Run ingest-blazegraph for IEEE 13 (requires Blazegraph + exported CDPSM XML).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

# shellcheck source=scripts/lib/docker.sh
source "${ROOT}/scripts/lib/docker.sh"

if ! curl -sf http://localhost:8889/bigdata/status >/dev/null 2>&1; then
  "${ROOT}/scripts/start-blazegraph.sh"
fi

run_cli() {
  if command -v grid-synth >/dev/null 2>&1; then
    grid-synth ingest-blazegraph ieee13
  elif [[ -x "${ROOT}/.venv/bin/grid-synth" ]]; then
    "${ROOT}/.venv/bin/grid-synth" ingest-blazegraph ieee13
  else
    PYTHONPATH="${ROOT}/src" python3 -m alteia_grid_synth.cli ingest-blazegraph ieee13
  fi
}

export BLAZEGRAPH_SPARQL_URL="${BLAZEGRAPH_SPARQL_URL:-http://localhost:8889/bigdata/namespace/kb/sparql}"
run_cli

echo "OK: ingest-blazegraph ieee13"
