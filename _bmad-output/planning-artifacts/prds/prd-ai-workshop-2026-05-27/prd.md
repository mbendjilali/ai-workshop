---
title: "PRD — Alteia Synthetic Grid Network Data Generator for GridOS"
status: final
created: 2026-05-27
updated: 2026-05-27
inputs:
  - brief-ai-workshop-2026-05-27
  - brief-addendum
  - brief-decision-log-d1-d9
scope: P0 + P1
product: Alteia synthetic grid network data generator
---

# PRD: Alteia Synthetic Grid Network Data Generator for GridOS

## 0. Document Purpose

This PRD defines **v1 (P0 + P1)** requirements for an internal, standards-native synthetic distribution network data product for **GridOS®**. It is written for Alteia engineering (builder), GridOS platform/fabric engineering (P0 approver), and GridOS ADMS QA (P1 approver). Downstream consumers: `bmad-create-architecture`, epics/stories, and CI implementation.

Structure: Glossary-anchored vocabulary; features grouped by phase with globally numbered FRs; cross-cutting NFRs; **interface contracts v0** (binding pack, manifest, fabric ZIP); **per-feeder acceptance tests**; decision traceability to brief log D1–D9. Technical depth beyond contracts lives in `briefs/brief-ai-workshop-2026-05-27/addendum.md`.

---

## 1. Vision

GridOS engineering and QA today rely on ad hoc lab feeders and partial GIS exports because production utility models cannot enter dev/test. Public IEEE benchmarks prove the conversion pattern but do not ship **fabric-ready CDPSM**, **versioned as-built semantics**, or **GridOS-specific regression packs**.

Alteia will deliver a **generator and packaging pipeline** that maintains one canonical **CDPSM/CIM100** semantic graph, seeds from **IEEE 13 → 123 → 8500 → 9500** benchmark feeders, gates promotion behind **structural validation + dual power-flow agreement**, and publishes **Tier A fabric-ready artifacts** pinned to a **GridOS binding pack**. Success is measured in repeatable CI artifacts, physics-gated promotion, and reduced time-to-regression for ADMS on shared fabric semantics — not in retail UMS positioning or Visual Intelligence delivery.

This is an **enabling data product** for GridOS quality. Value comes from GridOS integration discipline, validation gates, and release coupling — not from generic synthetic graph generation.

---

## 2. Target User

### 2.1 Jobs To Be Done

- **GridOS platform / fabric engineering:** Define and stabilize the CDPSM ingest subset and mRID rules so IEEE bundles load without manual repair.
- **GridOS ADMS QA:** Pull versioned dataset artifacts, import to fabric, and run repeatable trace + PF smoke tests instead of one-off internal feeders.
- **Alteia engineering:** Operate a CI-friendly generator pipeline that produces signed-off artifacts in an internal registry.
- **Network Model Orchestration integrators (consulted):** Consume as-built CDPSM snapshots; as-operated deltas deferred to P3.

### 2.2 Non-Users (v1)

- External utilities or partners expecting **Tier B CGMES IOP** bundles (deferred).
- Visual Intelligence teams expecting imagery or inspection overlays (deferred — mRID/geo hooks only where already in CDPSM GEO export).
- Operators seeking parameterized synthesis, FLISR/outage scenario packs, or REST self-service lab APIs (deferred).

### 2.3 Key User Journeys

- **UJ-1. Alex (platform engineer) co-designs the ingest spine.** Alex joins the P0 week-1 workshop with Alteia. Together they agree CDPSM profiles (FUN/EP/TOPO/CAT/GEO/SSH), spatial container rules, mRID stability, and SHACL subset shapes. Alex signs P0 when the binding pack v0 and IEEE 13 fabric ZIP ingest without manual repair. *Realizes P0 gate.*

- **UJ-2. Jordan (ADMS QA) runs smoke regression on promoted feeders.** Jordan pulls `ieee9500-asbuilt-v1.x.x` from the internal registry, imports via documented file-based ingest, runs trace + PF smoke scripts. Pass criteria were co-authored in P0; Jordan signs P1 when 4/4 IEEE feeders pass. *Realizes P1 gate.*

