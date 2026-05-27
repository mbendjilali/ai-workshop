---
stepsCompleted: [1, 2, 3, 4]
workflowType: epics-and-stories
status: complete
completedAt: 2026-05-27
scope: P0 + P1
fastPath: true
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-ai-workshop-2026-05-27/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/prds/prd-ai-workshop-2026-05-27/p0-workshop-outcomes-2026-05-27.md
implementationSequence: architecture.md §Implementation Sequence
---

# ai-workshop — Epic Breakdown

## Overview

This document decomposes **P0 + P1** requirements for the Alteia Synthetic Grid Network Data Generator into implementable epics and stories. Stories follow the architecture **Implementation Sequence** (§Completion) and trace to **FR-1–FR-24**, **NFR-1–NFR-10**, and per-feeder acceptance tests **AT-13**, **AT-123**, **AT-8500**, **AT-9500**.

**Fast path:** Single-pass generation from provided PRD, architecture, and P0 workshop outcomes (no step-by-step A/P/C gates).

**External/lab boundary:** FR-19–FR-21 fabric ingest and ADMS smoke **execution** are manual P1 gates tracked outside CI; dev-registry publish requires T0/T1+SHACL only (P-D8).

---

## Requirements Inventory

### Functional Requirements

FR-1: Facilitate P0 workshop producing fabric CDPSM ingest spec (profiles, spatial containers, mRID rules, smoke ingest procedure) with Elena Vasquez P0 sign-off.
FR-2: Publish binding pack v0 (YAML) co-versioned with latest GridOS platform release; every Tier A manifest references `binding_pack_version`.
FR-3: Co-develop GridOS CDPSM subset SHACL; pin bundle in binding pack; pySHACL pass required before promotion.
FR-4: Ingest IEEE 13 OpenDSS feeder and emit combined CDPSM XML via `export cim100` with stable `uuids.dat` mRIDs.
FR-5: Load CDPSM to Blazegraph and run CIMHub `CIMImporter` roundtrip to OpenDSS and GridLAB-D render directories.
FR-6: Compare CIMHub roundtrip PF against OpenDSS gold with max ΔV ≤ 0.1%; CI `validate-ieee13` fails on exceedance.
FR-7: Enforce T0 connectivity validation (terminals, ConnectivityNodes, feeder scope, dangling terminals); failures block promotion.
FR-8: Enforce dual PF gate (OpenDSS gold vs GridLAB-D roundtrip) with vm ≤ 0.1%, angle ≤ 0.01°, source kW/kvar ≤ 0.5%; pandapower non-blocking.
FR-9: Run pySHACL against GridOS subset SHACL bundle before promotion; zero violations required.
FR-10: Emit `.tar.gz` fabric ZIP matching §10.2 layout (manifest, cim, validation reports, render mirrors).
FR-11: Emit `manifest.json` conforming to §10.3 minimum fields including gate status and git_tag.
FR-12: Declare `validation_tiers: ["T0", "T1"]` on published datasets; no T2+ in v1.
FR-13: Provide Typer CLI executing export → validate → pack for a named IEEE feeder with non-zero exit on validation failure.
FR-14: CI runs `validate-ieee13` and `validate-ieee123` on every PR completing combined in < 10 minutes.
FR-15: CI runs `validate-ieee9500` nightly and `publish-tier-a` on git tag to internal registry.
FR-16: Promote IEEE 123 through full gate and emit Tier A fabric ZIP; SSH switch state for trace smoke.
FR-17: Promote IEEE 8500 through full gate within CI memory/time budget; regulators/caps PF pass.
FR-18: Promote IEEE 9500 through full gate including six-point PF validation pattern.
FR-19: GridOS platform ingests Tier A ZIP for all four IEEE feeders via file-based upload without manual CIM repair (4/4 P1 metric).
FR-20: Document ADMS smoke criteria (trace paths, PF buses, tolerances) co-authored in P0 and frozen before P1 execution.
FR-21: ADMS QA executes smoke tests on all four promoted bundles; 4/4 pass required for P1 sign-off (Marcus Chen); not required for dev-registry publish.
FR-22: Publish promoted Tier A artifacts to `https://artifactory.gridos.lab/tier-a/datasets/` on git tag with semver + manifest correlation.
FR-23: Published artifact versions are immutable; same semver with different checksum rejected.
FR-24: Every Tier A artifact includes independent OpenDSS/GridLAB-D render mirrors with manifest checksums.

### NonFunctional Requirements

