"""Unit tests for OpenDSS uuid map parsing."""

from pathlib import Path

import pytest

from alteia_grid_synth.feeders.uuid_map import (
    IEEE13_CIRCUIT_MRID,
    assert_no_forbidden_identifiers,
    mrid_set,
    parse_uuids_dat,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
IEEE13_DIR = REPO_ROOT / "feeders" / "ieee13"


def test_ieee13_seed_files_exist():
    assert (IEEE13_DIR / "Master.dss").is_file()
    assert (IEEE13_DIR / "uuids.dat").is_file()
    assert (IEEE13_DIR / "IEEE13NodeExtra_BusXY.csv").is_file()


def test_master_dss_loads_checked_in_uuid_map():
    master = (IEEE13_DIR / "Master.dss").read_text(encoding="utf-8")
    assert "uuids file=uuids.dat" in master.lower()


def test_uuids_dat_parses_circuit_mrid():
    entries = parse_uuids_dat(IEEE13_DIR / "uuids.dat")
    assert entries.get("circuit.ieee13nodeckt") == IEEE13_CIRCUIT_MRID
    assert len(entries) >= 40


def test_uuids_dat_mrid_set_size():
    mrids = mrid_set(IEEE13_DIR / "uuids.dat")
    assert len(mrids) >= 40


def test_seed_has_no_forbidden_identifier_patterns():
    assert_no_forbidden_identifiers(
        IEEE13_DIR / "Master.dss",
        IEEE13_DIR / "uuids.dat",
        IEEE13_DIR / "IEEE13NodeExtra_BusXY.csv",
    )


def test_exported_mrids_subset_of_checked_in_map_when_probe_exists():
    """OpenDSS export must not invent mRIDs outside the checked-in map."""
    probe = IEEE13_DIR / "work" / "_mrid_probe_1.dat"
    if not probe.is_file():
        pytest.skip("mRID probe not run — execute scripts/verify-ieee13-mrid-stability.sh")
    baseline = mrid_set(IEEE13_DIR / "uuids.dat")
    exported = mrid_set(probe)
    assert exported <= baseline