- **UJ-3. Sam (Alteia engineer) promotes IEEE 123 through CI.** Sam opens a PR touching the packager. CI runs `validate-ieee13` and `validate-ieee123` (< 10 min). On merge to main, nightly jobs cover 9500. Tag triggers `publish-tier-a` with manifest, SHACL report, and pf-diff-report. *Realizes FR-1 through FR-24.*

---

## 3. Glossary

- **Alteia** — GE Vernova Electrification Software team building the generator pipeline.
- **Binding pack** — Versioned YAML contract co-owned with GridOS platform; pins CDPSM subset, mRID rules, SHACL bundle reference, and platform release compatibility.
- **CDPSM** — IEC 61968-13:2021 Common Distribution Power System Model; canonical semantic layer for Tier A.
- **CIM100** — CIM namespace `http://iec.ch/TC57/CIM100#` used in CDPSM exports.
- **Dual PF gate** — Pre-ADMS promotion check: OpenDSS gold vs GridLAB-D roundtrip tolerances (not pandapower for NA unbalanced feeders).
- **Fabric** — GridOS federated grid data fabric consumed by ADMS, DERMS, and Network Model Orchestration.
- **Fabric smoke ingest** — Platform-verified load of a Tier A ZIP into lab fabric without manual CIM repair.
- **Feeder** — Distribution network container scoped for ingest; IEEE benchmark maps 1:1 to a Feeder artifact.
- **mRID** — Master resource identifier; must remain stable across re-exports via OpenDSS `uuids.dat`.
- **Tier A** — GridOS-native CDPSM bundles with binding-pack validation (v1 scope).
- **Tier B** — Partner-oriented CGMES exports with ENTSO-E SHACL (out of v1).
- **T0 / T1 validation tier** — T0 = connectivity/structural; T1 = PF-ready impedances and transformers. T2+ deferred.
- **Tier A artifact** — Published `.tar.gz` or OCI image: manifest + CDPSM + validation reports + render mirrors.

---

## 4. Features

### 4.1 P0 — GridOS Binding Pack Co-Design

**Description:** Alteia and GridOS platform engineering co-design the fabric CDPSM ingest subset, spatial containers, mRID rules, and GridOS subset SHACL. Output is **binding pack v0** referenced by every Tier A artifact. Realizes UJ-1. Traces **D1, D4, D8, D9**.

**Functional Requirements:**

#### FR-1: P0 workshop and ingest spec

Alteia can facilitate a P0 week-1 workshop with GridOS platform/fabric engineering to produce a written **fabric CDPSM ingest spec** covering: required profiles, spatial container model (`Feeder`, `SubGeographicalRegion`), mRID/uuid mapping, and smoke ingest procedure.

**Consequences (testable):**
- Written ingest spec document exists and is referenced by binding pack v0.
- Spec lists required CDPSM sub-profiles: FUN, EP, TOPO, CAT, GEO, SSH.
- Platform P0 approver (see §8) signs spec before P1 feeder promotion begins.

#### FR-2: Binding pack v0 publication

Alteia can publish **binding pack v0** (YAML) co-versioned with the **latest GridOS platform release at publish time** [per D8].

**Consequences (testable):**
- `gridos-binding-pack.yaml` validates against binding pack v0 schema (§10.1).
- `platform_release` field matches latest GridOS release at publish time or documents override rationale.
- Every Tier A `manifest.json` includes matching `binding_pack_version`.

#### FR-3: GridOS subset SHACL co-development

Alteia can co-develop **GridOS CDPSM subset SHACL** shapes with platform engineering and pin the bundle path in the binding pack.

**Consequences (testable):**
- SHACL bundle file exists at path declared in binding pack.
- pySHACL run against IEEE 13 CDPSM returns `pass` before fabric ZIP promotion.
- 100% of published Tier A artifacts include `validation/shacl-report.json` with `status: pass`.

**Feature-specific NFRs:**
- Binding pack changes require platform P0 re-approval when ingest subset or mRID rules change.

**Notes:** `[NOTE FOR PM]` Record approver names at P0 kickoff (placeholder until workshop).

---

### 4.2 P0 — Canonical CDPSM Pipeline (IEEE 13 Spine)