NFR-1: All Tier A artifacts conform to IEC 61968-13:2021 CDPSM and CIM100 namespace from binding pack.
NFR-2: mRIDs remain stable across pipeline re-runs when `uuids.dat` unchanged; uuid maps checked into source control per feeder.
NFR-3: Synthetic datasets contain no real utility IDs, customer data, or re-identifiable AMI patterns.
NFR-4: Binding pack refreshed and compatibility documented when GridOS platform ships new release.
NFR-5: CI jobs emit structured logs and machine-readable JSON validation reports for every gate stage.
NFR-6: CLI and batch run in Docker lab image compatible with GitHub Actions and Kubernetes Job execution.
NFR-7: PR-path validation (IEEE 13 + 123) completes in < 10 minutes on standard CI runners.
NFR-8: 8500/9500 PF and packager jobs complete within documented memory and nightly time budgets without OOM.
NFR-9: Artifacts stored in internal registry only; no public CDN or external partner access in v1.
NFR-10: CIMHub, Blazegraph, and OpenDSS versions pinned in Docker image with documented upgrade policy.

### Additional Requirements

- **Starter:** No web/API starter — initialize `alteia-grid-synth` Python pipeline repo with Docker composition and GitHub Actions (architecture §Starter Template Evaluation).
- **ADR-001:** CDPSM hub only — no custom IIDM canonical model in P0–P1.
- **ADR-002:** Adopt CIMHub + Powergrid-Models; invoke CIMHub via subprocess/JAR wrapper from Python CLI.
- **ADR-003:** Dual PF = OpenDSS + GridLAB-D only; optional pandapower sidecar is informational (`validation/pandapower-info.json`).
- **Fail-closed promotion:** Any gate failure → exit code 1, no ZIP publish; exit codes 0/1/2 (success / validation fail / infra fail).
- **Binding pack as runtime join:** Tolerances, SHACL path, registry URI loaded from `gridos-binding-pack.yaml` — not hard-coded constants.
- **Workshop artifacts as data:** Class allow-list, approver records, registry ACLs loaded from external artifacts (`p0-workshop-outcomes-2026-05-27.md`, ingest spec reference) — not compiled literals.
- **P0 gate record:** Pipeline refuses first P1 fabric-lab promotion until P0 approval record present (OQ-3).
- **Git tag → semver:** Tag `vMAJOR.MINOR.PATCH`; `manifest.git_tag` matches tag; `manifest.version` is tag without `v` prefix (P-D7).
- **CI bounds gap G-1:** Pin numeric 8500/9500 memory/time bounds in `docs/ci-bounds.md` before AT-8500-3 sign-off.
- **GridLAB-D in Docker:** Resolve G-4 — GridLAB-D availability in lab image required for dual PF gate.
- **Large feeder seeds:** Git LFS for 8500/9500 OpenDSS seeds if needed.
- **Report schemas:** `pf-diff-report.json` and `shacl-report.json` minimum fields per architecture §Format Patterns.
- **Naming conventions:** Dataset IDs `ieee{nodes}-asbuilt`; CIM files `{feeder}cdpsm.xml`; CI jobs `validate-ieee{feed}`.

### UX Design Requirements

N/A — v1 is a container-first data/ETL pipeline with CLI only; no UX Design document.

### FR Coverage Map

| FR | Epic | Story |
|----|------|-------|
| FR-1 | Epic 2 | 2.1 |
| FR-2 | Epic 2 | 2.1 |
| FR-3 | Epic 2 | 2.3 |
| FR-4 | Epic 1 | 1.3 |
| FR-5 | Epic 1 | 1.4, 1.5 |
| FR-6 | Epic 1 | 1.6 |
| FR-7 | Epic 2 | 2.2 |
| FR-8 | Epic 2 | 2.4 |
| FR-9 | Epic 2 | 2.3 |
| FR-10 | Epic 3 | 3.1 |
| FR-11 | Epic 3 | 3.2 |
| FR-12 | Epic 3 | 3.2 |
| FR-13 | Epic 3 | 3.3 |
| FR-14 | Epic 4 | 4.1, 4.3 |
| FR-15 | Epic 5, Epic 6 | 5.4, 6.1 |
| FR-16 | Epic 4 | 4.2 |
| FR-17 | Epic 5 | 5.2 |
| FR-18 | Epic 5 | 5.3 |
| FR-19 | Epic 7 | 7.1 |
| FR-20 | Epic 7 | 7.2 |
| FR-21 | Epic 7 | 7.3 |
| FR-22 | Epic 6 | 6.1 |
| FR-23 | Epic 6 | 6.2 |
| FR-24 | Epic 3, Epic 6 | 3.1, 6.3 |

