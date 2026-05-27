"""Integration checks for IEEE 13 feeder seed and mRID stability."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from alteia_grid_synth.feeders.uuid_map import compare_uuid_exports

REPO_ROOT = Path(__file__).resolve().parents[2]
FEEDER_DIR = REPO_ROOT / "feeders" / "ieee13"
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify-ieee13-mrid-stability.sh"

pytestmark_opendss = pytest.mark.opendss


def _opendss_available() -> bool:
    if shutil.which("opendsscmd"):
        return True
    if not shutil.which("docker"):
        return False
    try:
        subprocess.run(
            ["docker", "info"],
            capture_output=True,
            check=True,
            timeout=10,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.mark.skipif(not _opendss_available(), reason="OpenDSS (host or Docker) not available")
@pytest.mark.opendss
def test_mrid_stability_script_exits_zero():
    result = subprocess.run(
        [str(VERIFY_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr or result.stdout


@pytest.mark.skipif(not _opendss_available(), reason="OpenDSS (host or Docker) not available")
@pytest.mark.opendss
def test_mrid_probe_exports_are_identical_sets():
    """AC: re-export without uuid map change → identical mRID set (pairwise)."""
    work = FEEDER_DIR / "work"
    out1 = work / "_mrid_probe_1.dat"
    out2 = work / "_mrid_probe_2.dat"
    if not out1.is_file() or not out2.is_file():
        subprocess.run([str(VERIFY_SCRIPT)], cwd=REPO_ROOT, check=True, timeout=120)
    compare_uuid_exports(out1, out2)
