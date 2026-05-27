"""OpenDSS export cim100 pipeline stage."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from alteia_grid_synth.config.binding_pack import BindingPack, load_binding_pack, repo_root
from alteia_grid_synth.feeders.uuid_map import IEEE13_CIRCUIT_MRID
from alteia_grid_synth.pipeline.cim_xml import validate_combined_cdpsm_xml

SUPPORTED_FEEDERS = frozenset({"ieee13"})


class ExportCim100Error(Exception):
    """Validation failure (exit code 1)."""


class ExportCim100InfraError(Exception):
    """Infrastructure failure (exit code 2)."""


@dataclass(frozen=True)
class ExportPaths:
    feeder_id: str
    feeder_dir: Path
    work_cim_dir: Path
    output_xml: Path
    uuids_dat: Path
    dss_script: Path


def resolve_paths(feeder_id: str, root: Path | None = None) -> ExportPaths:
    if feeder_id not in SUPPORTED_FEEDERS:
        raise ExportCim100Error(f"Unsupported feeder: {feeder_id!r}")

    base = repo_root(root) if root is None else root.resolve()
    feeder_dir = base / "feeders" / feeder_id
    if not feeder_dir.is_dir():
        raise ExportCim100Error(f"Feeder directory missing: {feeder_dir}")

    work_cim_dir = base / "work" / feeder_id / "cim"
    return ExportPaths(
        feeder_id=feeder_id,
        feeder_dir=feeder_dir,
        work_cim_dir=work_cim_dir,
        output_xml=work_cim_dir / f"{feeder_id}cdpsm.xml",
        uuids_dat=feeder_dir / "uuids.dat",
        dss_script=feeder_dir / "export_cim100.dss",
    )


def _find_opendsscmd() -> str | None:
    return shutil.which("opendsscmd")


def run_opendss_export(paths: ExportPaths, *, image: str | None = None) -> None:
    """Execute feeders/{feeder}/export_cim100.dss via host or Docker lab image."""
    if not paths.dss_script.is_file():
        raise ExportCim100InfraError(f"OpenDSS script missing: {paths.dss_script}")

    paths.work_cim_dir.mkdir(parents=True, exist_ok=True)

    cmd = _find_opendsscmd()
    if cmd:
        subprocess.run(
            [cmd, paths.dss_script.name],
            cwd=paths.feeder_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        return

    docker = shutil.which("docker")
    if not docker:
        raise ExportCim100InfraError(
            "opendsscmd not on PATH and Docker unavailable"
        )

    lab_image = image or "alteia-grid-synth:lab"
    root = repo_root(paths.feeder_dir)
    subprocess.run(
        [
            docker,
            "run",
            "--rm",
            "-u",
            f"{os.getuid()}:{os.getgid()}",
            "-v",
            f"{root}:/app",
            "-w",
            f"/app/feeders/{paths.feeder_id}",
            lab_image,
            "opendsscmd",
            paths.dss_script.name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


# CIM container mRIDs passed to export cim100 (feeders/ieee13/README.md).
_IEEE13_CIM_ANCHOR_MRIDS = (
    IEEE13_CIRCUIT_MRID,
    "6C62C905-6FC7-653D-9F1E-1340F974A587",
    "73C512BD-7249-4F50-50DA-D93849B89C43",
    "ABEB635F-729D-24BF-B8A4-E2EF268D8B9E",
)


def assert_anchor_mrids_in_xml(xml_mrids: frozenset[str]) -> None:
    """Feeder/geo container mRIDs from export parameters must appear in XML."""
    missing = [m for m in _IEEE13_CIM_ANCHOR_MRIDS if m.upper() not in xml_mrids]
    if missing:
        raise ExportCim100Error(
            f"CIM anchor mRID(s) missing in export: {missing}"
        )


def run_export(
    feeder_id: str = "ieee13",
    *,
    binding_pack: BindingPack | None = None,
    docker_image: str | None = None,
    skip_opendss: bool = False,
) -> Path:
    """
    Run export-cim100 for *feeder_id* and validate the combined CDPSM XML.

    Returns path to ``work/{feeder}/cim/{feeder}cdpsm.xml``.
    """
    pack = binding_pack or load_binding_pack()
    paths = resolve_paths(feeder_id)

    if not skip_opendss:
        try:
            run_opendss_export(paths, image=docker_image)
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr or exc.stdout or str(exc)
            raise ExportCim100InfraError(
                f"OpenDSS export failed: {stderr}"
            ) from exc

    try:
        xml_mrids = validate_combined_cdpsm_xml(
            paths.output_xml,
            cim_namespace=pack.cim_namespace,
            profiles_required=pack.profiles_required,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise ExportCim100Error(str(exc)) from exc

    assert_anchor_mrids_in_xml(xml_mrids)
    return paths.output_xml


def compare_reexport_mrids(feeder_id: str = "ieee13") -> None:
    """Run export twice; assert identical mRID sets (NFR-2)."""
    pack = load_binding_pack()
    paths = resolve_paths(feeder_id)
    probe_dir = paths.work_cim_dir / "_reexport_probe"
    probe_dir.mkdir(parents=True, exist_ok=True)

    sets: list[frozenset[str]] = []
    for idx in (1, 2):
        dest = probe_dir / f"export_{idx}.xml"
        if dest.exists():
            dest.unlink()
        run_export(feeder_id, binding_pack=pack)
        shutil.copy2(paths.output_xml, dest)
        sets.append(
            validate_combined_cdpsm_xml(
                dest,
                cim_namespace=pack.cim_namespace,
                profiles_required=pack.profiles_required,
            )
        )

    if sets[0] != sets[1]:
        raise ExportCim100Error(
            "Re-export mRID sets differ "
            f"(only in first: {len(sets[0] - sets[1])}, "
            f"only in second: {len(sets[1] - sets[0])})"
        )
