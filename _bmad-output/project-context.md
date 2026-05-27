---
project_name: ai-workshop
user_name: Bemobrr
date: 2026-05-27
sections_completed:
  - technology_stack
  - language_rules
  - framework_rules
  - testing_rules
  - quality_rules
  - workflow_rules
  - anti_patterns
status: complete
rule_count: 52
optimized_for_llm: true
input_documents:
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/epics.md
  - _bmad-output/planning-artifacts/prds/prd-ai-workshop-2026-05-27/prd.md
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

**Product:** Alteia Synthetic Grid Network Data Generator (`alteia-grid-synth`) for GridOS Tier A CDPSM artifacts.  
**Scope:** P0 + P1 only — no REST API, no Tier B CGMES, no IIDM canonical model, no UX.

---

## Technology Stack & Versions

| Layer | Technology | Notes |
|-------|------------|-------|
| Orchestration | Python 3.10+ | Typer CLI; pySHACL subprocess |
| Canonical hub | Blazegraph + CDPSM/CIM100 RDF | Pattern B — not IIDM (ADR-001) |
| CIM toolchain | CIMHub JAR + Powergrid-Models | Subprocess/JAR wrapper from Python (ADR-002) |
| Graph API | CIMantic Graphs (`cimhub_2023` profile) | FeederModel access for custom checks |
| PF gold | OpenDSS (`export cim100`) | Stable mRIDs via `uuids.dat` |
| PF cross-check | GridLAB-D | Dual PF gate only; pandapower non-blocking (ADR-003) |
| Validation | pySHACL + CIMHub structural tests | GridOS subset SHACL pinned in binding pack |
| Deploy | Docker multi-stage image | Pin CIMHub, Blazegraph, OpenDSS versions (NFR-10) |
| CI | GitHub Actions | PR: ieee13+123; nightly: ieee9500; tag: publish-tier-a |
| Registry | Internal Artifactory | `https://artifactory.gridos.lab/tier-a/datasets/` |
| Package manager | `pyproject.toml` | Repo name: `alteia-grid-synth` |

**Pin versions in Docker image and document upgrade policy.** Do not leave tool versions implicit.

---

## Critical Implementation Rules

### Language-Specific Rules (Python)

- Use **Typer** for CLI; subcommands map 1:1 to pipeline stages (`run`, `validate`, `pack`).
- Invoke CIMHub via **subprocess/JAR wrapper** — do not reimplement CIM import/export in Python.
- Run pySHACL as subprocess; write machine-readable JSON reports on every gate stage (NFR-5).
- **Exit codes:** `0` = success; `1` = validation failure; `2` = infrastructure failure. CI depends on this contract.
- Load tolerances, SHACL path, registry URI from **`gridos-binding-pack.yaml`** — never hard-code as Python constants.
- Use `snake_case` for Python modules and JSON report fields.
- Structured logging for CI; archive JSON validation reports as CI artifacts.

### Framework-Specific Rules (Pipeline / CDPSM)

- **Canonical representation:** RDF in Blazegraph + on-disk combined CDPSM XML — not a custom IIDM model.
- **Pipeline stages (in order):** `export-cim100` → `ingest-blazegraph` → `cimhub-roundtrip` → validation gate → `fabric-packager`.
- **Validation gate DAG (fail-closed, short-circuit on first failure):** T0 connectivity → pySHACL subset → CIMHub structural → dual PF (OpenDSS gold vs GridLAB-D).
- **Pandapower:** Optional sidecar only; results go to `validation/pandapower-info.json`; must **never** set `pf_gate_status: pass`.
- **CIM export:** OpenDSS `export cim100` produces `{feeder}cdpsm.xml` with all six sub-profiles (FUN, EP, TOPO, CAT, GEO, SSH).
- **CIMHub roundtrip:** `-o=both` → `render/opendss/` and `render/gridlabd/` under feeder work path.
- **mRID stability:** Check in `uuids.dat` per feeder; re-export without uuid change must produce identical mRID set.
- **Binding pack** is the runtime join between code and workshop decisions — load at runtime, not compile time.

### Testing Rules

- Map integration tests to acceptance tests: **AT-13**, **AT-123**, **AT-8500**, **AT-9500** (see PRD §11).
- Unit tests under `tests/unit/`; integration tests under `tests/integration/` mapped to AT-* criteria.
- IEEE 13 is the P0 spine — all gate tests must pass on 13 before scaling to other feeders.
- PF tolerances (from binding pack): vm ≤ 0.1%, angle ≤ 0.01°, source kW/kvar ≤ 0.5%.
- IEEE 9500 requires **six sample PF points** in `pf-diff-report.json` (AT-9500-2).
- Packager must refuse **stale reports** from a different run id/timestamp.
- CI PR budget: combined `validate-ieee13` + `validate-ieee123` **< 10 minutes** (NFR-7).
- Document 8500/9500 memory/time bounds in `docs/ci-bounds.md` before AT-8500-3 sign-off (G-1).

### Code Quality & Style Rules

**Naming conventions (mandatory):**

