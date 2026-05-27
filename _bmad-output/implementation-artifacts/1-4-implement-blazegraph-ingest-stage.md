---
baseline_commit: 992cf9b9a593ca454aea5306f90e9e77a950148d
---

# Story 1.4: Implement Blazegraph Ingest Stage

Status: done

## Story

As an **Alteia engineer (Sam)**,
I want combined CDPSM XML loaded into Blazegraph per feeder run,
so that CIMHub roundtrip and SPARQL-based checks can operate on the canonical graph.

## Acceptance Criteria

1. **Given** `ieee13cdpsm.xml` from Story 1.3  
   **When** I run `ingest-blazegraph` for feeder `ieee13`  
   **Then** the graph loads without structural ingest errors

2. **Given** ingest completed  
   **When** a SPARQL health query runs  
   **Then** the expected `Feeder` individual (`49AD8E07-3BF9-A4E2-CB8F-C3722F837B62`) exists

3. **Given** infrastructure failure (Blazegraph unreachable)  
   **When** ingest fails  
   **Then** exit code is 2 with structured logs (NFR-5)

**Traces:** FR-5; NFR-5

## Tasks / Subtasks

- [x] **Blazegraph client** (AC: 1, 2, 3)
  - [x] Add `src/alteia_grid_synth/pipeline/blazegraph.py` — upload XML, SPARQL ASK, URL normalization
  - [x] Add `src/alteia_grid_synth/pipeline/ingest_blazegraph.py` — drop/upload/health check

- [x] **CLI and verify script** (AC: 1, 2)
  - [x] Add Typer command `ingest-blazegraph`
  - [x] Add `scripts/verify-ieee13-ingest-blazegraph.sh`

- [x] **Tests** (AC: 1–2)
  - [x] Add `tests/unit/test_blazegraph.py`
  - [x] Add `tests/integration/test_ingest_blazegraph.py` (skip if Blazegraph down)

## Dev Agent Record

### Agent Model Used

Composer (Cursor agent)

### Completion Notes List

- Ingest uses CIMHub `example.sh` curl upload pattern to `/bigdata/namespace/kb/sparql`.
- Feeder health ASK uses case-insensitive mRID match (Blazegraph stores lowercase UUIDs).

### Verification evidence

- Date: 2026-05-27
- Command: `./scripts/verify-p0-spine.sh`
- Exit code: 0
- Summary: ingest-blazegraph OK; full spine 24 pytest passed.

### File List

- `src/alteia_grid_synth/pipeline/blazegraph.py`
- `src/alteia_grid_synth/pipeline/ingest_blazegraph.py`
- `src/alteia_grid_synth/cli.py`
- `scripts/verify-ieee13-ingest-blazegraph.sh`
- `scripts/verify-p0-spine.sh`
- `tests/unit/test_blazegraph.py`
- `tests/integration/test_ingest_blazegraph.py`

### Senior Developer Review (AI)

**Review outcome:** Approve  
**Review date:** 2026-05-27

**Summary:** AC 1–3 satisfied. XML upload, Feeder SPARQL health check, exit code 2 on infra errors, structured logging.

### Change Log

- 2026-05-27: Story 1.4 — Blazegraph ingest stage, CLI, tests, P0 spine hook.
