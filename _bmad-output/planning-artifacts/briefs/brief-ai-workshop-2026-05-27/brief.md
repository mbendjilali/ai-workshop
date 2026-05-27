---
title: "Product Brief — Alteia Synthetic Grid Network Data Generator for GridOS"
status: draft
created: 2026-05-27
updated: 2026-05-27
clarifications:
  binding_pack_release: "Latest GridOS platform/lab release at time of publish"
  governance: "Two-step sign-off — platform for P0 ingest rules, ADMS QA for P1 smoke tests (names TBD in PRD)"
author: Bemobrr
inputs:
  - domain-research-2026-05-27
  - technical-research-2026-05-27
---

# Product Brief: Alteia Synthetic Electrical Grid Network Data Generator (GridOS)

## Executive Summary

**Alteia** (GE Vernova Electrification Software) will deliver an **internal, standards-native synthetic distribution network data product** for **GridOS®**—the federated grid data fabric, **ADMS**, **DERMS**, and **Network Model Orchestration** (Smallworld ↔ fabric ↔ apps). GridOS engineering and QA today rely on ad hoc lab feeders and partial GIS exports because production utility models cannot enter dev/test. Public IEEE benchmarks and research platforms (GridAPPS-D, NLR) prove the pattern but do not ship **fabric-ready CDPSM**, **versioned as-built/as-operated semantics**, or **GridOS-specific regression packs**.

v1 establishes the **Tier A (GridOS) spine**: co-design a **binding pack** with platform engineering, promote **IEEE 13 → 123 → 8500 → 9500** through a validated **CDPSM hub** pipeline, and prove **fabric smoke ingest** plus **ADMS trace/PF smoke** before broader scenarios. **Tier B** partner exports (CGMES IOP, Oracle/Schneider runbooks) and **P4 Visual Intelligence** imagery linkage stay explicitly out of v1.

This is an **enabling data product** for GridOS quality—not a retail UMS or a Visual Intelligence feature. Success is measured in **repeatable CI artifacts**, **physics-gated promotion**, and **reduced time-to-regression** for ADMS/DERMS on shared fabric semantics.

---

## The Problem

Grid modernization (DER, FLISR, orchestration, digital twin) requires **connectivity-correct, engineering-complete, versioned** network models in test. Vendors and utilities spend months building lab pipelines (GIS → CIM → model build → validation). GridOS teams face the same gap at portfolio scale: **no industry-standard feeder** historically met control-center operational scenario needs (IEEE 9500 initiative). Internal teams still build **private test models**, which drift from fabric bindings and block ADMS/DERMS joint regression.

**Costs of status quo**

- Slow GridOS release qualification when fabric ingest rules change without golden datasets  
- ADMS/DERMS tests that do not share one **fabric semantics** graph  
- Partner IOP work blocked on **production-like** models utilities cannot share  
- Risk of **unrealistic physics** or **profile mismatch** when ad hoc exports reach ADMS  

Synthetic data must be **physically plausible**, **standards-aligned (IEC 61968-13 CDPSM)**, and **governed** (no real utility IDs or re-identifiable AMI).

---

## Who This Serves

| Persona | Need | v1 success for them |
|---------|------|---------------------|
| **GridOS platform / fabric engineering** | Stable CDPSM ingest subset, mRID rules, binding pack per release | P0 spec signed; IEEE bundles ingest without manual repair |
| **GridOS ADMS / DERMS QA** | Repeatable feeders + smoke PF/trace on fabric | P1: 4/4 IEEE feeders pass smoke matrix; **ADMS QA signs off** on smoke criteria |
| **Network Model Orchestration integrators** | As-built snapshots; path to as-operated deltas (later) | v1 delivers as-built CDPSM; DifferenceModel scenarios deferred to P3 |
| **Alteia engineering** | CI-friendly generator pipeline inside portfolio | CLI/batch artifacts in internal registry |
| **GridOS partner ecosystem** (secondary) | CGMES/IOP parity | **Out of v1** — Tier B after Tier A stable |

---

## The Solution

A **generator and packaging pipeline** that:

