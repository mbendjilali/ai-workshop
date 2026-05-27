---
baseline_commit: dba648093e4a9811efc8a659fd8c0ee6d7ff302a
---

# Story 1.2: Check In IEEE 13 OpenDSS Seed with Stable UUID Map

Status: done

<!-- Ultimate context engine analysis completed - comprehensive developer guide created -->

## Story

As an **Alteia engineer (Sam)**,
I want the IEEE 13 OpenDSS master and `uuids.dat` in source control,
so that mRIDs remain stable across pipeline re-runs and CI can detect drift.

## Acceptance Criteria

1. **Given** `feeders/ieee13/Master.dss` and `feeders/ieee13/uuids.dat` exist in the repo  
   **When** I inspect the feeder seed layout  
   **Then** paths match architecture §Structure Patterns (`feeders/ieee13/`)  
   **And** `Master.dss` loads the checked-in map via `uuids file=uuids.dat` (relative path)  
   **And** supporting `IEEE13NodeExtra_BusXY.csv` is present for `BusCoords` in the master

2. **Given** the checked-in `uuids.dat`  
   **When** I parse equipment mRIDs from the file  
   **Then** the feeder circuit mRID is `49AD8E07-3BF9-A4E2-CB8F-C3722F837B62` (GridAPPS-D IEEE13 CDPSM reference)  
   **And** no lines contain real utility/customer identifiers (NFR-3 — synthetic IEEE test feeder only)

3. **Given** OpenDSS (`opendsscmd`) available (host or lab Docker image)  
   **When** I run the mRID stability probe twice without modifying `uuids.dat`  
   **Then** the exported UUID files are byte-identical  
   **And** the documented command is `scripts/verify-ieee13-mrid-stability.sh` (or pytest integration with same logic)

4. **Given** feeder CLI conventions from project-context  
   **When** tooling references this feeder  
   **Then** the short id is `ieee13` (maps to `feeders/ieee13/`, future `ieee13cdpsm.xml`, dataset `ieee13-asbuilt`)

5. **Given** story scope boundary  
   **When** this story is complete  
   **Then** **no** `export-cim100` pipeline module, **no** `work/ieee13/cim/*` automation, and **no** binding pack exist yet (Stories 1.3, 2.1)  
   **And** `feeders/ieee13/README.md` documents upstream provenance (GRIDAPPSD/Powergrid-Models IEEE13_CDPSM)

**Traces:** FR-4 (precondition); NFR-2, NFR-3

## Tasks / Subtasks

- [x] **Check in IEEE 13 OpenDSS seed files** (AC: 1, 4, 5)
  - [x] Add `feeders/ieee13/Master.dss` from Powergrid-Models `IEEE13_CDPSM.dss` with `uuids file=uuids.dat` before export-oriented commands
  - [x] Add `feeders/ieee13/uuids.dat` from upstream `ieee13_uuids.dat` (rename per architecture)
  - [x] Add `feeders/ieee13/IEEE13NodeExtra_BusXY.csv` (required by `BusCoords` in master)
  - [x] Add `feeders/ieee13/README.md` with provenance, license note, and CIM export placeholder params for Story 1.3

- [x] **mRID stability verification** (AC: 2, 3)
  - [x] Add `src/alteia_grid_synth/feeders/uuid_map.py` — parse/compare OpenDSS `uuids.dat` format
  - [x] Add `feeders/ieee13/mrid_stability.dss` — OpenDSS script: two `export uuids` passes to `work/ieee13/_mrid_probe_{1,2}.dat`
  - [x] Add `scripts/verify-ieee13-mrid-stability.sh` — runs probe via Docker lab image or host `opendsscmd`
  - [x] Add `tests/unit/test_uuid_map.py` — parser + golden circuit mRID
  - [x] Add `tests/integration/test_ieee13_seed.py` — layout + stability (skip if no OpenDSS)

- [x] **Documentation touch-up** (AC: 4)
  - [x] Update root `README.md` feeder seed section pointing to `feeders/ieee13/` and stability script

## Dev Notes

### Epic Context (Epic 1)

Story 1.1 delivered Docker lab image + Typer stub. **This story adds the IEEE 13 spine input** required by Story 1.3 (`export-cim100`).

| Story | Scope |
|-------|-------|
| **1.2** (this) | `feeders/ieee13/*` + mRID stability probe |
| 1.3 | `export-cim100` → `work/ieee13/cim/ieee13cdpsm.xml` |

### Upstream Source (mandatory provenance)