| Artifact | Pattern | Example |
|----------|---------|---------|
| Dataset ID | `ieee{nodes}-asbuilt` lowercase | `ieee9500-asbuilt` |
| Feeder CLI arg | short ieee id | `ieee13`, `ieee123` |
| Python modules | `snake_case` | `validation_gate/pf_diff.py` |
| JSON report fields | `snake_case` | `pf_max_vm_delta_pct` |
| CIM files | `{feeder}cdpsm.xml` | `ieee13cdpsm.xml` |
| CI jobs | `validate-ieee{feed}` | `validate-ieee13` |

**Repo layout (follow architecture):**

```
alteia-grid-synth/
├── config/gridos-binding-pack.yaml
├── shacl/gridos-cdpsm-subset.ttl
├── feeders/{ieee13,ieee123,ieee8500,ieee9500}/
├── src/alteia_grid_synth/{cli,pipeline,validation_gate,registry}/
├── docker/{Dockerfile,docker-compose.yml}
├── tests/{unit,integration}/
├── .github/workflows/{validate-pr,validate-nightly,publish-tier-a}.yml
└── docs/{ci-bounds,fabric-smoke-procedure}.md
```

**Report schemas (minimum fields):**

- `pf-diff-report.json`: `feeder`, `pf_gate`, `status`, `metrics` (vm/angle/source deltas), `samples[]`
- `shacl-report.json`: `status`, `violation_count`, `violations[]` with `path`, `message`, `focus_node`

### Development Workflow Rules

- **No web/API starter** — this is a container-first data pipeline repo.
- PR to `main` triggers `validate-ieee13` and `validate-ieee123`; failed gates block merge.
- Nightly on `main`: `validate-ieee9500` (and `validate-ieee8500` nightly or manual).
- **Publish trigger:** git tag `vMAJOR.MINOR.PATCH` on `main` → `publish-tier-a`.
- `manifest.git_tag` must match tag name; `manifest.version` = tag without `v` prefix (P-D7).
- Publish uses `svc-alteia-synth-gen-ci` credentials; human read via `gridos-lab-artifacts-ro`.
- **Immutability:** re-publish same semver with different checksum must fail (FR-23).
- **Dev publish vs P1:** T0+T1+SHACL pass is sufficient for dev-registry publish; ADMS smoke is **not** wired into CI (P-D8).
- Large feeder seeds (8500/9500): use Git LFS if needed.
- Binding pack version bump required when subset or mRID rules change; triggers platform re-approval.

### Critical Don't-Miss Rules

**NEVER do these in P0–P1 stories:**

- Add REST API, Tier B CGMES export, custom IIDM canonical model, or parameterized synthesis.
- Hard-code workshop class allow-lists, approver names, or registry URLs in application logic — load from external artifacts.
- Bypass validation gate for any publish path.
- Use pandapower as a blocking PF gate for NA unbalanced feeders.
- Set `validation_tiers` beyond `["T0", "T1"]` or `tier` beyond `"A"`.
- Include real utility IDs, customer data, or re-identifiable AMI patterns (NFR-3).
- Invent ADMS smoke script IDs — reference ADMS QA-owned placeholders (G-2).
- Duplicate normative contracts from PRD §10 in code comments — implement against binding pack + manifest schema.

**Workshop-gated integration points (load as data, not code literals):**

| OQ | Source | Integration |
|----|--------|-------------|
| OQ-2 | `p0-workshop-outcomes-2026-05-27.md` §2 | SHACL + optional SPARQL allow-list |
| OQ-3 | P0 approval record | Block first P1 fabric-lab promotion until present |
| OQ-4 | ADMS smoke criteria doc | P1 closure only; not dev publish |
| OQ-5 | Binding pack `artifact_registry` | Publish client reads URI + ACLs |

**Fabric ZIP layout v0 (§10.2) — required paths:**

```
{dataset_id}-v{semver}/
  manifest.json
  cim/{feeder}cdpsm.xml
  validation/shacl-report.json
  validation/pf-diff-report.json
  render/opendss/
  render/gridlabd/
  render/cgmes/          # empty or omitted in v1
```

**Manifest minimum fields:** `dataset_id`, `version`, `tier`, `binding_pack_version`, `cdpsm_edition`, `platform_release`, `validation_tiers`, `feeders`, `validation`, `artifacts`, `published_at`, `git_tag`.

**External/lab execution (document only — not CI jobs):** FR-19 fabric smoke ingest, FR-21 ADMS smoke execution. Deliver procedures in `docs/`; execution is GridOS lab responsibility.

**Normative references for implementers:**

- PRD §10: binding pack, fabric ZIP, manifest, registry contracts
- Architecture: module mapping, pipeline stages, enforcement rules
- Epics: story acceptance criteria and FR traceability

---

## Usage Guidelines

**For AI Agents:**

- Read this file before implementing any code in `alteia-grid-synth`.
- Follow ALL rules exactly as documented.
- When in doubt, prefer the more restrictive option (fail-closed).
- Implement stories in architecture implementation sequence (Docker → IEEE 13 spine → gate → packager → CLI → CI → scale-up → registry).
- Update this file if new patterns emerge during implementation.

**For Humans:**

- Keep this file lean and focused on unobvious agent needs.
- Update when technology stack, binding pack schema, or PRD §10 contracts change.
- Review quarterly; remove rules that become obvious once codebase exists.
- Pin CI bounds (G-1) and GridLAB-D in Docker (G-4) before large-feeder stories.

Last Updated: 2026-05-27