1. Maintains **one canonical CDPSM/CIM100 semantic graph** (hub-and-spoke architecture).  
2. Seeds from **IEEE benchmark feeders** and emits **fabric-ready Tier A bundles** with manifest, validation reports, and OpenDSS/GridLAB-D mirrors for independent proof.  
3. Gates **fabric promotion** behind **structural validation + OpenDSS/GridLAB-D power-flow agreement** (not pandapower for typical North American unbalanced feeders).  
4. Versions compatibility via a **GridOS binding pack** co-owned with platform releases.

**Experience:** QA and platform engineers pull a **versioned dataset artifact** (OCI/tar + manifest), import to fabric, run documented smoke tests—replacing one-off internal feeders.

**Out of v1 UX:** REST self-service lab API, parameterized synthesis, FLISR/outage scenario packs, imagery overlays.

---

## What Makes This Different

| Differentiator | Honest note |
|----------------|-------------|
| **Fabric-native + NMO-aligned** | Public IEEE kits are not GridOS binding-pack aware |
| **ADMS + DERMS shared fabric semantics** | Joint regression datasets, not single-app dumps |
| **Adopt proven CIM hub pattern (CIMHub/GridAPPS-D)** | Execution speed vs reinventing conversion |
| **mRID stability** | Foundation for future Visual Intelligence correlation—not v1 delivery |
| **Not a moat in “synthetic graphs”** | Value is **GridOS integration discipline + validation gates + release coupling** |

---

## Success Criteria (v1 / P0–P1)

| Metric | Target | Notes |
|--------|--------|-------|
| P0 fabric ingest spec | Signed CDPSM subset + mRID rules with platform team | Blocking deliverable |
| Binding pack v0 | Published and referenced in every Tier A artifact manifest | Pins to **latest GridOS release** at publish time; refresh when platform ships a new release |
| IEEE feeder promotion | **13, 123, 8500, 9500** → CDPSM → fabric smoke ingest | **4/4 pass** |
| CIMHub roundtrip PF | Max ΔV ≤ **0.1%** vs OpenDSS gold | Per technical research |
| Dual PF gate (pre-ADMS promote) | OpenDSS vs GridLAB-D within published tolerances | IEEE 9500 six-point pattern |
| Tier A SHACL / structural validation | **100%** pass on published bundles | Custom GridOS subset shapes (co-developed) |
| CI pipeline (13 + 123) | < **10 min** on PR path | Nightly full 9500 |
| ADMS smoke | Trace + PF smoke pass on promoted bundles | Criteria defined with **ADMS QA**; pass = their sign-off |

**Not v1 success metrics:** Partner ENTSO-E IOP sign-off, DERMS constraint scenario library, ML tensor exports, operator training realism certification.

---

## Scope — v1 (P0 + P1)

### P0 — Platform co-design and spine

- Workshop with GridOS platform engineering: **fabric CDPSM ingest subset**, spatial containers, mRID stability rules.  
- **Binding pack v0** (YAML manifest schema + validation profile reference).  
- **IEEE 13** end-to-end: OpenDSS → CDPSM → CIMHub roundtrip → dual PF → fabric-ready ZIP packager.  
- **CLI + batch** packaging for CI; container-first deployment [ASSUMPTION: Docker lab image acceptable].  
- Adopt **CIMHub + Powergrid-Models + Blazegraph + CIMantic Graphs** for canonical layer (build only fabric packager + binding pack).

### P1 — Flagship feeder scale-up

- Promote **IEEE 123, 8500, 9500** through same pipeline.  
- **Fabric smoke ingest** for all four feeders.  
- **ADMS smoke** (trace + PF) on promoted bundles.  
- **Tier A artifact registry**: manifest.json, SHACL/structural report, pf-diff-report, checksums.  
- **T0 connectivity + T1 PF-ready** tier labels on published datasets (T2+ operations layers later).

### Explicit non-goals (v1)