**Description:** End-to-end pipeline from IEEE 13 OpenDSS seed through CDPSM hub to validation-ready graph. Adopts CIMHub + Powergrid-Models + Blazegraph + CIMantic Graphs; builds fabric packager and binding integration only. Realizes UJ-3. Traces **D4, D5**.

**Functional Requirements:**

#### FR-4: OpenDSS to CDPSM export

The pipeline can ingest IEEE 13 OpenDSS feeder and emit combined CDPSM XML via `export cim100` with stable `uuids.dat`.

**Consequences (testable):**
- Combined CDPSM XML includes all six sub-profiles per IEC 61968-13:2021.
- Re-export without uuid map change produces identical mRIDs for all equipment.

#### FR-5: Blazegraph ingest and CIMHub roundtrip

The pipeline can load CDPSM to Blazegraph and run CIMHub `CIMImporter` roundtrip to OpenDSS and GridLAB-D.

**Consequences (testable):**
- CIMHub roundtrip completes without structural errors on IEEE 13.
- Roundtrip OpenDSS and GridLAB-D render directories are produced under `render/`.

#### FR-6: CIMHub roundtrip PF agreement

The pipeline can compare CIMHub roundtrip PF against OpenDSS gold with max ΔV ≤ **0.1%** per technical research KPI.

**Consequences (testable):**
- `validation/pf-diff-report.json` records max voltage magnitude delta ≤ 0.1% for IEEE 13.
- CI job `validate-ieee13` fails on exceedance.

**Out of Scope:**
- Custom IIDM-style internal canonical model (ADR-001: CDPSM hub only).

---

### 4.3 P0 — Validation Gate

**Description:** Structural and physics gates block promotion to fabric ZIP. Dual PF = OpenDSS + GridLAB-D [D5]. Pandapower is not a blocking gate for typical NA unbalanced feeders.

**Functional Requirements:**

#### FR-7: T0 connectivity validation

The validation gate can enforce T0 checks: terminals, ConnectivityNodes, feeder scope, dangling terminal detection.

**Consequences (testable):**
- T0 failures block promotion with explicit error in CI logs.
- CIMHub structural tests + custom SHACL cardinalities run on every promote path.

#### FR-8: Dual PF gate (OpenDSS vs GridLAB-D)

Before **Tier A fabric ZIP promotion**, the gate can enforce dual PF tolerances on roundtrip solvers:

| Metric | Tolerance |
|--------|-----------|
| Voltage magnitude (per phase) | ≤ 0.1% vs OpenDSS gold |
| Voltage angle | ≤ 0.01° where applicable |
| Source kW/kvar | ≤ 0.5% |

**Consequences (testable):**
- `pf-diff-report.json` includes per-metric pass/fail and max deltas.
- Promotion blocked when any metric exceeds tolerance.
- Pandapower results, if collected, are informational only and do not unblock promotion [D5].

#### FR-9: pySHACL structural conformance

The gate can run pySHACL against GridOS subset SHACL bundle before promotion.

**Consequences (testable):**
- SHACL violations block promotion.
- `shacl-report.json` lists violation count (zero required for pass).

---

### 4.4 P0 — Fabric ZIP Packager and Manifest

**Description:** On validation pass, emit Tier A fabric-ready ZIP with manifest and checksums per contract v0 (§10). Realizes UJ-1, UJ-3.

**Functional Requirements:**

#### FR-10: Fabric ZIP layout v0

The packager can emit a `.tar.gz` (or OCI-equivalent) matching §10.2 directory layout.

**Consequences (testable):**
- Archive contains: `manifest.json`, `cim/*.xml`, `validation/shacl-report.json`, `validation/pf-diff-report.json`, `render/opendss/`, `render/gridlabd/`.
- `render/cgmes/` directory present but empty or omitted for v1 Tier A.
- SHA-256 checksums for CIM and render artifacts recorded in manifest.

#### FR-11: manifest.json v0

The packager can emit `manifest.json` conforming to §10.3 minimum fields.

**Consequences (testable):**
- Required fields present: `dataset_id`, `version`, `tier`, `binding_pack_version`, `cdpsm_edition`, `platform_release`, `validation_tiers`, `feeders`, `validation`, `artifacts`, `published_at`, `git_tag`.
- `validation.shacl_status` and `validation.pf_gate_status` reflect gate outcomes.
- `tier` = `"A"` for all v1 artifacts.

