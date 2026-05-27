"""CIMHub roundtrip to OpenDSS and GridLAB-D render mirrors."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from alteia_grid_synth.config.binding_pack import repo_root
from alteia_grid_synth.feeders.uuid_map import IEEE13_CIRCUIT_MRID
from alteia_grid_synth.pipeline.cimhub_client import (
    CimhubInfraError,
    CimhubValidationError,
    default_config,
    require_success,
    run_cim_importer,
)

logger = logging.getLogger(__name__)

SUPPORTED_FEEDERS = frozenset({"ieee13"})

_FEEDER_MRIDS = {
    "ieee13": IEEE13_CIRCUIT_MRID,
}


class CimhubRoundtripError(Exception):
    """Validation failure (exit code 1)."""


class CimhubRoundtripInfraError(Exception):
    """Infrastructure failure (exit code 2)."""


@dataclass(frozen=True)
class RoundtripPaths:
    feeder_id: str
    render_root: Path
    opendss_dir: Path
    gridlabd_dir: Path


def resolve_paths(feeder_id: str, root: Path | None = None) -> RoundtripPaths:
    if feeder_id not in SUPPORTED_FEEDERS:
        raise CimhubRoundtripError(f"Unsupported feeder: {feeder_id!r}")
    base = repo_root(root) if root is None else root.resolve()
    render_root = base / "work" / feeder_id / "render"
    return RoundtripPaths(
        feeder_id=feeder_id,
        render_root=render_root,
        opendss_dir=render_root / "opendss",
        gridlabd_dir=render_root / "gridlabd",
    )


def _assert_render_outputs(paths: RoundtripPaths) -> None:
    dss_files = list(paths.opendss_dir.glob("*.dss"))
    glm_files = list(paths.gridlabd_dir.glob("*.glm"))
    if not dss_files:
        raise CimhubRoundtripError(
            f"No OpenDSS .dss files under {paths.opendss_dir}"
        )
    if not glm_files:
        raise CimhubRoundtripError(
            f"No GridLAB-D .glm files under {paths.gridlabd_dir}"
        )
    logger.info(
        "roundtrip_outputs dss=%d glm=%d opendss=%s gridlabd=%s",
        len(dss_files),
        len(glm_files),
        paths.opendss_dir,
        paths.gridlabd_dir,
    )


def run_roundtrip(
    feeder_id: str = "ieee13",
    *,
    root: Path | None = None,
    load_scale: float = 1.0,
) -> RoundtripPaths:
    """
    Run CIMHub ``CIMImporter -o=both`` into ``work/{feeder}/render/``.

    Expects CDPSM already loaded in Blazegraph (Story 1.4).
    """
    paths = resolve_paths(feeder_id, root)
    feeder_mrid = _FEEDER_MRIDS[feeder_id]
    cfg = default_config()

    paths.opendss_dir.mkdir(parents=True, exist_ok=True)
    paths.gridlabd_dir.mkdir(parents=True, exist_ok=True)

    # CIMHub writes {prefix}_base.dss/.glm into the parent of this leaf directory.
    export_leaf = paths.opendss_dir / feeder_id
    if export_leaf.exists():
        shutil.rmtree(export_leaf)
    export_leaf.mkdir(parents=True, exist_ok=True)

    try:
        idx = run_cim_importer(
            f"-u={cfg.sparql_url}",
            "-o=idx",
            str(paths.render_root / "_idx"),
            config=cfg,
        )
        require_success(idx, stage="CIMImporter idx (structural index)")

        result = run_cim_importer(
            f"-s={feeder_mrid}",
            f"-u={cfg.sparql_url}",
            "-o=both",
            f"-l={load_scale}",
            "-i=1",
            "-h=0",
            "-x=0",
            "-t=1",
            str(export_leaf),
            config=cfg,
        )
        require_success(result, stage="CIMImporter roundtrip")
    except CimhubValidationError as exc:
        raise CimhubRoundtripError(str(exc)) from exc
    except CimhubInfraError as exc:
        raise CimhubRoundtripInfraError(str(exc)) from exc

    for glm in paths.opendss_dir.glob("*.glm"):
        target = paths.gridlabd_dir / glm.name
        if not target.exists():
            shutil.copy2(glm, target)

    _assert_render_outputs(paths)
    logger.info("cimhub_roundtrip_ok feeder=%s mrid=%s", feeder_id, feeder_mrid)
    return paths