---

## Epic List

### Epic 1: IEEE 13 CDPSM Hub Pipeline
Sam (Alteia engineer) can export IEEE 13 from OpenDSS to CDPSM, roundtrip through CIMHub/Blazegraph, and verify PF agreement against OpenDSS gold.
**FRs covered:** FR-4, FR-5, FR-6 | **AT:** AT-13-1, AT-13-2

### Epic 2: Binding Pack Integration & Validation Gate
Sam can gate promotion using binding-pack-driven T0 connectivity, pySHACL subset conformance, and dual PF (OpenDSS vs GridLAB-D) with fail-closed JSON reports.
**FRs covered:** FR-1, FR-2, FR-3, FR-7, FR-8, FR-9 | **AT:** AT-13-3, AT-13-4

### Epic 3: Tier A Fabric ZIP Packager & CLI
Sam can produce a §10.2-compliant Tier A `.tar.gz` with manifest, validation reports, and render mirrors via `grid-synth` CLI.
**FRs covered:** FR-10, FR-11, FR-12, FR-13, FR-24 (packaging) | **AT:** AT-13-5

### Epic 4: PR CI Path — IEEE 13 + 123
Sam gets automated PR feedback: IEEE 13 and 123 pass full pipeline within the 10-minute CI budget.
**FRs covered:** FR-14, FR-16 | **AT:** AT-13-7, AT-123-1, AT-123-2, AT-123-5

### Epic 5: Nightly Large-Feeder Validation (8500 / 9500)
Sam gets nightly validation on IEEE 8500 and 9500 including regulator PF and six-point 9500 pattern within documented CI bounds.
**FRs covered:** FR-15, FR-17, FR-18 | **AT:** AT-8500-1, AT-8500-2, AT-8500-3, AT-9500-1, AT-9500-2, AT-9500-3, AT-9500-6

### Epic 6: Tier A Registry Publication
Sam can publish immutable, checksum-verified Tier A artifacts to the internal registry on git tag with bundled render mirrors.
**FRs covered:** FR-15, FR-22, FR-23, FR-24 | **NFR:** NFR-9

### Epic 7: External Lab Gates — Fabric & ADMS Smoke (P1 Sign-off)
GridOS platform and ADMS QA execute fabric ingest and ADMS smoke on promoted artifacts; Alteia delivers procedures, criteria linkage, and gate templates — **not CI-blocked dev publish**.
**FRs covered:** FR-19, FR-20, FR-21 | **AT:** AT-13-6, AT-123-3, AT-123-4, AT-8500-4, AT-8500-5, AT-9500-4, AT-9500-5

---

## Epic 1: IEEE 13 CDPSM Hub Pipeline

Sam can export IEEE 13 from OpenDSS to CDPSM, roundtrip through CIMHub/Blazegraph, and verify PF agreement against OpenDSS gold.

### Story 1.1: Initialize Pipeline Repo and Docker Lab Image

As an **Alteia engineer (Sam)**,
I want a containerized lab image with pinned OpenDSS, CIMHub, Blazegraph, and Python toolchain,
So that the CDPSM hub pipeline runs reproducibly in CI and local dev.

**Acceptance Criteria:**

**Given** the architecture repo layout for `alteia-grid-synth`
**When** I build the Docker lab image from `docker/Dockerfile`
**Then** OpenDSS, CIMHub JAR, Blazegraph, and Python 3.10+ with Typer are available in the container
**And** tool versions are pinned and documented per NFR-10
**And** `docker-compose.yml` starts Blazegraph for local integration runs
**And** GridLAB-D availability is verified or tracked as G-4 blocker before dual PF stories

**Traces:** Architecture seq. 1; NFR-6, NFR-10

---

### Story 1.2: Check In IEEE 13 OpenDSS Seed with Stable UUID Map

As an **Alteia engineer (Sam)**,
I want the IEEE 13 OpenDSS master and `uuids.dat` in source control,
So that mRIDs remain stable across pipeline re-runs and CI can detect drift.

**Acceptance Criteria:**

**Given** `feeders/ieee13/Master.dss` and `feeders/ieee13/uuids.dat`
**When** I re-run export without changing `uuids.dat`
**Then** the extracted mRID set is identical to the prior run
**And** no real utility identifiers appear in seed files per NFR-3
**And** dataset naming follows `ieee13` CLI arg convention