#### FR-12: T0/T1 tier labels on datasets

Published datasets can declare validation tier labels **T0 connectivity** and **T1 PF-ready** in manifest metadata.

**Consequences (testable):**
- `manifest.json` includes `validation_tiers: ["T0", "T1"]` for promoted bundles.
- T2+ tiers absent from v1 publications.

---

### 4.5 P0 — CLI, Batch, and CI

**Description:** Container-first CLI/batch for lab and CI [ASSUMPTION A3]. No REST API in v1.

**Functional Requirements:**

#### FR-13: CLI entry point

Alteia engineering can run a CLI (Typer/Click) to execute: export → validate → packager for a named IEEE feeder.

**Consequences (testable):**
- Single command produces fabric ZIP + reports for IEEE 13 in Docker lab image.
- Exit code non-zero on validation failure.

#### FR-14: CI jobs — PR path

CI can run `validate-ieee13` on every PR and complete IEEE 13 + 123 validation in **< 10 minutes** [ASSUMPTION A7].

**Consequences (testable):**
- PR pipeline duration logged; fails if > 10 min for 13+123 combined job.
- Failed gate blocks merge.

#### FR-15: CI jobs — nightly and publish

CI can run `validate-ieee9500` nightly and `publish-tier-a` on **git tag** to an **internal registry** with semver-correlated artifacts (registry URL TBD at P0 — OQ-5).

**Consequences (testable):**
- Nightly 9500 job produces pf-diff and memory/time metrics.
- Tag publish pushes versioned artifact with immutable checksum.

**Out of Scope:**
- REST self-service lab API (non-goal).
- External partner distribution of artifacts [ASSUMPTION A1].

---

### 4.6 P1 — IEEE Feeder Scale-Up (123, 8500, 9500)

**Description:** Promote remaining IEEE benchmarks through the same pipeline with feeder-specific acceptance tests (§11). Traces **D2**.

**Functional Requirements:**

#### FR-16: IEEE 123 promotion

The pipeline can promote IEEE 123 through full gate and emit Tier A fabric ZIP.

**Consequences (testable):**
- AT-123 acceptance tests pass (§11).
- SSH profile includes switch state sufficient for trace smoke.

#### FR-17: IEEE 8500 promotion

The pipeline can promote IEEE 8500 through full gate within CI memory/time budget.

**Consequences (testable):**
- AT-8500 acceptance tests pass (§11).
- Nightly or dedicated job completes PF within documented memory bound.

#### FR-18: IEEE 9500 flagship promotion

The pipeline can promote IEEE 9500 through full gate including six-point PF validation pattern from IEEE 9500 paper.

**Consequences (testable):**
- AT-9500 acceptance tests pass (§11).
- pf-diff-report includes six sample points comparing OpenDSS vs GridLAB-D.

---

### 4.7 P1 — Fabric Smoke Ingest

**Description:** All four IEEE feeders pass fabric smoke ingest in GridOS lab via **file-based ZIP upload** (REST deferred; P-D3).

**Functional Requirements:**

#### FR-19: Fabric smoke ingest — 4/4 feeders

GridOS platform can ingest Tier A ZIP for **IEEE 13, 123, 8500, 9500** without manual CIM repair.

**Consequences (testable):**
- Documented **file-based ZIP ingest** procedure (from P0 spec) succeeds for each feeder in lab fabric.
- Ingest failures block P1 sign-off until resolved or binding pack updated.
- **4/4 feeders pass** is a P1 success metric (SM-3).

---

### 4.8 P1 — ADMS Smoke (Trace + PF)

**Description:** ADMS QA runs trace + PF smoke on promoted bundles at **P1 milestone sign-off**; criteria co-authored in P0. Intermediate dev-registry publishes do not require ADMS smoke (P-D8). Traces **D9**.

**Functional Requirements:**

#### FR-20: ADMS smoke criteria definition

Alteia and ADMS QA can document smoke test criteria (trace paths, PF buses, tolerances) during P0 and freeze before P1 execution.

**Consequences (testable):**
- Written ADMS smoke criteria document referenced by P1 test harness.
- Criteria cover trace connectivity and PF spot checks per feeder.

