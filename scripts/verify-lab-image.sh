#!/usr/bin/env bash
# Verify alteia-grid-synth lab image toolchain (Story 1.1 / G-4).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/lib/docker.sh
source "${ROOT}/scripts/lib/docker.sh"

IMAGE="${LAB_IMAGE:-alteia-grid-synth:lab}"

resolve_docker

echo "==> Verifying lab image: ${IMAGE}"

run_check() {
  local label="$1"
  shift
  echo "--- ${label}"
  "${DOCKER[@]}" run --rm "${IMAGE}" "$@"
  echo
}

run_check "OpenDSS (opendsscmd -h)" opendsscmd -h
run_check "Java (java -version)" java -version
run_check "GridLAB-D (gridlabd --version)" gridlabd --version
run_check "grid-synth CLI (--help)" grid-synth --help
run_check "Python package import" python -c "import alteia_grid_synth; print(alteia_grid_synth.__version__)"

echo "==> All lab image checks passed."
