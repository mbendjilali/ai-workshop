---
baseline_commit: 0313f07d6f0e8cfff7a016dc72fb491fcd37fa89
---

# Story 1.1: Initialize Pipeline Repo and Docker Lab Image

Status: review

<!-- Ultimate context engine analysis completed - comprehensive developer guide created -->

## Story

As an **Alteia engineer (Sam)**,
I want a containerized lab image with pinned OpenDSS, CIMHub, Blazegraph, GridLAB-D, and Python toolchain,
so that the CDPSM hub pipeline runs reproducibly in CI and local dev.

## Acceptance Criteria

1. **Given** the architecture §Structure Patterns repo layout for `alteia-grid-synth`  
   **When** I inspect the repository root  
   **Then** `pyproject.toml`, `README.md`, `src/alteia_grid_synth/`, `docker/`, and `tests/` exist with the package importable as `alteia_grid_synth`  
   **And** Python is **3.10+** with **Typer** declared as a dependency  
   **And** `grid-synth` console script entry point resolves to a Typer stub CLI (`run`, `validate`, `pack` subcommands registered but not implemented beyond `--help`)

2. **Given** `docker/Dockerfile`  
   **When** I run `docker build -f docker/Dockerfile -t alteia-grid-synth:lab .`  
   **Then** the image builds successfully  
   **And** the following tools are on `PATH` inside the container with **pinned versions documented** per NFR-10 in `docs/docker-tool-versions.md` (or equivalent README section):
   - OpenDSS (`opendsscmd` or documented invoke)
   - CIMHub JAR (or CIMHub-compatible Java exporter)
   - Java 11+ runtime for CIMHub
   - Python 3.10+ with project deps installed

3. **Given** `docker-compose.yml`  
   **When** I run `docker compose -f docker/docker-compose.yml up -d blazegraph`  
   **Then** Blazegraph starts and responds on the documented SPARQL endpoint (default: `http://localhost:8889/bigdata/sparql`)  
   **And** compose documents how the lab image connects to Blazegraph for local integration runs (NFR-6)

4. **Given** the built lab image  
   **When** I run the documented verification commands (see Tasks)  
   **Then** each pinned tool reports its version or health  
   **And** **GridLAB-D is installed and verifiable** — e.g. `gridlabd --version` succeeds or documented equivalent invoke (readiness **G-4 / Q-3**; blocks FR-8 / Story 2.4 if missing)  
   **And** verification output is reproducible from README instructions

5. **Given** this story scope boundary  
   **When** the scaffold is complete  
   **Then** **no** pipeline stage logic, **no** `config/gridos-binding-pack.yaml`, **no** `shacl/*`, **no** `feeders/*` seeds, and **no** `.github/workflows/*` exist yet  
   **And** **no** workshop URLs, approver names, or registry URIs are hard-coded in application logic (binding pack is runtime config per project-context)

6. **Given** `README.md`  
   **When** a new engineer follows build/run instructions  
   **Then** they can build the lab image, start Blazegraph via compose, run tool verification, and invoke `grid-synth --help` inside the container  
   **And** upgrade policy for pinned tool versions is documented (when to bump, what to re-verify)

**Traces:** Architecture seq. 1; NFR-6, NFR-10; readiness G-4/Q-3

## Tasks / Subtasks

- [x] **Scaffold greenfield repo layout** (AC: 1, 5)
  - [x] Create `pyproject.toml`: project name `alteia-grid-synth`, Python `>=3.10`, build backend (hatchling or setuptools), `[project.scripts] grid-synth = "alteia_grid_synth.cli:app"`
  - [x] Create package skeleton:
    ```
    src/alteia_grid_synth/
      __init__.py          # __version__
      cli.py               # Typer app; subcommands run/validate/pack as stubs
    tests/
      unit/
      integration/
    ```
  - [x] Add `.gitignore` (Python, Docker, `work/`, `dist/`, `.venv`)
  - [x] **Do not** create `config/`, `shacl/`, `feeders/`, `pipeline/`, `validation_gate/`, `.github/workflows/` yet

