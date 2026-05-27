"""Blazegraph SPARQL client for CDPSM ingest and health checks."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from alteia_grid_synth.config.binding_pack import repo_root

logger = logging.getLogger(__name__)

DEFAULT_SPARQL_URL = "http://localhost:8889/bigdata/namespace/kb/sparql"


class BlazegraphInfraError(Exception):
    """Infrastructure failure (exit code 2)."""


class BlazegraphValidationError(Exception):
    """Validation failure (exit code 1)."""


@dataclass(frozen=True)
class BlazegraphConfig:
    sparql_url: str


def normalize_sparql_url(url: str) -> str:
    """Ensure CIMHub-compatible KB namespace endpoint."""
    trimmed = url.rstrip("/")
    if trimmed.endswith("/bigdata/sparql") and "/namespace/" not in trimmed:
        return trimmed.replace("/bigdata/sparql", "/bigdata/namespace/kb/sparql")
    return trimmed


def resolve_sparql_url() -> str:
    """Resolve SPARQL endpoint from env or default host URL."""
    raw = os.environ.get("BLAZEGRAPH_SPARQL_URL", DEFAULT_SPARQL_URL)
    return normalize_sparql_url(raw)


def load_config() -> BlazegraphConfig:
    return BlazegraphConfig(sparql_url=resolve_sparql_url())


def _request(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 120.0,
) -> bytes:
    req = urllib.request.Request(url, data=data, method=method)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.URLError as exc:
        raise BlazegraphInfraError(f"Blazegraph request failed: {exc}") from exc


def drop_all(config: BlazegraphConfig | None = None) -> None:
    """Clear the default KB namespace (feeder-scoped runs start fresh)."""
    cfg = config or load_config()
    body = urllib.parse.urlencode({"update": "drop all"}).encode("utf-8")
    _request(
        cfg.sparql_url,
        method="POST",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    logger.info("blazegraph_drop_all url=%s", cfg.sparql_url)


def upload_cim_xml(xml_path: Path, config: BlazegraphConfig | None = None) -> None:
    """POST combined CDPSM XML to Blazegraph (CIMHub example.sh pattern)."""
    cfg = config or load_config()
    if not xml_path.is_file():
        raise BlazegraphValidationError(f"CIM XML missing: {xml_path}")

    payload = xml_path.read_bytes()
    _request(
        cfg.sparql_url,
        method="POST",
        data=payload,
        headers={"Content-Type": "application/xml"},
    )
    logger.info(
        "blazegraph_upload xml=%s bytes=%d url=%s",
        xml_path,
        len(payload),
        cfg.sparql_url,
    )


def sparql_query(query: str, config: BlazegraphConfig | None = None) -> dict[str, Any]:
    """Run a SPARQL SELECT/ASK query; return JSON bindings."""
    cfg = config or load_config()
    body = urllib.parse.urlencode({"query": query}).encode("utf-8")
    raw = _request(
        cfg.sparql_url,
        method="POST",
        data=body,
        headers={
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise BlazegraphInfraError(f"Invalid SPARQL JSON response: {raw[:200]!r}") from exc


def feeder_exists(
    feeder_mrid: str,
    cim_namespace: str,
    *,
    config: BlazegraphConfig | None = None,
) -> bool:
    """ASK whether a Feeder individual with *feeder_mrid* exists in the graph."""
    cfg = config or load_config()
    mrid = feeder_mrid.lower()
    ns = cim_namespace.rstrip("#")
    query = f"""
PREFIX cim: <{ns}#>
ASK {{
  ?feeder a cim:Feeder .
  FILTER(CONTAINS(LCASE(STR(?feeder)), "{mrid}"))
}}
"""
    result = sparql_query(query, cfg)
    return bool(result.get("boolean"))


def cim_xml_path(feeder_id: str, root: Path | None = None) -> Path:
    base = repo_root(root) if root is None else root.resolve()
    return base / "work" / feeder_id / "cim" / f"{feeder_id}cdpsm.xml"