#### FR-21: ADMS smoke execution — 4/4 feeders

ADMS QA can execute smoke tests on all four promoted bundles and record pass/fail.

**Consequences (testable):**
- Smoke test report per feeder stored alongside artifact or in QA system.
- P1 approver sign-off requires 4/4 pass (SM-4).
- Failures block P1 gate until regression fixed or criteria adjusted with documented approval.
- ADMS smoke **not** required for intermediate dev-registry publishes that pass T0/T1 gates only (P-D8).

---

### 4.9 P1 — Tier A Artifact Registry

**Description:** Internal registry of versioned Tier A bundles with manifest and validation reports.

**Functional Requirements:**

#### FR-22: Artifact registry publication

Alteia can publish promoted Tier A artifacts to an internal registry triggered by **git tag**, with **semver + git tag** correlation in manifest (P-D7).

**Consequences (testable):**
- Each published artifact is retrievable by `dataset_id` + `version`.
- Registry entry includes manifest, checksums, binding pack version, validation status.

#### FR-23: Artifact immutability

Published artifact versions are immutable; corrections require new semver patch/minor.

**Consequences (testable):**
- Re-publish of same version with different checksum is rejected by registry policy.

#### FR-24: OpenDSS/GridLAB-D mirrors bundled

Every Tier A artifact includes independent proof mirrors under `render/opendss/` and `render/gridlabd/`.

**Consequences (testable):**
- Mirrors solve without modification using bundled files.
- Checksums in manifest match archive contents.

---

## 5. Cross-Cutting Non-Functional Requirements

#### NFR-1: Standards alignment

All Tier A artifacts conform to **IEC 61968-13:2021 CDPSM** and **CIM100** namespace declared in binding pack.

#### NFR-2: mRID stability

mRIDs remain stable across pipeline re-runs when source `uuids.dat` unchanged; uuid map checked into source control per feeder.

#### NFR-3: No real utility data

Synthetic datasets contain no real utility IDs, customer data, or re-identifiable AMI patterns.

#### NFR-4: Binding pack release coupling

When GridOS platform ships a new release, binding pack is refreshed and compatibility documented before next Tier A publish [D8].

#### NFR-5: Observability

CI jobs emit structured logs and machine-readable validation reports (JSON) for every gate stage.

#### NFR-6: Deployment

CLI and batch run in **Docker** lab image [ASSUMPTION A3]; compatible with GitHub Actions and Kubernetes Job execution.

#### NFR-7: Performance — CI budget

PR-path validation (IEEE 13 + 123) completes in **< 10 minutes** on standard CI runners.

#### NFR-8: Performance — IEEE 8500/9500

8500/9500 PF and packager jobs complete within documented memory and nightly time budgets without OOM on reference runner (baseline defined with AT-8500-3; `[NOTE FOR PM]` pin numeric bound in architecture).

#### NFR-9: Security

Artifacts stored in internal registry only [ASSUMPTION A1]; no public CDN or external partner access in v1.

#### NFR-10: Maintainability

CIMHub, Blazegraph, and OpenDSS versions pinned in Docker image with documented upgrade policy.

---

## 6. MVP Scope

### 6.1 In Scope (P0 + P1)

- P0 workshop → fabric CDPSM ingest spec + binding pack v0
- IEEE **13, 123, 8500, 9500** → CDPSM → validation gate → fabric ZIP
- Dual PF gate (OpenDSS + GridLAB-D); CIMHub roundtrip
- GridOS subset SHACL (co-developed)
- CLI + batch CI; Docker deployment
- Fabric smoke ingest 4/4; ADMS trace + PF smoke 4/4
- Tier A artifact registry with manifest and reports
- T0/T1 tier labels on published datasets

### 6.2 Out of Scope for MVP

