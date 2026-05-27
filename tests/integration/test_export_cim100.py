"""Integration tests for export-cim100 stage."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from alteia_grid_synth.config.binding_pack import load_binding_pack, repo_root
from alteia_grid_synth.pipeline.cim_xml import validate_combined_cdpsm_xml
from alteia_grid_synth.pipeline.export_cim100 import (
    compare_reexport_mrids,
    resolve_paths,
    run_export,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify-ieee13-export-cim100.sh"


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
def test_export_cim100_produces_valid_xml():
    pack = load_binding_pack()
    out = run_export("ieee13")
    assert out == repo_root() / "work" / "ieee13" / "cim" / "ieee13cdpsm.xml"
    mrids = validate_combined_cdpsm_xml(
        out,
        cim_namespace=pack.cim_namespace,
        profiles_required=pack.profiles_required,
    )
    assert len(mrids) >= 10


@pytest.mark.skipif(not _opendss_available(), reason="OpenDSS (host or Docker) not available")
@pytest.mark.opendss
def test_reexport_mrids_are_stable():
    compare_reexport_mrids("ieee13")


@pytest.mark.skipif(not _opendss_available(), reason="OpenDSS (host or Docker) not available")
@pytest.mark.opendss
def test_verify_script_exits_zero():
    result = subprocess.run(
        [str(VERIFY_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_resolve_paths_ieee13():
    paths = resolve_paths("ieee13", REPO_ROOT)
    assert paths.output_xml.name == "ieee13cdpsm.xml"
    assert paths.uuids_dat.is_file()
