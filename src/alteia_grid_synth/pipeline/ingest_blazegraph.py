"""Load combined CDPSM XML into Blazegraph."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from alteia_grid_synth.config.binding_pack import BindingPack, load_binding_pack, repo_root
from alteia_grid_synth.feeders.uuid_map import IEEE13_CIRCUIT_MRID
from alteia_grid_synth.pipeline.blazegraph import (
    BlazegraphInfraError,
    BlazegraphValidationError,
    cim_xml_path,
    drop_all,
    feeder_exists,
    load_config,
    upload_cim_xml,
)

logger = logging.getLogger(__name__)

SUPPORTED_FEEDERS = frozenset({"ieee13"})

_FEEDER_MRIDS = {
    "ieee13": IEEE13_CIRCUIT_MRID,
}


class IngestBlazegraphError(Exception):
    """Validation failure (exit code 1)."""


class IngestBlazegraphInfraError(Exception):
    """Infrastructure failure (exit code 2)."""


@dataclass(frozen=True)
class IngestPaths:
    feeder_id: str
    cim_xml: Path


def resolve_paths(feeder_id: str, root: Path | None = None) -> IngestPaths:
    if feeder_id not in SUPPORTED_FEEDERS:
        raise IngestBlazegraphError(f"Unsupported feeder: {feeder_id!r}")
    xml = cim_xml_path(feeder_id, root)
    if not xml.is_file():
        raise IngestBlazegraphError(
            f"Combined CDPSM XML missing: {xml} (run export-cim100 first)"
        )
    return IngestPaths(feeder_id=feeder_id, cim_xml=xml)


def run_ingest(
    feeder_id: str = "ieee13",
    *,
    binding_pack: BindingPack | None = None,
    clear_namespace: bool = True,
    root: Path | None = None,
) -> None:
    """
    Ingest ``work/{feeder}/cim/{feeder}cdpsm.xml`` into Blazegraph.

    Validates Feeder individual via SPARQL health query.
    """
    pack = binding_pack or load_binding_pack()
    paths = resolve_paths(feeder_id, root)
    feeder_mrid = _FEEDER_MRIDS[feeder_id]
    cfg = load_config()

    try:
        if clear_namespace:
            drop_all(cfg)
        upload_cim_xml(paths.cim_xml, cfg)
        if not feeder_exists(feeder_mrid, pack.cim_namespace, config=cfg):
            raise IngestBlazegraphError(
                f"Feeder mRID {feeder_mrid} not found after ingest"
            )
    except BlazegraphValidationError as exc:
        raise IngestBlazegraphError(str(exc)) from exc
    except BlazegraphInfraError as exc:
        raise IngestBlazegraphInfraError(str(exc)) from exc

    logger.info(
        "ingest_blazegraph_ok feeder=%s mrid=%s xml=%s sparql=%s",
        feeder_id,
        feeder_mrid,
        paths.cim_xml,
        cfg.sparql_url,
    )