**Traces:** FR-4 (precondition); NFR-2, NFR-3

---

### Story 1.3: Implement export-cim100 Pipeline Stage

As an **Alteia engineer (Sam)**,
I want OpenDSS `export cim100` to produce combined CDPSM XML for IEEE 13,
So that the canonical hub artifact includes all six IEC 61968-13:2021 sub-profiles.

**Acceptance Criteria:**

**Given** IEEE 13 OpenDSS seed and `uuids.dat`
**When** I run `export-cim100` for feeder `ieee13`
**Then** `work/ieee13/cim/ieee13cdpsm.xml` is produced
**And** the XML includes FUN, EP, TOPO, CAT, GEO, and SSH sub-profiles per NFR-1
**And** CIM100 namespace matches binding pack `cim_namespace`
**And** re-export without uuid map change produces identical mRIDs for all equipment

**Traces:** FR-4; NFR-1

---

### Story 1.4: Implement Blazegraph Ingest Stage

As an **Alteia engineer (Sam)**,
I want combined CDPSM XML loaded into Blazegraph per feeder run,
So that CIMHub roundtrip and SPARQL-based checks can operate on the canonical graph.

**Acceptance Criteria:**

**Given** `ieee13cdpsm.xml` from Story 1.3
**When** I run `ingest-blazegraph` for feeder `ieee13`
**Then** the graph loads without structural ingest errors
**And** a SPARQL health query confirms the expected `Feeder` individual exists
**And** failures return exit code 2 (infra fail) with structured logs per NFR-5

**Traces:** FR-5; NFR-5

---

### Story 1.5: Implement CIMHub Roundtrip to Render Mirrors

As an **Alteia engineer (Sam)**,
I want CIMHub `CIMImporter` roundtrip producing OpenDSS and GridLAB-D render directories,
So that downstream PF and packaging stages have solver-ready mirrors.

**Acceptance Criteria:**

**Given** IEEE 13 CDPSM loaded in Blazegraph
**When** I run `cimhub-roundtrip` with `-o=both`
**Then** CIMHub roundtrip completes without structural errors (AT-13-1)
**And** `render/opendss/` and `render/gridlabd/` directories are produced under the feeder work path
**And** CIMHub structural test suite passes

**Traces:** FR-5; AT-13-1

---

### Story 1.6: Implement CIMHub PF vs OpenDSS Gold Comparison

As an **Alteia engineer (Sam)**,
I want CIMHub roundtrip PF compared against OpenDSS gold with recorded max ΔV,
So that physics agreement is verified before validation gate integration.

**Acceptance Criteria:**

**Given** IEEE 13 gold OpenDSS solve on original seed and CIMHub roundtrip outputs
**When** I run the PF comparison stage
**Then** max voltage magnitude delta ≤ 0.1% (AT-13-2, FR-6)
**And** results are written to a PF report structure compatible with `validation/pf-diff-report.json`
**And** exceedance produces a non-zero exit suitable for CI failure

**Traces:** FR-6; AT-13-2

---

## Epic 2: Binding Pack Integration & Validation Gate

Sam can gate promotion using binding-pack-driven T0 connectivity, pySHACL subset conformance, and dual PF with fail-closed JSON reports.

### Story 2.1: Wire Binding Pack v0 and P0 Workshop Artifacts

As an **Alteia engineer (Sam)**,
I want the pipeline to load `gridos-binding-pack.yaml` and reference P0 workshop artifacts,
So that tolerances, SHACL path, registry URI, and ingest subset are runtime-configurable per FR-1/FR-2.

**Acceptance Criteria:**

**Given** `config/gridos-binding-pack.yaml` with `binding_version: 2026.05.1` and `platform_release: GridOS-2026.2-lab`
**When** any pipeline stage requests binding pack configuration
**Then** tolerances, `shacl_bundle` path, `artifact_registry.base_uri`, and profile requirements load from YAML
**And** `gridos-binding-pack.yaml` validates against binding pack v0 schema (FR-2)
**And** docs link to P0 ingest spec and `p0-workshop-outcomes-2026-05-27.md` §2 class allow-list (FR-1)
**And** P0 approval record (Elena Vasquez, 2026-05-27) is referenced before first P1 fabric-lab promotion flag is enabled
**And** no workshop class tables or approver names are hard-coded in application logic

**Traces:** FR-1, FR-2; NFR-4; OQ-2, OQ-3

---

### Story 2.2: Implement T0 Connectivity Validation

