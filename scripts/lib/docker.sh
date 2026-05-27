#!/usr/bin/env bash
# Shared Docker helpers for alteia-grid-synth lab scripts.

resolve_docker() {
  if docker info >/dev/null 2>&1; then
    DOCKER=(docker)
    return 0
  fi

  if sudo -n docker info >/dev/null 2>&1; then
    echo "NOTE: using sudo docker (prefer: sudo usermod -aG docker \"\$USER\" && newgrp docker)" >&2
    DOCKER=(sudo docker)
    return 0
  fi

  cat >&2 <<'EOF'
ERROR: Docker is installed but this user cannot access /var/run/docker.sock.

One-time fix (Ubuntu):
  sudo usermod -aG docker "$USER"
  newgrp docker          # or log out and log back in

Optional — Docker Compose v2 plugin:
  sudo apt install -y docker-compose-v2

Then re-run this script.
EOF
  return 1
}

resolve_compose() {
  if "${DOCKER[@]}" compose version >/dev/null 2>&1; then
    COMPOSE=("${DOCKER[@]}" compose)
    return 0
  fi

  if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE=(docker-compose)
    return 0
  fi

  COMPOSE=()
  return 1
}

blazegraph_container_name() {
  echo "${BLAZEGRAPH_CONTAINER:-alteia-blazegraph}"
}
