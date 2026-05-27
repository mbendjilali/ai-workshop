# P0 Workshop Outcomes — Synthetic Grid Network Data Generator (Tutorial Emulation)

**Date:** 2026-05-27  
**Facilitator:** Alteia (Bemobrr)  
**Attendees:** GridOS Fabric Platform Engineering, GridOS ADMS QA (consulted), Alteia engineering  
**Status:** Signed — P0 gate criteria met for ingest spec and binding pack v0

> **Tutorial note:** Names, release tags, and registry URLs are fictional stand-ins for a real GridOS P0 workshop. Replace with org-specific values in production.

---

## 1. Workshop decisions

| ID | Topic | Resolution |
|----|--------|------------|
| **WS-1** | Platform release pin | **GridOS-2026.2-lab** (latest lab train at workshop date) |
| **WS-2** | Fabric CDPSM class subset (OQ-2) | **Tier A ingest subset v0** — see §2 (signed as `fabric-cdpsm-ingest-spec-v0.md` reference) |
| **WS-3** | P0 approver (OQ-3) | **Elena Vasquez** — GridOS Fabric Platform Engineering Lead |
| **WS-4** | P1 approver (OQ-4) | **Marcus Chen** — GridOS ADMS QA Lead |
| **WS-5** | Artifact registry (OQ-5) | Base URI `https://artifactory.gridos.lab/tier-a/datasets/`; path pattern `{dataset_id}/v{semver}/`; access per §4 |
| **WS-6** | Ingest mode | **File-based ZIP** confirmed (no REST in v1) |
| **WS-7** | ADMS smoke criteria | Co-authored draft `adms-smoke-criteria-v0.md` — execution at P1 only |

---

## 2. Fabric CDPSM ingest subset v0 (OQ-2)

**Profiles required (unchanged):** FUN, EP, TOPO, CAT, GEO, SSH  

**Spatial containers (mandatory):** `Feeder`, `SubGeographicalRegion`, `GeographicalRegion`  

**Equipment & connectivity classes (allow-list for fabric ingest v0):**

| Category | CIM classes |
|----------|-------------|
| Connectivity | `ConnectivityNode`, `Terminal` |
| Conducting | `ACLineSegment`, `EnergyConsumer`, `PowerTransformer`, `PowerTransformerEnd`, `LinearShuntCompensator`, `SeriesCompensator` |
| Switching | `Breaker`, `Disconnector`, `Fuse`, `LoadBreakSwitch`, `Recloser`, `Jumper` (as modeled) |
| Regulation | `RegulatingControl`, `TapChanger`, `RatioTapChanger` |
| Voltage / structure | `BaseVoltage`, `VoltageLevel`, `BusbarSection` (where buswork modeled) |
| Containers | `Feeder`, `Substation`, `SubGeographicalRegion`, `GeographicalRegion` |
| Location | `Location`, `PositionPoint` (GEO profile) |
| Identifiers | `Asset`, `AssetInfo` (minimal for mRID stability) |

**Explicitly excluded v0 (reject at ingest validation):** `TopologicalNode`, `TopologicalIsland`, CGMES-only TSO equipment, `DifferenceModel` / as-operated deltas, customer/CIS classes, SCADA measurement instances.

**mRID rules:** Stable UUID from OpenDSS `uuids.dat`; no regeneration on re-export of same feeder seed.

---

## 3. Sign-offs

| Gate | Approver | Date | Evidence |
|------|----------|------|----------|
| P0 ingest spec + binding pack v0 | Elena Vasquez | 2026-05-27 | This document + PRD §10 updates |
| ADMS smoke criteria draft (P1 prep) | Marcus Chen (reviewed, not P1 gate) | 2026-05-27 | `adms-smoke-criteria-v0.md` (tutorial: referenced in PRD FR-20) |

---

## 4. Internal artifact registry (OQ-5)

| Field | Value |
|-------|--------|
| **Base URI** | `https://artifactory.gridos.lab/tier-a/datasets/` |
| **Publish trigger** | Git tag on `main` (semver tag = artifact version) |
| **CI principal** | Service account `svc-alteia-synth-gen-ci` |
| **Human read** | AD group `gridos-lab-artifacts-ro` |
| **Human publish** | AD group `gridos-lab-artifacts-rw` (Alteia + platform) |
| **Immutability** | Re-publish same semver with different checksum → **reject** |

---

## 5. Action items post-workshop

1. Alteia: bump `gridos-binding-pack.yaml` to `binding_version: 2026.05.1` with subset + release pin.  
2. Alteia: configure CI `publish-tier-a` with registry credentials for `svc-alteia-synth-gen-ci`.  
3. Platform: provision IEEE 13 fabric smoke ingest slot on **GridOS-2026.2-lab**.  
4. ADMS QA: finalize `adms-smoke-criteria-v0.md` before first P1 promotion (Marcus Chen).