As an **Alteia engineer (Sam)**,
I want T0 checks for terminals, ConnectivityNodes, feeder scope, and dangling terminals,
So that structurally invalid graphs never reach packaging.

**Acceptance Criteria:**

**Given** IEEE 13 CDPSM in Blazegraph after roundtrip
**When** I run the T0 connectivity gate
**Then** CIMHub structural tests and custom SHACL cardinalities execute
**And** dangling terminals or missing feeder scope produce explicit errors in CI logs (FR-7)
**And** T0 failure blocks promotion with exit code 1
**And** gate emits structured JSON observability per NFR-5

**Traces:** FR-7; AT-13 gate suite (structural)

---

### Story 2.3: Implement pySHACL GridOS Subset Gate

As an **Alteia engineer (Sam)**,
I want pySHACL validation against the GridOS CDPSM subset bundle pinned in the binding pack,
So that disallowed classes and cardinality violations block promotion.

**Acceptance Criteria:**

**Given** `shacl/gridos-cdpsm-subset.ttl` at the path declared in binding pack (FR-3)
**When** I run pySHACL on IEEE 13 CDPSM
**Then** `validation/shacl-report.json` is produced with `status: pass` and `violation_count: 0` (AT-13-4)
**And** SHACL violations block promotion (FR-9)
**And** violations list includes `path`, `message`, and `focus_node` per architecture report schema
**And** 100% of promoted artifacts will include this report (FR-3 consequence)

**Traces:** FR-3, FR-9; AT-13-4

---

### Story 2.4: Implement Dual PF Gate (OpenDSS vs GridLAB-D)

As an **Alteia engineer (Sam)**,
I want dual PF comparison of GridLAB-D roundtrip vs OpenDSS gold using binding-pack tolerances,
So that Tier A promotion is physics-gated per D5/ADR-003.

**Acceptance Criteria:**

**Given** binding pack `pf_tolerances` (vm ≤ 0.1%, angle ≤ 0.01°, source kW/kvar ≤ 0.5%)
**When** I run the dual PF gate on IEEE 13
**Then** `validation/pf-diff-report.json` records per-metric pass/fail and max deltas (AT-13-3, FR-8)
**And** promotion is blocked when any metric exceeds tolerance
**And** optional pandapower results, if collected, do not set `pf_gate_status: pass`
**And** tolerances are read from binding pack, not code constants

**Traces:** FR-8; AT-13-3; ADR-003

---

## Epic 3: Tier A Fabric ZIP Packager & CLI

Sam can produce a §10.2-compliant Tier A `.tar.gz` with manifest, validation reports, and render mirrors via `grid-synth` CLI.

### Story 3.1: Implement Fabric ZIP Packager (§10.2 Layout)

As an **Alteia engineer (Sam)**,
I want a packager that assembles a Tier A `.tar.gz` after all gates pass,
So that fabric-ready artifacts match the v0 directory contract.

**Acceptance Criteria:**

**Given** passing gate outputs for IEEE 13 (SHACL + PF reports, CDPSM XML, render mirrors)
**When** I run the fabric packager
**Then** the archive contains `manifest.json`, `cim/ieee13cdpsm.xml`, `validation/shacl-report.json`, `validation/pf-diff-report.json`, `render/opendss/`, and `render/gridlabd/` (FR-10, AT-13-5)
**And** `render/cgmes/` is empty or omitted for v1 Tier A
**And** packager refuses stale reports from a different run id/timestamp (fail-closed)
**And** SHA-256 checksums for CIM and render artifacts are computed for manifest inclusion

**Traces:** FR-10, FR-24 (checksums); AT-13-5

---

### Story 3.2: Implement manifest.json Builder with T0/T1 Labels

As an **Alteia engineer (Sam)**,
I want `manifest.json` emitted with all §10.3 required fields and gate statuses,
So that registry consumers can trust validation tier and binding pack correlation.

**Acceptance Criteria:**

**Given** a passing IEEE 13 promotion run and active binding pack
**When** the packager writes `manifest.json`
**Then** required fields are present: `dataset_id`, `version`, `tier`, `binding_pack_version`, `cdpsm_edition`, `platform_release`, `validation_tiers`, `feeders`, `validation`, `artifacts`, `published_at`, `git_tag` (FR-11)
**And** `tier` is `"A"` and `validation_tiers` is `["T0", "T1"]` only (FR-12)
**And** `validation.shacl_status` and `validation.pf_gate_status` reflect actual gate outcomes
**And** `binding_pack_version` matches active `gridos-binding-pack.yaml`

**Traces:** FR-11, FR-12

