"""Unit tests for Blazegraph helpers."""

from __future__ import annotations

from alteia_grid_synth.pipeline.blazegraph import normalize_sparql_url


def test_normalize_sparql_url_adds_kb_namespace() -> None:
    url = "http://localhost:8889/bigdata/sparql"
    assert (
        normalize_sparql_url(url)
        == "http://localhost:8889/bigdata/namespace/kb/sparql"
    )


def test_normalize_sparql_url_preserves_kb_path() -> None:
    url = "http://blazegraph:8080/bigdata/namespace/kb/sparql"
    assert normalize_sparql_url(url) == url