| Item | Reason | Brief ref |
|------|--------|-----------|
| **Tier B** — CGMES IOP, Oracle/Schneider runbooks, ENTSO-E FAT | After Tier A stable; dual validation avoided | D1, non-goals |
| **P4 Visual Intelligence** — imagery, inspection overlays | User non-goal; mRID/geo hooks only where already exported | D3 |
| **P2** — parameterized feeders, PowerGridSynth, SCADA CSV, DER-heavy packs | Needs canonical path proven | Roadmap |
| **P3** — DifferenceModel as-operated, FLISR/outage scripts | Orchestration depth after ingest baseline | Roadmap |
| **P5** — partner IOP matrices | Commercial parity, not GridOS QA blocker | Non-goals |
| **REST API** self-service | CLI/batch first | Non-goals |
| **Retail SKU / external market** | Internal enabling product | D6 |
| **pandapower as blocking PF gate** for NA feeders | Technical correction | D5 |
| **DERMS separate sign-off gate** | Consulted in P0 only unless org adds | D9 note |

---

## 7. Success Metrics

**Primary**

- **SM-1:** P0 fabric ingest spec signed by platform approver. Validates FR-1, FR-2.
- **SM-2:** Binding pack v0 published; 100% Tier A artifacts reference it. Validates FR-2, FR-11. Traces D8.
- **SM-3:** Fabric smoke ingest **4/4** IEEE feeders. Validates FR-19.
- **SM-4:** ADMS smoke trace + PF **4/4** with ADMS QA sign-off. Validates FR-20, FR-21. Traces D9.

**Secondary**

- **SM-5:** CIMHub roundtrip max ΔV ≤ **0.1%** on all promoted feeders. Validates FR-6, FR-8.
- **SM-6:** GridOS subset SHACL **100% pass** on Tier A artifacts. Validates FR-3, FR-9.
- **SM-7:** CI PR path (13 + 123) **< 10 min**. Validates FR-14.
- **SM-8:** IEEE 9500 six-point PF pattern pass. Validates FR-18, AT-9500.

**Counter-metrics (do not optimize)**

- **SM-C1:** Count of CGMES/Tier B exports — defer; do not ship in v1.
- **SM-C2:** Pandapower agreement rate — informational only; not a promotion gate.
- **SM-C3:** Parameterized/synthetic feeder count — out of scope; avoid scope creep.

---

## 8. Stakeholders and Approvals

Two-step sign-off [D9]. **Placeholder names until P0 kickoff workshop** [OQ-3, OQ-4].

| Milestone | Deliverable approved | Approver role | Placeholder name |
|-----------|---------------------|---------------|------------------|
| **P0 done** | CDPSM subset + mRID rules + binding pack v0; IEEE 13 fabric ingest | GridOS platform / fabric engineering | `[TBD — Platform Approver]` |
| **P1 done** | 4/4 feeders pass ADMS trace + PF smoke | GridOS ADMS QA | `[TBD — ADMS QA Approver]` |
| **Build** | Generator, CI artifacts, registry publications | Alteia engineering | Alteia (builder) |

**Consulted (not gating v1):** DERMS QA, Network Model Orchestration integrators — where model semantics affect their paths.

---

## 9. Risk and Mitigations

| Risk | Impact | Mitigation | FR/SM |
|------|--------|------------|-------|
| Fabric binding drift across GridOS releases | Broken ingest on upgrade | Versioned binding pack; manifest pins `binding_pack_version` | FR-2, NFR-4 |
| Non-public fabric ingest API | Integration guesswork | **File-based ZIP confirmed** for v1; REST deferred | P-D3, FR-19 |
| CDPSM subset not agreed | Rework all feeders | P0 spec gate blocks P1 | FR-1 |
| No public CDPSM SHACL | Weak automated conformance | Co-develop GridOS subset SHACL | FR-3, FR-9 |
| Unrealistic physics | Unsafe ADMS normalization | Dual PF gate before promotion | FR-8 |
| Scope creep into Visual Intelligence | Delays network v1 | Non-goals; mRID stability only | D3, §6.2 |
| Unclear approvers | P0/P1 stall | Placeholders → names at kickoff | §8 |

---

## 10. Interface Contracts v0

*Normative for implementation. Changes require binding pack version bump and platform re-approval.*

### 10.1 Binding pack v0 (`gridos-binding-pack.yaml`)