---

### Story 3.3: Implement grid-synth CLI (run / validate / pack)

As an **Alteia engineer (Sam)**,
I want a Typer CLI orchestrating export → validate → pack for a named feeder,
So that lab and CI can produce fabric ZIP + reports in one command.

**Acceptance Criteria:**

**Given** the Docker lab image and implemented pipeline stages
**When** I run `grid-synth run --feeder ieee13 --binding-pack config/gridos-binding-pack.yaml --out dist/`
**Then** a fabric ZIP and validation reports are produced for IEEE 13 in one invocation (FR-13)
**And** `grid-synth validate` and `grid-synth pack` subcommands map 1:1 to gate and packager stages
**And** validation failure returns non-zero exit code 1; infra failure returns exit code 2
**And** `--skip-adms` defaults true (ADMS smoke external per FR-21)

**Traces:** FR-13; NFR-6

---

## Epic 4: PR CI Path — IEEE 13 + 123

Sam gets automated PR feedback: IEEE 13 and 123 pass full pipeline within the 10-minute CI budget.

### Story 4.1: Add validate-ieee13 CI Job

As an **Alteia engineer (Sam)**,
I want `validate-ieee13` running on every PR,
So that IEEE 13 regressions block merge before they reach main.

**Acceptance Criteria:**

**Given** `.github/workflows/validate-pr.yml` triggered on PR to `main`
**When** the `validate-ieee13` job runs `grid-synth run --feeder ieee13` in Docker
**Then** the job passes when AT-13-1 through AT-13-5 gate tests pass (AT-13-7)
**And** job failure blocks merge
**And** structured logs and JSON reports are archived as CI artifacts per NFR-5

**Traces:** FR-14; AT-13-7

---

### Story 4.2: Promote IEEE 123 Through Full Pipeline

As an **Alteia engineer (Sam)**,
I want IEEE 123 seeded and promoted through the same export → validate → pack path,
So that switch-state SSH and larger topology regressions are covered on PR path.

**Acceptance Criteria:**

**Given** `feeders/ieee123/` with OpenDSS master and checked-in `uuids.dat`
**When** I run the full pipeline for `ieee123`
**Then** all AT-13 gate tests pass on the IEEE 123 artifact (AT-123-1)
**And** SSH profile includes switch state sufficient for trace smoke scenarios (AT-123-2, FR-16)
**And** a Tier A fabric ZIP is produced with correct `dataset_id` pattern `ieee123-asbuilt`
**And** mRID stability holds per NFR-2

**Traces:** FR-16; AT-123-1, AT-123-2

---

### Story 4.3: Enforce Combined PR CI Budget (13 + 123 < 10 min)

As an **Alteia engineer (Sam)**,
I want `validate-ieee123` on PR with combined duration logging,
So that the 13+123 validation budget meets NFR-7.

**Acceptance Criteria:**

**Given** PR workflow running both `validate-ieee13` and `validate-ieee123`
**When** both jobs complete on a standard org CI runner
**Then** combined wall-clock duration is logged and fails the workflow if > 10 minutes (FR-14, AT-123-5, NFR-7)
**And** failed gates block merge regardless of duration

**Traces:** FR-14; AT-123-5; NFR-7

---

## Epic 5: Nightly Large-Feeder Validation (8500 / 9500)

Sam gets nightly validation on IEEE 8500 and 9500 including regulator PF and six-point 9500 pattern within documented CI bounds.

### Story 5.1: Document CI Memory and Time Bounds for 8500/9500

As an **Alteia engineer (Sam)**,
I want numeric CI bounds documented before large-feeder promotion,
So that AT-8500-3 can be signed off and nightly jobs avoid OOM.

**Acceptance Criteria:**

**Given** reference CI runner profile used for nightly jobs
**When** I publish `docs/ci-bounds.md`
**Then** documented memory ceiling and time budget for IEEE 8500 and 9500 PF/packager jobs are recorded (NFR-8, G-1)
**And** bounds are referenced by nightly workflow configuration
**And** AT-8500-3 pass criteria reference these numeric limits

**Traces:** NFR-8; AT-8500-3; Architecture G-1

---

### Story 5.2: Promote IEEE 8500 Through Full Gate

As an **Alteia engineer (Sam)**,
I want IEEE 8500 promoted with regulator/capacitor PF validation within CI bounds,
So that mid-scale benchmark feeders are Tier A ready.

**Acceptance Criteria:**

