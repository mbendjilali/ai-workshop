#!/usr/bin/env bash
# Check Docker host readiness for alteia-grid-synth lab workflows.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/lib/docker.sh
source "${ROOT}/scripts/lib/docker.sh"

echo "==> Docker preflight"

resolve_docker
echo "OK  Docker daemon reachable via: ${DOCKER[*]}"

if resolve_compose; then
  echo "OK  Compose available via: ${COMPOSE[*]}"
else
  echo "WARN Compose not found — use scripts/start-blazegraph.sh (plain docker run) or:"
  echo "     sudo apt install -y docker-compose-v2"
fi

if groups | grep -qw docker; then
  echo "OK  User is in the docker group"
else
  echo "WARN User is not in the docker group — docker commands may require sudo or newgrp"
  echo "     sudo usermod -aG docker \"\$USER\" && newgrp docker"
fi

echo "==> Preflight complete"