Seed content is derived from [GRIDAPPSD/Powergrid-Models](https://github.com/GRIDAPPSD/Powergrid-Models) tag `master`:

| Upstream path | Repo path |
|---------------|-----------|
| `models/feeders/OpenDSS/IEEE/IEEE13_CDPSM/IEEE13_CDPSM.dss` | `feeders/ieee13/Master.dss` |
| `models/feeders/OpenDSS/IEEE/IEEE13_CDPSM/ieee13_uuids.dat` | `feeders/ieee13/uuids.dat` |
| `models/feeders/OpenDSS/IEEE/IEEE13_CDPSM/IEEE13NodeExtra_BusXY.csv` | same name |

`convert.json` from upstream documents CIM export mRIDs for Story 1.3:

- `feeder`: `49AD8E07-3BF9-A4E2-CB8F-C3722F837B62`
- `substation`: `6C62C905-6FC7-653D-9F1E-1340F974A587`
- `geo_region` / `sub_geo_region`: see README in feeder folder

### Architecture Compliance

- Feeder CLI arg: `ieee13` (short id)
- CIM output file (later): `ieee13cdpsm.xml`
- Dataset id (later): `ieee13-asbuilt`
- mRID stability: checked-in `uuids.dat`; re-export without map change → identical mRID set (NFR-2)

### Previous Story Intelligence (1.1)

- Lab image: `alteia-grid-synth:lab` from `docker/Dockerfile` (CIMHub 1.1.0 base) includes `opendsscmd` on PATH.
- Verification pattern: `scripts/verify-lab-image.sh` — mirror for ieee13 mRID script.
- Docker may be unavailable on dev host; tests must **skip** OpenDSS integration when `opendsscmd` missing, not fail the suite.

### Testing Requirements

| Check | Type | Pass criteria |
|-------|------|---------------|
| Seed files exist | Unit | paths + `uuids file=` in Master.dss |
| Parser | Unit | known circuit mRID; ≥ 40 equipment UUIDs |
| NFR-3 scan | Unit | no forbidden patterns in seed text |
| mRID stability | Integration (optional) | probe outputs byte-equal |

### Project Context Reference

- Read `_bmad-output/project-context.md` — mRID stability, naming, NFR-3, no utility IDs
- Do not hard-code registry URLs or workshop literals

### References

- [Source: _bmad-output/planning-artifacts/epics.md § Story 1.2]
- [Source: _bmad-output/planning-artifacts/architecture.md § Structure Patterns, mRID stability]
- [Source: GRIDAPPSD/Powergrid-Models IEEE13_CDPSM]
- [Source: GRIDAPPSD/CIMHub example/cim_test.dss — export uuids / cim100 pattern]

## Dev Agent Record

### Agent Model Used

Composer (Cursor agent)

### Debug Log References

- Seed imported from GRIDAPPSD/Powergrid-Models `IEEE13_CDPSM` (2026-05-27).
- `sg docker -c ./scripts/verify-ieee13-mrid-stability.sh` → byte-identical exports (29439 bytes); OpenDSS stderr re Documents dir is benign in container.
- Pytest integration `@pytest.mark.opendss` skips when user not in `docker` group and `opendsscmd` absent on host.

### Completion Notes List

- Checked in IEEE 13 CDPSM OpenDSS seed under `feeders/ieee13/` with architecture naming (`Master.dss`, `uuids.dat`).
- Added `uuids file=uuids.dat` to master after solve for NFR-2 stability.
- Implemented `uuid_map.py` parser, mRID stability DSS probe, shell verifier (host or Docker), and unit/integration tests.
- Verified mRID stability via Docker lab image; 8 unit tests pass (including subset guard when probe artifacts present).

### File List

- `feeders/ieee13/Master.dss`
- `feeders/ieee13/uuids.dat`
- `feeders/ieee13/IEEE13NodeExtra_BusXY.csv`
- `feeders/ieee13/README.md`
- `feeders/ieee13/mrid_stability.dss`
- `src/alteia_grid_synth/feeders/__init__.py`
- `src/alteia_grid_synth/feeders/uuid_map.py`
- `scripts/verify-ieee13-mrid-stability.sh`
- `tests/unit/test_uuid_map.py`
- `tests/integration/test_ieee13_seed.py`
- `README.md`
- `pyproject.toml`

### Senior Developer Review (AI)

**Review outcome:** Approve  
**Review date:** 2026-05-27

**Summary:** All AC satisfied. Seed provenance documented; mRID probe byte-stable in Docker lab image; scope excludes export-cim100 and binding pack.

### Review Findings

- [x] [Review][Defer] OpenDSS stderr about `OpenDSSCmd` Documents directory in container — does not affect probe outputs; harden Dockerfile env in later story if noisy in CI logs
- [x] [Review][Dismiss] Integration tests skip without `docker` group membership — acceptable; shell script is canonical verifier per AC 3

### Change Log

- 2026-05-27: Story 1.2 — IEEE 13 OpenDSS seed, uuids.dat, mRID stability probe and tests.
- 2026-05-27: Code review approved — AC 1–5 satisfied; mRID probe verified in Docker lab image.
