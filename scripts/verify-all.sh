#!/usr/bin/env bash
# Full Story 1.1 verification: build lab image, start Blazegraph, run toolchain checks.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${LAB_IMAGE:-alteia-grid-synth:lab}"

echo "==> Step 1/4: Docker preflight"
"${ROOT}/scripts/docker-preflight.sh"

echo
echo "==> Step 2/4: Build lab image"
# shellcheck source=scripts/lib/docker.sh
source "${ROOT}/scripts/lib/docker.sh"
resolve_docker
"${DOCKER[@]}" build -f "${ROOT}/docker/Dockerfile" -t "${IMAGE}" "${ROOT}"

echo
echo "==> Step 3/4: Start Blazegraph"
"${ROOT}/scripts/start-blazegraph.sh"

echo
echo "==> Step 4/4: Verify lab image tools (including GridLAB-D G-4)"
LAB_IMAGE="${IMAGE}" "${ROOT}/scripts/verify-lab-image.sh"

echo
echo "==> Story 1.1 Docker verification complete."
