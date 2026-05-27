---
baseline_commit: 992cf9b9a593ca454aea5306f90e9e77a950148d
---

# Story 1.6: Implement CIMHub PF vs OpenDSS Gold Comparison

Status: done

## Story

As an **Alteia engineer (Sam)**,
I want CIMHub roundtrip PF compared against OpenDSS gold with recorded max ΔV,
so that physics agreement is verified before validation gate integration.

## Acceptance Criteria

1. **Given** IEEE 13 gold OpenDSS seed and CIMHub roundtrip outputs  
   **When** I run the PF comparison stage (`pf-diff`)  
   **Then** max voltage magnitude delta ≤ 0.1% (AT-13-2, FR-6)

2. **Given** PF comparison completes  
   **When** I read the report  
   **Then** `work/ieee13/validation/pf-diff-report.json` matches architecture schema

3. **Given** tolerance exceedance  
   **When** PF comparison runs  
   **Then** non-zero exit (code 1) suitable for CI failure

**Traces:** FR-6; AT-13-2

## Tasks / Subtasks

- [x] **Binding pack PF tolerance** (AC: 1)
  - [x] Extend `config/gridos-binding-pack.yaml` with `pf_tolerances.vm_delta_pct_max: 0.1`
  - [x] Load tolerance in `binding_pack.py`

- [x] **PF diff module** (AC: 1–3)
  - [x] Add `src/alteia_grid_synth/pipeline/pf_diff.py` — phase-level pu compare, CIMHub-style solve (`controlmode=off`)
  - [x] Add Typer command `pf-diff`
  - [x] Add `scripts/verify-ieee13-pf-diff.sh`

- [x] **Tests** (AC: 1)
  - [x] Add `tests/unit/test_pf_diff.py`

## Dev Agent Record

### Agent Model Used

Composer (Cursor agent)

### Completion Notes List

- Phase-level per-unit comparison (`BUS_A` keys) matches CIMHub Compare_Cases convention; bus-aggregate compare overstated delta (~1.5%).
- Observed `vm_delta_pct_max=0.009858` on IEEE 13 (pass).

### Verification evidence

- Date: 2026-05-27
- Command: `./scripts/verify-p0-spine.sh`
- Exit code: 0
- Summary: pf-diff pass; report at `work/ieee13/validation/pf-diff-report.json`; 24 pytest passed.

### File List

- `config/gridos-binding-pack.yaml`
- `src/alteia_grid_synth/config/binding_pack.py`
- `src/alteia_grid_synth/pipeline/pf_diff.py`
- `src/alteia_grid_synth/cli.py`
- `scripts/verify-ieee13-pf-diff.sh`
- `scripts/verify-p0-spine.sh`
- `tests/unit/test_pf_diff.py`

### Senior Developer Review (AI)

**Review outcome:** Approve  
**Review date:** 2026-05-27

**Summary:** AC 1–3 satisfied. Phase-level ΔV, binding-pack tolerance, pf-diff-report.json, exit 1 on exceedance.

### Change Log

- 2026-05-27: Story 1.6 — PF diff stage, report schema, P0 spine extension.
