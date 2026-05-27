"""CIMHub JAR subprocess wrapper."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

CIMHUB_JAR = Path(os.environ.get("CIMHUB_JAR", "/opt/cimhub/releases/cimhub-1.1.0.jar"))
CIMHUB_MAIN = "gov.pnnl.gridappsd.cimhub.CIMImporter"


class CimhubInfraError(Exception):
    """Infrastructure failure (exit code 2)."""


class CimhubValidationError(Exception):
    """Validation failure (exit code 1)."""


@dataclass(frozen=True)
class CimhubConfig:
    jar_path: Path
    sparql_url: str


def default_config() -> CimhubConfig:
    from alteia_grid_synth.pipeline.blazegraph import resolve_sparql_url

    return CimhubConfig(jar_path=CIMHUB_JAR, sparql_url=resolve_sparql_url())


def run_cim_importer(
    *args: str,
    config: CimhubConfig | None = None,
    timeout: float = 600.0,
) -> subprocess.CompletedProcess[str]:
    """Invoke ``java -cp cimhub.jar CIMImporter`` with given arguments."""
    cfg = config or default_config()
    if not cfg.jar_path.is_file():
        raise CimhubInfraError(f"CIMHub JAR missing: {cfg.jar_path}")

    cmd = [
        "java",
        "-cp",
        str(cfg.jar_path),
        CIMHUB_MAIN,
        *args,
    ]
    try:
        return subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise CimhubInfraError("java not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise CimhubInfraError(f"CIMImporter timed out after {timeout}s") from exc


def require_success(result: subprocess.CompletedProcess[str], *, stage: str) -> None:
    if result.returncode == 0:
        return
    detail = (result.stderr or result.stdout or "").strip()
    raise CimhubValidationError(
        f"{stage} failed (exit {result.returncode}): {detail[-2000:]}"
    )