**Given** `feeders/ieee8500/` seed (Git LFS if required) and documented CI bounds from Story 5.1
**When** I run the full pipeline for `ieee8500` in nightly or dedicated job
**Then** all AT-13 gate tests pass on IEEE 8500 artifact (AT-8500-1)
**And** dual PF passes with regulator devices modeled (AT-8500-2, FR-17)
**And** job completes within documented memory/time bounds without OOM (AT-8500-3)
**And** Tier A fabric ZIP is emitted

**Traces:** FR-17; AT-8500-1, AT-8500-2, AT-8500-3

---

### Story 5.3: Promote IEEE 9500 with Six-Point PF Validation

As an **Alteia engineer (Sam)**,
I want IEEE 9500 promoted with six sample PF points per IEEE 9500 paper pattern,
So that the flagship feeder meets SM-8 and AT-9500 criteria.

**Acceptance Criteria:**

**Given** `feeders/ieee9500/` seed and binding pack tolerances
**When** I run the full pipeline for `ieee9500`
**Then** all AT-13 gate tests pass (AT-9500-1)
**And** `pf-diff-report.json` includes six sample points comparing OpenDSS vs GridLAB-D, all within §10.1 tolerances (AT-9500-2, FR-18)
**And** 100% PF gate pass on gold base case (AT-9500-6, SM-8)
**And** Tier A fabric ZIP is emitted with `dataset_id` `ieee9500-asbuilt`

**Traces:** FR-18; AT-9500-1, AT-9500-2, AT-9500-6

---

### Story 5.4: Add validate-ieee9500 Nightly CI Job

As an **Alteia engineer (Sam)**,
I want `validate-ieee9500` running nightly on main,
So that flagship regressions are caught outside the PR path.

**Acceptance Criteria:**

**Given** `.github/workflows/validate-nightly.yml` on `main` branch schedule
**When** `validate-ieee9500` runs
**Then** IEEE 9500 full gate passes (AT-9500-3)
**And** pf-diff and memory/time metrics are logged per FR-15
**And** failures emit structured alerts/logs per NFR-5
**And** a dedicated `validate-ieee8500` job runs on nightly or manual trigger per FR-17

**Traces:** FR-15; AT-9500-3

---

## Epic 6: Tier A Registry Publication

Sam can publish immutable, checksum-verified Tier A artifacts to the internal registry on git tag with bundled render mirrors.

### Story 6.1: Implement publish-tier-a on Git Tag

As an **Alteia engineer (Sam)**,
I want tag-triggered publish to the internal artifact registry,
So that versioned Tier A bundles are consumable by GridOS lab and ADMS QA.

**Acceptance Criteria:**

**Given** git tag `v1.0.0` on `main` and passing promotion artifacts
**When** `publish-tier-a` workflow runs using `svc-alteia-synth-gen-ci` credentials
**Then** artifact is pushed to `{base_uri}{dataset_id}/v{semver}/` per §10.5 (FR-22, FR-15)
**And** published URI matches `{registry_base_uri}{dataset_id}/v{semver}/manifest.json` pattern
**And** `manifest.git_tag` matches tag name and `manifest.version` matches semver without `v` prefix (P-D7)
**And** registry entry includes manifest, checksums, binding pack version, and validation status
**And** human read access documented for AD group `gridos-lab-artifacts-ro`

**Traces:** FR-15, FR-22; NFR-9; P-D7, P-D11

---

### Story 6.2: Enforce Artifact Version Immutability

As an **Alteia engineer (Sam)**,
I want re-publish of the same semver with a different checksum rejected,
So that consumers can trust immutable artifact versions.

**Acceptance Criteria:**

**Given** an existing published artifact at `ieee13-asbuilt/v1.0.0/`
**When** CI attempts to publish the same semver with a different checksum
**Then** the registry client detects conflict and fails the publish job (FR-23)
**And** corrections require a new semver patch/minor
**And** publish job surfaces a clear immutability violation message

**Traces:** FR-23

---

### Story 6.3: Verify Bundled Render Mirrors in Published Artifact

As an **Alteia engineer (Sam)**,
I want published artifacts to include solver-ready OpenDSS and GridLAB-D mirrors with matching checksums,
So that independent proof mirrors solve without modification.

**Acceptance Criteria:**

**Given** a published Tier A `.tar.gz` from Story 6.1
**When** ADMS QA or platform engineering extracts `render/opendss/` and `render/gridlabd/`
**Then** mirrors solve without modification using bundled files (FR-24)
**And** SHA-256 checksums in `manifest.artifacts` match archive contents
**And** checksum verification is part of publish job pre-flight

