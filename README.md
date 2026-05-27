# alteia-grid-synth

Alteia Synthetic Grid Network Data Generator — container-first CDPSM hub pipeline for GridOS Tier A artifacts.

This repository scaffolds the IEEE 13 spine (Epic 1). Story 1.1 delivers the lab Docker image and Typer CLI stub; Story 1.2 adds the IEEE 13 OpenDSS seed under `feeders/ieee13/`.

## Prerequisites

- Docker Engine 24+
- Docker Compose v2 (optional — `scripts/start-blazegraph.sh` uses plain `docker run`)
- Git

## Docker host setup (one-time, Ubuntu)

After `sudo apt install docker.io`, two common issues block verification:

1. **Permission denied on `/var/run/docker.sock`** — your user is not in the `docker` group yet.
2. **`docker compose` unknown command** — Compose v2 plugin not installed.

```bash
sudo usermod -aG docker "$USER"
sudo apt install -y docker-compose-v2
newgrp docker    # or log out and log back in
```

Check readiness:

```bash
chmod +x scripts/*.sh
./scripts/docker-preflight.sh
```

## Quick start

### 1. Build the lab image

From the repository root:

```bash
docker build -f docker/Dockerfile -t alteia-grid-synth:lab .
```

The image extends [`gridappsd/cimhub:1.1.0`](https://hub.docker.com/r/gridappsd/cimhub) for OpenDSS, CIMHub JAR, GridLAB-D, and Java 11, then adds Python 3.10+ with this package installed.

### 2. Start Blazegraph

With Compose v2:

```bash
docker compose -f docker/docker-compose.yml up -d blazegraph
```

Without Compose (equivalent):

```bash
./scripts/start-blazegraph.sh
```

SPARQL endpoint (host): **http://localhost:8889/bigdata/sparql**

Health check:

```bash
curl -sf http://localhost:8889/bigdata/status
```

### All-in-one verification (build + Blazegraph + G-4 checks)

```bash
./scripts/verify-all.sh
```

### 3. Verify toolchain inside the lab image

Run individually:

```bash
docker run --rm alteia-grid-synth:lab opendsscmd -h
docker run --rm alteia-grid-synth:lab java -version
docker run --rm alteia-grid-synth:lab gridlabd --version
docker run --rm alteia-grid-synth:lab grid-synth --help
docker run --rm alteia-grid-synth:lab python -c "import alteia_grid_synth; print(alteia_grid_synth.__version__)"
```

Or run the bundled script:

```bash
chmod +x scripts/verify-lab-image.sh
./scripts/verify-lab-image.sh
```

**GridLAB-D (`gridlabd --version`) is required (readiness G-4)** — Story 2.4 dual PF gate depends on it.

### 4. Interactive lab shell (optional)

Starts Blazegraph + lab container with `BLAZEGRAPH_SPARQL_URL` set for in-network SPARQL:

```bash
docker compose -f docker/docker-compose.yml run --rm lab
# inside container:
echo $BLAZEGRAPH_SPARQL_URL   # http://blazegraph:8080/bigdata/sparql
grid-synth --help
```

## Pinned tool versions

See [docs/docker-tool-versions.md](docs/docker-tool-versions.md) for the full pin table and upgrade policy (NFR-10).

## IEEE 13 feeder seed (Story 1.2)

OpenDSS master and stable UUID map:

```
feeders/ieee13/
  Master.dss
  uuids.dat
  IEEE13NodeExtra_BusXY.csv
```

Verify mRID stability (requires `opendsscmd` on PATH or Docker lab image):

```bash
./scripts/verify-ieee13-mrid-stability.sh
```

Export combined CDPSM XML (Story 1.3):

```bash
./scripts/verify-ieee13-export-cim100.sh
# or: grid-synth export-cim100 ieee13
```

**P0 spine gate** (export + mRID + ingest + roundtrip + pf-diff + pytest):

```bash
./scripts/verify-p0-spine.sh
```

Uses `sg docker` automatically when your user is in the `docker` group but the current shell is not.

Feeder CLI id: `ieee13`. See [feeders/ieee13/README.md](feeders/ieee13/README.md) for provenance and CIM export parameters.

Hub stages (Stories 1.4–1.6):

```bash
grid-synth ingest-blazegraph ieee13    # requires Blazegraph on :8889
grid-synth cimhub-roundtrip ieee13   # requires prior ingest + Java/CIMHub
grid-synth pf-diff ieee13            # gold vs roundtrip OpenDSS PF
```

## Local Python development (optional)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
grid-synth --help
pytest tests/unit/
```

## Scope (through Story 1.6)

**Included:** repo layout, Typer CLI (`export-cim100`, `ingest-blazegraph`, `cimhub-roundtrip`, `pf-diff`, stub `run`/`validate`/`pack`), Docker lab image (Java/CIMHub fix), Blazegraph compose, IEEE 13 P0 hub spine through PF diff.

**Not yet implemented:** validation gate, fabric packager, full binding pack (Story 2.1), CI workflows — see Epic 2+.

## Architecture

Structure follows `_bmad-output/planning-artifacts/architecture.md` § Structure Patterns. Application code lives at this repo root; BMAD planning artifacts remain under `_bmad-output/`.