```yaml
binding_version: "2026.05.0"          # semver; bump on subset/rule change
platform_release: "GridOS-TBD"        # latest GridOS release at publish [D8]
cdpsm_edition: "IEC-61968-13:2021"
cim_namespace: "http://iec.ch/TC57/CIM100#"
profiles_required: [FUN, EP, TOPO, CAT, GEO, SSH]
mrid_rules:
  stable_uuid: true
  source: opendss_uuids_dat
fabric_ingest:
  container_type: Feeder
  spatial: SubGeographicalRegion required
  mode: file_zip                        # v1 confirmed; REST deferred [P-D3]
validation:
  shacl_bundle: "./shacl/gridos-cdpsm-subset.ttl"
  pf_gate: opendss_gridlabd
  pf_tolerances:
    vm_delta_pct_max: 0.1
    angle_delta_deg_max: 0.01
    source_kw_kvar_delta_pct_max: 0.5
```

### 10.2 Fabric ZIP / Tier A artifact layout v0

```
{dataset_id}-v{semver}/
  manifest.json
  cim/
    {feeder}cdpsm.xml                  # combined CDPSM
    profiles/                          # optional split; may be omitted v0
  validation/
    shacl-report.json
    pf-diff-report.json
  render/
    opendss/
    gridlabd/
    cgmes/                             # empty or absent in v1
```

Packaging: `.tar.gz` required [ASSUMPTION A6]; OCI image optional for v0 with equivalent paths.

### 10.3 manifest.json v0 (minimum fields)

```json
{
  "dataset_id": "ieee9500-asbuilt",
  "version": "1.0.0",
  "tier": "A",
  "binding_pack_version": "2026.05.0",
  "cdpsm_edition": "IEC-61968-13:2021",
  "platform_release": "GridOS-TBD",
  "validation_tiers": ["T0", "T1"],
  "feeders": [{"mRID": "<uuid>", "name": "ieee9500", "node_count": 9500}],
  "validation": {
    "shacl_status": "pass",
    "pf_gate_status": "pass",
    "pf_max_vm_delta_pct": 0.05,
    "pf_gate": "opendss_gridlabd"
  },
  "artifacts": {
    "cim": "sha256:<hex>",
    "opendss": "sha256:<hex>",
    "gridlabd": "sha256:<hex>"
  },
  "published_at": "2026-05-27T00:00:00Z",
  "git_tag": "v1.0.0"
}
```

### 10.4 Promotion rules v0

1. All T0 + T1 gates pass (FR-7, FR-8, FR-9).
2. `binding_pack_version` in manifest matches active binding pack.
3. Platform P0 sign-off obtained before first P1 feeder promotion to fabric lab.
4. **Intermediate dev-registry publishes:** full validation gate required; **ADMS smoke not required** (P-D8, Option A).
5. **P1 milestone closure:** ADMS smoke pass required for all four feeders (FR-21, SM-4).

---

## 11. Per-Feeder Acceptance Tests

Global gate tolerances: §10.1 `pf_tolerances`. Each feeder adds scoped tests.

### AT-13 — IEEE 13 (P0 spine)

| # | Test | Pass criteria |
|---|------|---------------|
| AT-13-1 | CIMHub roundtrip | Completes without error |
| AT-13-2 | CIMHub PF vs gold | max ΔV ≤ 0.1% |
| AT-13-3 | Dual PF gate | OpenDSS vs GridLAB-D within §10.1 tolerances |
| AT-13-4 | SHACL | Zero violations |
| AT-13-5 | Fabric ZIP layout | §10.2 structure + manifest §10.3 |
| AT-13-6 | Fabric smoke ingest | Loads without manual repair |
| AT-13-7 | CI `validate-ieee13` | Pass on PR |

### AT-123 — IEEE 123 (P1)

| # | Test | Pass criteria |
|---|------|---------------|
| AT-123-1 | All AT-13 gate tests | Pass on IEEE 123 artifact |
| AT-123-2 | Switch state in SSH | Present for reconfiguration scenarios |
| AT-123-3 | Trace smoke | ADMS trace paths complete per co-authored criteria |
| AT-123-4 | PF smoke | ADMS PF spot checks within criteria |
| AT-123-5 | CI PR budget | Contributes to 13+123 < 10 min |

### AT-8500 — IEEE 8500 (P1)