**Traces:** FR-24

---

## Epic 7: External Lab Gates — Fabric & ADMS Smoke (P1 Sign-off)

GridOS platform and ADMS QA execute fabric ingest and ADMS smoke on promoted artifacts; Alteia delivers procedures, criteria linkage, and gate templates — **not CI-blocked dev publish**.

### Story 7.1: Publish Fabric Smoke Ingest Procedure and Lab Checklist (External Execution)

As a **GridOS platform engineer (Elena)**,
I want a documented file-based ZIP ingest procedure and per-feeder checklist,
So that fabric smoke ingest for all four IEEE feeders can be executed and tracked in lab fabric without CI automation.

**Acceptance Criteria:**

**Given** promoted Tier A ZIPs for IEEE 13, 123, 8500, and 9500 from registry or local packager
**When** platform engineering follows `docs/fabric-smoke-procedure.md` on GridOS-2026.2-lab
**Then** file-based ZIP ingest succeeds without manual CIM repair for each feeder (FR-19, AT-13-6, AT-8500-4, AT-9500-4)
**And** procedure references P0 ingest spec and binding pack `fabric_ingest.mode: file_zip`
**And** checklist records pass/fail per feeder for P1 metric SM-3
**And** ingest failures block P1 sign-off until resolved or binding pack updated
**And** this story delivers **documentation and checklist only** — execution is **external/lab**, not a CI job

**Traces:** FR-19; AT-13-6, AT-8500-4, AT-9500-4; SM-3; P-D3

---

### Story 7.2: Link ADMS Smoke Criteria Document for P1 Harness

As a **GridOS ADMS QA engineer (Marcus)**,
I want ADMS smoke criteria frozen and referenced by the P1 test harness,
So that trace and PF spot checks are consistent across feeders before P1 execution.

**Acceptance Criteria:**

**Given** P0 co-authored draft `adms-smoke-criteria-v0.md` (workshop WS-7, FR-20)
**When** Alteia links criteria in repo docs and P1 harness configuration
**Then** criteria cover trace connectivity and PF spot checks per feeder
**And** criteria are frozen before first P1 promotion execution
**And** intermediate dev-registry publishes that pass T0/T1 gates do **not** require ADMS smoke (P-D8)
**And** no ADMS script IDs are invented — placeholders reference ADMS QA-owned script IDs (Architecture G-2)

**Traces:** FR-20; A5; P-D8; Architecture G-2

---

### Story 7.3: ADMS Smoke Execution Gate Template (External/Lab — P1 Sign-off)

As a **GridOS ADMS QA lead (Marcus Chen)**,
I want a P1 smoke execution report template and sign-off record for 4/4 feeders,
So that P1 closure (SM-4) is evidenced outside the Alteia CI pipeline.

**Acceptance Criteria:**

**Given** promoted bundles for IEEE 13, 123, 8500, and 9500 and frozen ADMS smoke criteria (Story 7.2)
**When** ADMS QA executes trace + PF smoke in lab per feeder
**Then** a smoke test report per feeder is stored alongside artifact or in QA system (FR-21)
**And** trace paths complete per co-authored criteria (AT-123-3)
**And** PF spot checks pass per criteria (AT-123-4, AT-8500-5, AT-9500-5)
**And** P1 approver sign-off requires 4/4 pass (SM-4, Marcus Chen)
**And** this story delivers **report template, sign-off checklist, and lab runbook** — execution is **external/lab**, explicitly **not** wired into `publish-tier-a` CI

**Traces:** FR-21; AT-123-3, AT-123-4, AT-8500-5, AT-9500-5; SM-4; P-D8

---

## Validation Summary (Step 4)

| Check | Result |
|-------|--------|
| All FR-1–FR-24 mapped to stories | Pass |
| All NFR-1–NFR-10 addressed in stories or additional requirements | Pass |
| Architecture implementation sequence reflected in epic/story order | Pass |
| AT-13/123/8500/9500 traced in acceptance criteria | Pass |
| FR-19–FR-21 execution deferred to external/lab | Pass |
| No forward story dependencies within epics | Pass |
| No REST, Tier B, IIDM, or UX scope creep | Pass |
| Starter = pipeline repo + Docker (not generic web starter) | Pass |
| Dev publish vs P1 smoke boundary (P-D8) documented | Pass |

**Workflow complete.** Next recommended steps: `bmad-generate-project-context`, `bmad-create-story` for Epic 1 Story 1.1, pin CI bounds (G-1) before Story 5.2.
