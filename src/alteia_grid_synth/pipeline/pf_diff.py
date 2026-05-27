"""Compare OpenDSS gold PF vs CIMHub roundtrip OpenDSS mirror."""

from __future__ import annotations

import csv
import json
import logging
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from alteia_grid_synth.config.binding_pack import BindingPack, load_binding_pack, repo_root

logger = logging.getLogger(__name__)

SUPPORTED_FEEDERS = frozenset({"ieee13"})


class PfDiffError(Exception):
    """Validation failure (exit code 1)."""


class PfDiffInfraError(Exception):
    """Infrastructure failure (exit code 2)."""


@dataclass(frozen=True)
class PfDiffPaths:
    feeder_id: str
    gold_master: Path
    roundtrip_dss_dir: Path
    report_path: Path


@dataclass(frozen=True)
class PfMetrics:
    vm_delta_pct_max: float
    compared_nodes: int


def resolve_paths(feeder_id: str, root: Path | None = None) -> PfDiffPaths:
    if feeder_id not in SUPPORTED_FEEDERS:
        raise PfDiffError(f"Unsupported feeder: {feeder_id!r}")
    base = repo_root(root) if root is None else root.resolve()
    return PfDiffPaths(
        feeder_id=feeder_id,
        gold_master=base / "feeders" / feeder_id / "Master.dss",
        roundtrip_dss_dir=base / "work" / feeder_id / "render" / "opendss",
        report_path=base / "work" / feeder_id / "validation" / "pf-diff-report.json",
    )


def _find_opendsscmd() -> str:
    cmd = shutil.which("opendsscmd")
    if not cmd:
        raise PfDiffInfraError("opendsscmd not on PATH")
    return cmd


def _pick_roundtrip_master(dss_dir: Path) -> Path:
    if not dss_dir.is_dir():
        raise PfDiffError(f"Roundtrip OpenDSS dir missing: {dss_dir}")
    candidates = sorted(dss_dir.glob("*.dss"))
    if not candidates:
        raise PfDiffError(f"No .dss files in {dss_dir}")
    # Prefer CIMHub roundtrip master (often largest / named like IEEE13*.dss)
    candidates.sort(key=lambda p: (-p.stat().st_size, p.name))
    return candidates[0]


def _write_solve_script(master: Path, voltages_csv: Path) -> Path:
    """Write a DSS script beside *master* so relative redirects resolve."""
    script_path = master.parent / f"_pf_solve_{master.stem}.dss"
    script_path.write_text(
        f'clear\nredirect "{master.name}"\n'
        f"set maxiterations=80\nset controlmode=off\n"
        f"Set mode=Snapshot\nSolve\n"
        f'export voltages file="{voltages_csv.resolve()}"\n',
        encoding="utf-8",
    )
    return script_path


def _run_opendss(script: Path) -> None:
    cmd = _find_opendsscmd()
    try:
        subprocess.run(
            [cmd, str(script.resolve())],
            cwd=script.parent,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr or exc.stdout or str(exc)
        raise PfDiffInfraError(f"OpenDSS solve failed: {detail}") from exc


def _dss_phase(node: int) -> str:
    if node == 1:
        return "_A"
    if node == 2:
        return "_B"
    return "_C"


def _parse_voltages_csv(path: Path) -> dict[str, float]:
    """
    Parse OpenDSS ``export voltages`` CSV into ``BUS_A`` -> per-unit magnitude.
    """
    if not path.is_file():
        raise PfDiffError(f"Voltage export missing: {path}")

    nodes: dict[str, float] = {}
    with path.open(encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if not header:
            raise PfDiffError(f"Empty voltage export: {path}")

        for row in reader:
            if not row or not row[0].strip():
                continue
            bus = row[0].strip().strip('"').upper()
            if len(row) < 14:
                continue
            for node_idx, pu_idx in ((2, 5), (6, 9), (10, 13)):
                try:
                    node = int(row[node_idx])
                    pu = float(row[pu_idx])
                except (ValueError, IndexError):
                    continue
                if node > 0 and pu > 0:
                    nodes[f"{bus}{_dss_phase(node)}"] = pu

    if not nodes:
        raise PfDiffError(f"No voltage rows parsed from {path}")

    return nodes


def _compare_voltages(
    gold: dict[str, float],
    roundtrip: dict[str, float],
) -> PfMetrics:
    shared = sorted(set(gold) & set(roundtrip))
    if not shared:
        raise PfDiffError("No common bus-phase keys between gold and roundtrip exports")

    max_delta_pct = 0.0
    for key in shared:
        g = gold[key]
        r = roundtrip[key]
        if g <= 0:
            continue
        delta_pct = abs(r - g) / g * 100.0
        max_delta_pct = max(max_delta_pct, delta_pct)

    return PfMetrics(vm_delta_pct_max=max_delta_pct, compared_nodes=len(shared))


def build_report(
    feeder_id: str,
    metrics: PfMetrics,
    *,
    tolerance_pct: float,
    status: str,
) -> dict[str, object]:
    return {
        "feeder": feeder_id,
        "pf_gate": "cimhub_opendss",
        "status": status,
        "metrics": {
            "vm_delta_pct_max": round(metrics.vm_delta_pct_max, 6),
            "compared_nodes": metrics.compared_nodes,
        },
        "samples": [],
        "tolerance_vm_delta_pct_max": tolerance_pct,
    }


def run_pf_diff(
    feeder_id: str = "ieee13",
    *,
    binding_pack: BindingPack | None = None,
    root: Path | None = None,
) -> Path:
    """
    Compare gold OpenDSS seed vs CIMHub roundtrip OpenDSS voltages.

    Writes ``work/{feeder}/validation/pf-diff-report.json``.
    """
    pack = binding_pack or load_binding_pack()
    paths = resolve_paths(feeder_id, root)
    tolerance = pack.pf_vm_delta_pct_max

    if not paths.gold_master.is_file():
        raise PfDiffError(f"Gold master missing: {paths.gold_master}")

    roundtrip_master = _pick_roundtrip_master(paths.roundtrip_dss_dir)

    gold_csv = paths.gold_master.parent / "_pf_gold_voltages.csv"
    rt_csv = roundtrip_master.parent / "_pf_roundtrip_voltages.csv"
    gold_script = _write_solve_script(paths.gold_master, gold_csv)
    rt_script = _write_solve_script(roundtrip_master, rt_csv)
    try:
        _run_opendss(gold_script)
        _run_opendss(rt_script)
        gold_v = _parse_voltages_csv(gold_csv)
        rt_v = _parse_voltages_csv(rt_csv)
    finally:
        gold_script.unlink(missing_ok=True)
        rt_script.unlink(missing_ok=True)
        gold_csv.unlink(missing_ok=True)
        rt_csv.unlink(missing_ok=True)

    metrics = _compare_voltages(gold_v, rt_v)
    status = "pass" if metrics.vm_delta_pct_max <= tolerance else "fail"
    report = build_report(
        feeder_id,
        metrics,
        tolerance_pct=tolerance,
        status=status,
    )

    paths.report_path.parent.mkdir(parents=True, exist_ok=True)
    paths.report_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    logger.info(
        "pf_diff feeder=%s status=%s vm_delta_pct_max=%.6f tolerance=%.3f",
        feeder_id,
        status,
        metrics.vm_delta_pct_max,
        tolerance,
    )

    if status == "fail":
        raise PfDiffError(
            f"PF exceedance: vm_delta_pct_max={metrics.vm_delta_pct_max:.6f} "
            f"> tolerance={tolerance}"
        )

    return paths.report_path
