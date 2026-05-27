#!/usr/bin/env bash
# Start local Blazegraph (Story 1.1) — works without Docker Compose v2.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/lib/docker.sh
source "${ROOT}/scripts/lib/docker.sh"

BLAZEGRAPH_IMAGE="${BLAZEGRAPH_IMAGE:-lyrasis/blazegraph:2.1.5}"
HOST_PORT="${BLAZEGRAPH_HOST_PORT:-8889}"
CONTAINER_PORT=8080

resolve_docker

NAME="$(blazegraph_container_name)"

if "${DOCKER[@]}" ps -a --format '{{.Names}}' | grep -qx "${NAME}"; then
  if ! "${DOCKER[@]}" ps --format '{{.Names}}' | grep -qx "${NAME}"; then
    echo "==> Starting existing container: ${NAME}"
    "${DOCKER[@]}" start "${NAME}"
  else
    echo "==> Container already running: ${NAME}"
  fi
else
  echo "==> Pulling and starting ${BLAZEGRAPH_IMAGE} as ${NAME} on port ${HOST_PORT}"
  "${DOCKER[@]}" run -d \
    --name "${NAME}" \
    -p "${HOST_PORT}:${CONTAINER_PORT}" \
    "${BLAZEGRAPH_IMAGE}"
fi

echo "==> Waiting for Blazegraph health at http://localhost:${HOST_PORT}/bigdata/status"
for _ in $(seq 1 30); do
  if curl -sf "http://localhost:${HOST_PORT}/bigdata/status" >/dev/null; then
    echo "OK  Blazegraph is up — SPARQL: http://localhost:${HOST_PORT}/bigdata/sparql"
    exit 0
  fi
  sleep 2
done

echo "ERROR: Blazegraph did not become healthy in time" >&2
"${DOCKER[@]}" logs --tail 30 "${NAME}" >&2 || true
exit 1