| Deferred | Rationale |
|----------|-----------|
| **P4 — GridOS Visual Intelligence** (imagery, inspection overlays) | User directive; only stable mRID/geo hooks in CDPSM GEO profile where already exported |
| **Tier B — partner exports** (CGMES IOP bundles, Oracle workbook, ArcFM GRR, ENTSO-E FAT matrices) | After Tier A stable; avoids dual validation pipelines in v1 |
| **P2+** parameterized feeders (PowerGridSynth), DER-heavy scenario packs, SCADA CSV overlays | Needs canonical path proven |
| **P3** as-operated **DifferenceModel** scenarios, FLISR/outage script packs | Orchestration depth after ingest baseline |
| **P5** partner IOP runbooks | Commercial parity, not GridOS QA blocker |
| **REST API** self-service | CLI/batch first per technical research |
| **Retail SKU / external market** | Internal enabling product |

---

## Who approves what (v1 — plain language)

Question 2 was only about **who says “done”** at each milestone—not job titles like “DRI” or org charts.

| Milestone | What gets approved | Who approves (you name them in the PRD workshop) |
|-----------|-------------------|--------------------------------------------------|
| **P0 done** | “This CDPSM subset and mRID rules are what fabric accepts” | **GridOS platform / fabric engineering** (co-design with Alteia) |
| **P1 done** | “These datasets pass trace + PF smoke on ADMS” | **GridOS ADMS QA** (criteria written together with Alteia) |
| **Build** | Generator, CI artifacts, binding pack YAML | **Alteia engineering** delivers; platform + QA consume |

DERMS and Network Model Orchestration are **consulted** in P0 where the model affects them, but v1 does not require a separate DERMS sign-off gate. If your org needs one, add it in the PRD—otherwise two approvers above are enough.

---

## Risks and Open Questions (GridOS platform co-design)

| Risk / question | Impact | Mitigation or next step |
|-----------------|--------|-------------------------|
| **Fabric binding drift** across GridOS releases | Broken ingest on upgrade | Versioned **binding pack** owned with platform release train |
| **Non-public fabric ingest API** | Integration guesswork | P0 workshop: confirm **file-based ingest** vs REST; document in PRD |
| **CDPSM subset not agreed** | Rework of all feeders | P0 is spec gate—no P1 promotion without sign-off |
| **No public CDPSM SHACL** (unlike ENTSO-E CGMES) | Weak automated conformance | Co-develop **GridOS subset SHACL** in binding pack |
| **CIM profile mismatch** (CDPSM vs internal fabric) | Silent semantic loss | Tier A validation separate from future Tier B ENTSO-E SHACL |
| **Unrealistic physics** in synthetic params | Unsafe training normalization | OpenDSS gold + GridLAB-D cross-check before ADMS promotion |
| **Scope creep into Visual Intelligence** | Delays network v1 | Non-goal; mRID stability only |
| **Unclear approvers** (many teams, no “done”) | P0/P1 stall | Use two-step table above; record **names** in PRD after P0 kickoff workshop |

**Co-design workshop agenda (recommended P0 week 1):** ingest container model, required CDPSM profiles (FUN/EP/TOPO/CAT/GEO/SSH), mRID/uuid mapping, smoke test definition, artifact registry location.

---

## Vision (post–v1)

**P2–P3:** Parameterized DER-heavy feeders, SCADA point lists, as-built/as-operated **DifferenceModel** scenarios, Network Model Orchestration roundtrip tests, GridOS scenario catalog (FLISR, DERMS constraints).  
**Tier B:** PowSyBl CGMES exports + ENTSO-E SHACL for partner IOP.  
**P4+:** Visual Intelligence asset correlation on stable mRIDs and synthetic geolocation—without blocking network delivery.

---

## Recommended Next Step — PRD

Run **`bmad-prd` create intent** with this brief and `addendum.md` as inputs. The PRD should:

1. Turn P0 workshop outputs into **functional requirements** for binding pack, packager, and validation gate.  
2. Specify **acceptance tests** per IEEE feeder (trace, PF, ingest, CI budgets).  
3. Record **approver names** for P0 (platform) and P1 (ADMS QA) from the workshop.  
4. Lock **interface contracts** (manifest schema, fabric ZIP layout, promotion rules).  
5. Trace **non-goals** to PRD out-of-scope section to prevent Tier B / VI scope creep.

Optional before PRD if UI-heavy lab portal emerges: `bmad-ux` — likely minimal for v1 (CLI/CI primary).

---

*Technical depth: see `addendum.md` in this folder.*
