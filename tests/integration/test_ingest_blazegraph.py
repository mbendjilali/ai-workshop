"""Integration tests for ingest-blazegraph (requires Blazegraph)."""

from __future__ import annotations

import os
import shutil
import urllib.error
import urllib.request

import pytest

from alteia_grid_synth.pipeline.export_cim100 import run_export
from alteia_grid_synth.pipeline.ingest_blazegraph import run_ingest


def _blazegraph_available() -> bool:
    url = os.environ.get(
        "BLAZEGRAPH_SPARQL_URL",
        "http://localhost:8889/bigdata/namespace/kb/sparql",
    ).replace("/sparql", "/status").replace("/namespace/kb/status", "/status")
    if not url.endswith("/status"):
        url = "http://localhost:8889/bigdata/status"
    try:
        with urllib.request.urlopen(url, timeout=3):
            return True
    except (urllib.error.URLError, OSError):
        return False


pytestmark = pytest.mark.skipif(
    not _blazegraph_available(),
    reason="Blazegraph not reachable",
)


def test_ingest_blazegraph_ieee13():
    if not shutil.which("opendsscmd") and not shutil.which("docker"):
        pytest.skip("OpenDSS unavailable for export pre-step")
    run_export("ieee13", skip_opendss=not shutil.which("opendsscmd"))
    run_ingest("ieee13")
