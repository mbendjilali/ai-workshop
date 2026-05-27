# Docker Lab Image — Pinned Tool Versions

Documented per NFR-10. Resolved versions are captured at image build time; re-run
`scripts/verify-lab-image.sh` after any bump.

| Component | Pinned version / tag | Source | Verification command |
|-----------|----------------------|--------|--------------------|
| CIMHub base image | `gridappsd/cimhub:1.1.0` | [GRIDAPPSD/CIMHub](https://github.com/GRIDAPPSD/CIMHub) Docker Hub | Inherited — see OpenDSS / GridLAB-D / Java rows |
| CIMHub JAR release | `2024.06.0` (bundled in base) | [CIMHub Releases](https://github.com/GRIDAPPSD/CIMHub/releases) | `ls /opt/cimhub/releases` inside lab image |
| OpenDSS | Bundled with CIMHub 1.1.0 | CIMHub `opendsscmd/linux` | `opendsscmd -h` |
| GridLAB-D | Bundled with CIMHub 1.1.0 | CIMHub `gridlabd/bin` | `gridlabd --version` |
| Java runtime | OpenJDK 11 (copied from CIMHub 1.1.0 base) | CIMHub bullseye layer | `java -version` |
| Python | 3.10 (official `python:3.10-bookworm`) | [Docker Hub python](https://hub.docker.com/_/python) | `python --version` |
| alteia-grid-synth | `0.1.0` (pyproject) | This repo | `python -c "import alteia_grid_synth; print(alteia_grid_synth.__version__)"` |
| Typer | `>=0.9.0,<0.16` (pyproject) | PyPI | `grid-synth --help` |
| Blazegraph (compose) | `lyrasis/blazegraph:2.1.5` | [Blazegraph Docker](https://hub.docker.com/r/lyrasis/blazegraph) | `curl -sf http://localhost:8889/bigdata/status` |

## Upgrade policy

1. **Bump one component at a time** — never change CIMHub base, Blazegraph, and Python in a single PR without cause.
2. **Re-run full verification** after every bump:
   ```bash
   docker build -f docker/Dockerfile -t alteia-grid-synth:lab .
   scripts/verify-lab-image.sh
   docker compose -f docker/docker-compose.yml up -d blazegraph
   curl -sf http://localhost:8889/bigdata/status
   ```
3. **GridLAB-D (G-4) is blocking** — `gridlabd --version` must succeed before merging any image change.
4. **Binding pack updates** (`config/gridos-binding-pack.yaml`) are deferred to Story 2.1; do not embed workshop registry URIs in the Docker layer.
5. **Record digest pins** for production CI when Epic 4 workflows land; tag pins above are the Story 1.1 baseline.

## Docker build arguments

| ARG | Default | Purpose |
|-----|---------|---------|
| `CIMHUB_IMAGE` | `gridappsd/cimhub:1.1.0` | Toolchain source (OpenDSS, GridLAB-D, CIMHub JAR) |
| `CIMHUB_RELEASE` | `2024.06.0` | Documented JAR release label |
| `PYTHON_IMAGE` | `python:3.10-bookworm` | Python runtime layer |

Example override:

```bash
docker build -f docker/Dockerfile \
  --build-arg CIMHUB_IMAGE=gridappsd/cimhub:1.1.0 \
  -t alteia-grid-synth:lab .
```