- [x] **Implement Typer CLI stub** (AC: 1)
  - [x] `cli.py`: `@app.command()` for `run`, `validate`, `pack` — each prints "not implemented" or raises `typer.Exit(code=2)` with clear message
  - [x] Root callback sets up `--version` from package `__version__`
  - [x] Use `snake_case` modules; no hard-coded workshop/registry constants

- [x] **Docker lab image** (AC: 2, 4)
  - [x] `docker/Dockerfile`: multi-stage recommended — base with Java 11+, tool layer (OpenDSS, GridLAB-D, CIMHub JAR), Python layer with editable install
  - [x] Pin versions via build args or env vars; record resolved pins in `docs/docker-tool-versions.md`
  - [x] **GridLAB-D (G-4):** MUST install in image — prefer patterns from [CIMHub Docker](https://github.com/GRIDAPPSD/CIMHub) (`gridappsd/cimhub:1.1.0` bundles GridLAB-D) or equivalent source build; verify with `gridlabd --version`
  - [x] OpenDSS: `opendsscmd` Linux build or CIMHub-bundled binary
  - [x] CIMHub: JAR from [CIMHub Releases](https://github.com/GRIDAPPSD/CIMHub/releases) (e.g. tag `2024.06.0` or latest stable at build time — **pin and document**)
  - [x] Java 11+ (OpenJDK) for CIMHub subprocess invocations (future stories)

- [x] **docker-compose for local Blazegraph** (AC: 3)
  - [x] Service `blazegraph`: image pinned (e.g. `lyrasis/blazegraph:2.1.5` or `gridappsd/blazegraph:v2024.06.0` — document choice)
  - [x] Port map `8889:8080` (GridAPPS-D convention)
  - [x] Optional `lab` service building from `Dockerfile` with `depends_on: blazegraph` for integrated dev shell
  - [x] Healthcheck: HTTP GET to Blazegraph endpoint or documented curl SPARQL ping

- [x] **Version documentation (NFR-10)** (AC: 2, 6)
  - [x] Create `docs/docker-tool-versions.md` table: Component | Pinned version/tag | Source/URL | Verification command
  - [x] Document upgrade policy: bump one component at a time; re-run full verification; update binding pack only in Story 2.1

- [x] **README build/run guide** (AC: 6)
  - [x] Prerequisites: Docker, Docker Compose, git
  - [x] Build: `docker build -f docker/Dockerfile -t alteia-grid-synth:lab .`
  - [x] Start Blazegraph: `docker compose -f docker/docker-compose.yml up -d blazegraph`
  - [x] Verify tools (document exact commands):
    ```bash
    docker run --rm alteia-grid-synth:lab opendsscmd -h    # or version flag
    docker run --rm alteia-grid-synth:lab java -version
    docker run --rm alteia-grid-synth:lab gridlabd --version   # G-4 REQUIRED
    docker run --rm alteia-grid-synth:lab grid-synth --help
    docker run --rm alteia-grid-synth:lab python -c "import alteia_grid_synth; print(alteia_grid_synth.__version__)"
    ```
  - [x] Link to `docs/docker-tool-versions.md` and architecture Structure Patterns

- [x] **Smoke test (manual or script)** (AC: 4)
  - [x] Add `scripts/verify-lab-image.sh` (optional but recommended) that runs all verification commands and exits non-zero on failure
  - [ ] Confirm GridLAB-D verification passes before marking story done *(blocked: no Docker runtime on dev host — run `./scripts/verify-lab-image.sh` after build)*

## Dev Notes

### Epic Context (Epic 1 — IEEE 13 CDPSM Hub Pipeline)

Epic 1 delivers the IEEE 13 spine: export → Blazegraph → CIMHub roundtrip → PF agreement. **Story 1.1 is the foundation** — no feeder data or pipeline logic yet.

| Story | Scope | Depends on 1.1 |
|-------|-------|----------------|
| **1.1** (this) | Repo + Docker lab image | — |
| 1.2 | IEEE 13 OpenDSS seed + `uuids.dat` | Lab image |
| 1.3 | `export-cim100` stage | 1.2 |
| 1.4 | Blazegraph ingest | 1.3, compose Blazegraph |
| 1.5 | CIMHub roundtrip | 1.4 |
| 1.6 | PF vs OpenDSS gold | 1.5 |

### Scope Boundaries — DO NOT Implement

| Deferred item | Target story | Reason |
|---------------|--------------|--------|
| `feeders/ieee13/*` | 1.2 | Seed check-in separate |
| `config/gridos-binding-pack.yaml` | 2.1 | Runtime config; workshop values as data |
| `shacl/gridos-cdpsm-subset.ttl` | 2.1 / 2.3 | SHACL gate not yet |
| Pipeline stages (`export_cim100`, etc.) | 1.3–1.6 | Epic 1 sequence |
| Validation gate modules | Epic 2 | After hub pipeline |
| `.github/workflows/*` | Epic 4 | CI after CLI exists |
| Hard-coded registry URLs / approver names | Never | project-context anti-pattern |

### Architecture Compliance

**Repo root = pipeline repo** (`alteia-grid-synth`). In this workshop workspace, scaffold at project root using architecture §Structure Patterns. Final layout after 1.1 (minimal):

```
alteia-grid-synth/                    # repo root (ai-workshop workspace)
├── README.md
├── pyproject.toml
├── docs/
│   └── docker-tool-versions.md       # NEW in 1.1
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── src/alteia_grid_synth/
│   ├── __init__.py
│   └── cli.py                        # Typer stub only
└── tests/
    ├── unit/
    └── integration/
```

Full target layout (for orientation — **not** all created in 1.1):

```
├── config/gridos-binding-pack.yaml   # Story 2.1
├── shacl/gridos-cdpsm-subset.ttl     # Story 2.1
├── feeders/{ieee13,...}/             # Story 1.2+
├── src/alteia_grid_synth/{pipeline,validation_gate,registry}/  # Later epics
├── .github/workflows/                # Epic 4
└── docs/{ci-bounds,fabric-smoke-procedure}.md  # Later stories
```

**ADR alignment (scaffold only — no logic yet):**
- **ADR-001:** CDPSM hub — prepare toolchain, not IIDM
- **ADR-002:** CIMHub via subprocess/JAR — install JAR in Docker now; wrapper in later stories
- **ADR-003:** GridLAB-D in image now (G-4) — required for future dual PF gate

**Exit codes (establish in CLI stub docstring; enforce in Story 3.3):** `0` success, `1` validation fail, `2` infra fail.

### Technical Requirements

| Requirement | Implementation guidance |
|-------------|-------------------------|
| Python 3.10+ | `requires-python = ">=3.10"` in pyproject |
| Typer CLI | `[project.dependencies] typer>=0.9` (pin minor in pyproject) |
| NFR-10 pins | Document in `docs/docker-tool-versions.md`; use Docker `ARG` for tags |
| NFR-6 Docker | Image runnable in GitHub Actions / K8s Job (single entrypoint, no GUI) |
| G-4 GridLAB-D | **Blocking AC** — must pass `gridlabd --version` or documented equivalent |
| No secrets | No `.env` with credentials; no registry tokens in repo |

**Suggested pin starting points (verify at build time; document actual resolved versions):**

| Component | Suggested pin | Notes |
|-----------|---------------|-------|
| CIMHub | JAR from release `2024.06.0` or `gridappsd/cimhub:1.1.0` base | Includes OpenDSSCmd + GridLAB-D |
| Blazegraph | `lyrasis/blazegraph:2.1.5` or `gridappsd/blazegraph:v2024.06.0` | SPARQL at `:8889` |
| OpenDSS | Bundled with CIMHub / `opendsscmd` | Linux build for container |
| GridLAB-D | Bundled with CIMHub image or distro package | **G-4 — verify explicitly** |
| Java | OpenJDK 11 | CIMHub requirement |
| Python deps | `typer`, future: `pyshacl`, `cim-graph` | Only `typer` in 1.1 |

**Docker strategy options (pick one; document choice in README):**

1. **Extend `gridappsd/cimhub:1.1.0`** — fastest path; inherits OpenDSS, GridLAB-D, Java, Blazegraph client libs; add Python 3.10+ layer and project install.
2. **Multi-stage from scratch** — more control over pins; higher maintenance; must still satisfy G-4 GridLAB-D install.

Prefer option 1 unless org policy requires fully custom base.

**Blazegraph compose pattern (from GridAPPS-D docs):**
```bash
docker run --name blazegraph -d -p 8889:8080 lyrasis/blazegraph:2.1.5
# SPARQL endpoint: http://localhost:8889/bigdata/sparql
```

### Library & Framework Requirements

**pyproject.toml minimum:**
```toml
[project]
name = "alteia-grid-synth"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["typer>=0.9.0"]

[project.scripts]
grid-synth = "alteia_grid_synth.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/alteia_grid_synth"]
```

Adjust build config to match chosen backend; ensure `pip install -e .` works inside Docker.

**cli.py stub pattern:**
```python
import typer
app = typer.Typer(name="grid-synth", help="Alteia Synthetic Grid Network Data Generator")

@app.command()
def run(...):
    typer.echo("Not implemented — see Story 3.3", err=True)
    raise typer.Exit(code=2)

# validate, pack similarly
```

### Testing Requirements

**Story 1.1 testing is verification-focused, not pipeline AT-*:**

| Check | Type | Pass criteria |
|-------|------|---------------|
| Package import | Manual / optional unit test | `import alteia_grid_synth` succeeds |
| CLI help | Manual | `grid-synth --help` lists run/validate/pack |
| Docker build | Manual | `docker build` exits 0 |
| Blazegraph up | Manual | compose healthcheck or curl SPARQL |
| Tool pins | Manual | `docs/docker-tool-versions.md` matches `docker run ... version` output |
| **GridLAB-D G-4** | **Manual — blocking** | `gridlabd --version` succeeds in lab image |

Optional: `tests/unit/test_cli_stub.py` asserting `--help` exit 0. No integration tests against feeders yet.

### Project Context Reference

From `_bmad-output/project-context.md` — **mandatory agent rules for this story:**

- Package manager: `pyproject.toml`; repo name `alteia-grid-synth`
- Typer CLI; subcommands map 1:1 to pipeline stages (stub now, implement later)
- Pin versions in Docker + document upgrade policy (NFR-10)
- **Never** hard-code workshop URLs/names/registry in code
- No web/API starter — container-first pipeline repo
- GridLAB-D in Docker (G-4) before large-feeder / dual-PF stories
- Implementation sequence starts with Docker image (architecture seq. 1)

### Previous Story Intelligence

None — first story in Epic 1. No prior implementation artifacts or git history in `alteia-grid-synth`.

### Latest Technical Information

- **CIMHub Docker** (`gridappsd/cimhub:1.1.0`) bundles Blazegraph client tooling, OpenDSSCmd, **GridLAB-D**, Java 11, Python — recommended reference for G-4 resolution ([CIMHub README](https://github.com/GRIDAPPSD/CIMHub)).
- CIMHub releases tagged e.g. `2024.06.0` (July 2024) — pin JAR or image digest, not floating `latest`.
- Blazegraph 2.1.x series used by GridAPPS-D; compose port **8889:8080** is the de facto lab standard.
- OpenDSS CIM100 export is the gold path for CDPSM (FR-4, future stories) — ensure `opendsscmd` in image supports `export cim100`.
- Python 3.10+ required for future `cim-graph` / CIMantic Graphs compatibility.

### Readiness Pre-Flight (G-4 / Q-3)

Implementation readiness report flags **G-4: GridLAB-D availability in Docker** as **High** priority before Story 2.4 (dual PF gate, FR-8). This story **must close G-4** with a verifiable install — not merely "tracked as blocker."

**Definition of done for G-4:** Lab image verification script includes GridLAB-D check; README documents command; Story 2.4 can assume `gridlabd` on PATH.

**Q-3 (readiness question)** maps to G-4 resolution in Story 1.1 — distinct from workshop **OQ-3** (P0 sign-off record), which is wired in Story 2.1.

### Project Structure Notes

- Workshop workspace `ai-workshop` holds BMAD planning artifacts under `_bmad-output/`; **application code lives at repo root** per architecture, not inside `_bmad-output/`.
- Do not commit large binaries without LFS policy — CIMHub JAR may be downloaded at Docker build time via `ARG`/URL rather than vendored in git (document approach).
- `work/` and `dist/` are runtime outputs — gitignore them.

### References

- [Source: _bmad-output/planning-artifacts/epics.md § Epic 1 Story 1.1]
- [Source: _bmad-output/planning-artifacts/architecture.md § Starter Template Evaluation, § Structure Patterns, § Implementation Sequence step 1, G-4]
- [Source: _bmad-output/planning-artifacts/prds/prd-ai-workshop-2026-05-27/prd.md § NFR-6, NFR-10]
- [Source: _bmad-output/project-context.md § Technology Stack, § Critical Don't-Miss Rules]
- [Source: _bmad-output/planning-artifacts/implementation-readiness-report-2026-05-27.md § G-4/Q-3, Recommended next steps]
- [Source: _bmad-output/planning-artifacts/research/technical-synthetic-electrical-grid-network-data-generator-gridos-cim-cdpsm-research-2026-05-27.md § 7.4 Cloud/deployment]
- [External: GRIDAPPSD/CIMHub](https://github.com/GRIDAPPSD/CIMHub) — Docker, JAR, GridLAB-D bundling
- [External: OpenDSS CIM100](https://opendss.epri.com/CommonInformationModelCIM100.html)

## Dev Agent Record

### Agent Model Used

Composer (Cursor agent)

### Debug Log References

- Docker/Podman not installed on dev host (`docker: command not found`); `sudo apt install docker.io` requires interactive password.
- Local verification: `pip install -e ".[dev]"` + `pytest tests/unit/` passed (2/2).
- Docker image build and `gridlabd --version` in-container checks deferred to host with Docker — Dockerfile uses multi-stage copy from `gridappsd/cimhub:1.1.0` per G-4 strategy.

### Completion Notes List

- Scaffolded `alteia-grid-synth` at repo root: `pyproject.toml`, `src/alteia_grid_synth/`, `tests/{unit,integration}/`, `.gitignore`.
- Typer CLI stub with `run`, `validate`, `pack` (exit 2 + message) and `--version`; no hard-coded workshop/registry constants.
- Multi-stage `docker/Dockerfile`: copies OpenDSS, GridLAB-D, CIMHub JAR from `gridappsd/cimhub:1.1.0` into `python:3.10-bookworm` + editable install.
- `docker/docker-compose.yml`: `lyrasis/blazegraph:2.1.5` on `8889:8080`, healthcheck, optional `lab` service with `BLAZEGRAPH_SPARQL_URL`.
- `docs/docker-tool-versions.md` pin table + upgrade policy (NFR-10).
- `scripts/verify-lab-image.sh` for post-build toolchain checks including G-4 GridLAB-D.
- Scope boundary respected: no `feeders/`, `config/`, `shacl/`, pipeline, validation_gate, or CI workflows.

### File List

- `.gitignore`
- `.dockerignore`
- `README.md`
- `pyproject.toml`
- `docs/docker-tool-versions.md`
- `docker/Dockerfile`
- `docker/docker-compose.yml`
- `scripts/verify-lab-image.sh`
- `src/alteia_grid_synth/__init__.py`
- `src/alteia_grid_synth/cli.py`
- `tests/unit/.gitkeep`
- `tests/unit/test_cli_stub.py`
- `tests/integration/.gitkeep`

### Change Log

- 2026-05-27: Story 1.1 — initialize pipeline repo, Typer CLI stub, Docker lab image (CIMHub 1.1.0 base), Blazegraph compose, tool version docs, verify script.