| # | Test | Pass criteria |
|---|------|---------------|
| AT-8500-1 | All AT-13 gate tests | Pass on IEEE 8500 artifact |
| AT-8500-2 | Regulators/caps PF | Dual PF pass with regulator devices modeled |
| AT-8500-3 | CI memory/time | Job completes within documented bounds without OOM |
| AT-8500-4 | Fabric smoke ingest | Pass |
| AT-8500-5 | ADMS smoke | Trace + PF pass |

### AT-9500 — IEEE 9500 (P1 flagship)

| # | Test | Pass criteria |
|---|------|---------------|
| AT-9500-1 | All AT-13 gate tests | Pass on IEEE 9500 artifact |
| AT-9500-2 | Six-point PF validation | Six sample points per IEEE 9500 paper pattern; all within §10.1 tolerances |
| AT-9500-3 | Nightly CI | `validate-ieee9500` pass |
| AT-9500-4 | Fabric smoke ingest | Pass |
| AT-9500-5 | ADMS smoke | Trace + PF pass |
| AT-9500-6 | Flagship regression | SM-8; 100% PF gate pass on gold base case |

**P1 milestone aggregate:** AT-13, AT-123, AT-8500, AT-9500 all pass → SM-3, SM-4, FR-19, FR-21.

---

## 12. Decision Traceability (Brief D1–D9)

| Brief ID | Decision | PRD realization |
|----------|----------|-----------------|
| **D1** | GridOS-first Tier A before Tier B | §6.2 Tier B out of scope; FR-11 tier `"A"` only |
| **D2** | v1 = P0 + P1 only | §6.1; P2–P5 in §6.2 |
| **D3** | Defer P4 Visual Intelligence | §6.2; mRID/geo via CDPSM GEO only |
| **D4** | Canonical CDPSM hub (CIMHub) | FR-4–FR-6; §4.2; no IIDM |
| **D5** | Dual PF = OpenDSS + GridLAB-D | FR-8; §10.1; SM-C2 pandapower non-blocking |
| **D6** | Enabling data for GridOS QA, not retail UMS | §1 Vision; §6.2 retail out |
| **D7** | Technical depth in addendum | §0; contracts here, pipeline detail in addendum |
| **D8** | Binding pack pins latest GridOS release | FR-2; §10.1; SM-2; NFR-4 |
| **D9** | Two-step sign-off: platform P0, ADMS QA P1 | §8; FR-1, FR-21; SM-1, SM-4 |

### 12.1 PRD decisions (P-D*)

| PRD ID | Decision | PRD realization |
|--------|----------|-----------------|
| **P-D3** | File-based fabric ZIP ingest for v1 | FR-19, §10.1 `mode: file_zip` |
| **P-D7** | Git-tag → semver internal registry | FR-15, FR-22, §10.3 `git_tag` |
| **P-D8** | Dev publish: validation gate only; ADMS smoke at P1 sign-off | §10.4 rules 4–5, FR-21 |

---

## 13. Open Questions

1. **OQ-2:** Exact CDPSM class subset for fabric — blocks P0 sign-off. Owner: platform + Alteia.
2. **OQ-3:** Platform P0 approver name. Owner: P0 kickoff.
3. **OQ-4:** ADMS QA P1 approver name. Owner: P0 kickoff.
4. **OQ-5:** Internal artifact registry **URL/path** and access policy (publish model confirmed: git tag → semver artifact). Owner: platform + Alteia before first publish.

---

## 14. Assumptions Index

- **A1** (§6.2, NFR-9): v1 internal GridOS lab/CI only — no external partner CGMES ship.
- **A3** (FR-13, NFR-6): Docker lab image acceptable for CLI/batch.
- **A4** (§1): Alteia remains builder under GE Vernova Electrification Software.
- **A5** (FR-20): ADMS smoke criteria co-authored in P0; executed in P1.
- **A6** (§10.2): `.tar.gz` required; OCI optional for v0.
- **A7** (FR-14): Standard org CI runners meet 10 min budget for 13+123.

**Confirmed (no longer assumptions):** file-based fabric ingest (P-D3); git-tag internal registry (P-D7); ADMS smoke at P1 sign-off only (P-D8).

---

*Technical pipeline detail: `briefs/brief-ai-workshop-2026-05-27/addendum.md`*
