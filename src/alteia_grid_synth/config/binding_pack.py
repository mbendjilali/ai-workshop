"""Load GridOS binding pack values at runtime (PRD §10.1)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_BINDING_PACK_PATH = Path("config/gridos-binding-pack.yaml")


@dataclass(frozen=True)
class BindingPack:
    binding_version: str
    cim_namespace: str
    profiles_required: tuple[str, ...]
    cdpsm_edition: str
    platform_release: str
    pf_vm_delta_pct_max: float = 0.1


def repo_root(start: Path | None = None) -> Path:
    """Walk up from *start* (or this file) to find repo root (pyproject.toml)."""
    path = (start or Path(__file__)).resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise FileNotFoundError("Could not locate repo root (pyproject.toml)")


def _parse_binding_pack_text(text: str) -> dict[str, object]:
    """Parse flat binding-pack YAML used in P0 (no nested structures)."""
    data: dict[str, object] = {}
    profiles: list[str] = []
    in_profiles = False
    in_pf_tolerances = False

    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith(("cim_namespace:", "binding_version:")) or ":" in stripped:
            line = stripped
        else:
            line = stripped.split("#", 1)[0].strip()
        if not line:
            continue
        if line == "profiles_required:":
            in_profiles = True
            in_pf_tolerances = False
            continue
        if line == "pf_tolerances:":
            in_pf_tolerances = True
            in_profiles = False
            continue
        if in_profiles:
            if line.startswith("- "):
                profiles.append(line[2:].strip())
                continue
            in_profiles = False
        if in_pf_tolerances:
            if line.startswith("vm_delta_pct_max:"):
                data["pf_vm_delta_pct_max"] = line.split(":", 1)[1].strip()
                continue
            in_pf_tolerances = False
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            data[key] = value

    if profiles:
        data["profiles_required"] = profiles
    return data


def load_binding_pack(path: Path | None = None) -> BindingPack:
    root = repo_root()
    pack_path = path or (root / DEFAULT_BINDING_PACK_PATH)
    if not pack_path.is_file():
        raise FileNotFoundError(f"Binding pack not found: {pack_path}")

    data = _parse_binding_pack_text(pack_path.read_text(encoding="utf-8"))
    profiles = tuple(str(p) for p in data.get("profiles_required", ()))
    pf_vm = float(data.get("pf_vm_delta_pct_max", 0.1))
    return BindingPack(
        binding_version=str(data["binding_version"]),
        cim_namespace=str(data["cim_namespace"]),
        profiles_required=profiles,
        cdpsm_edition=str(data.get("cdpsm_edition", "")),
        platform_release=str(data.get("platform_release", "")),
        pf_vm_delta_pct_max=pf_vm,
    )
