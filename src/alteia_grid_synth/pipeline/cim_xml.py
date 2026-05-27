"""Validate combined CIM100 CDPSM XML exports."""

from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree as ET

# Combined CIM100 merges six CDPSM sub-profiles; OpenDSS does not emit literal
# "FUN"/"EP" tokens. Each profile must have at least one representative element.
PROFILE_CLASS_MARKERS: dict[str, tuple[str, ...]] = {
    "FUN": ("<cim:Feeder ", "<cim:Substation ", "<cim:GeographicalRegion "),
    "EP": ("<cim:ACLineSegment ", "<cim:PowerTransformer ", "<cim:PerLengthImpedance "),
    "TOPO": ("<cim:ConnectivityNode ", "<cim:Terminal "),
    "CAT": ("<cim:TransformerTankInfo ", "<cim:TransformerEndInfo "),
    "GEO": ("<cim:PositionPoint ", "<cim:Location "),
    "SSH": (
        "<cim:PowerElectronicsConnection.p>",
        "<cim:TopologicalNode ",
        "<cim:EnergyConsumer.",
    ),
}

_MRID_IN_TAG = re.compile(
    r"<cim:IdentifiedObject\.mRID>(?P<mrid>[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-"
    r"[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})</cim:IdentifiedObject\.mRID>"
)
_MRID_ATTR = re.compile(
    r'(?:rdf:)?ID="(?P<mrid>[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-'
    r"[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})\""
)


def extract_mrids_from_cim_xml(path: Path) -> frozenset[str]:
    """Collect normalized mRIDs from a combined CIM100 XML file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    found = {m.group("mrid").upper() for m in _MRID_IN_TAG.finditer(text)}
    found.update(m.group("mrid").upper() for m in _MRID_ATTR.finditer(text))
    if not found:
        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            raise ValueError(f"Invalid XML in {path}: {exc}") from exc
        for elem in root.iter():
            for attr in ("ID", "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}ID"):
                val = elem.attrib.get(attr)
                if val and re.search(
                    r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-"
                    r"[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
                    val,
                ):
                    m = re.search(
                        r"([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-"
                        r"[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})",
                        val,
                    )
                    if m:
                        found.add(m.group(1).upper())
    if not found:
        raise ValueError(f"No mRIDs found in CIM XML: {path}")
    return frozenset(found)


def assert_cim_namespace(xml_path: Path, expected_namespace: str) -> None:
    text = xml_path.read_text(encoding="utf-8", errors="replace")
    if expected_namespace not in text:
        raise ValueError(
            f"CIM namespace {expected_namespace!r} not found in {xml_path}"
        )


def assert_profiles_present(xml_path: Path, profiles_required: tuple[str, ...]) -> None:
    text = xml_path.read_text(encoding="utf-8", errors="replace")
    missing: list[str] = []
    for profile in profiles_required:
        markers = PROFILE_CLASS_MARKERS.get(profile)
        if not markers:
            missing.append(profile)
            continue
        if not any(marker in text for marker in markers):
            missing.append(profile)
    if missing:
        raise ValueError(
            f"Missing CDPSM sub-profile content for {missing} in {xml_path}"
        )


def validate_combined_cdpsm_xml(
    xml_path: Path,
    *,
    cim_namespace: str,
    profiles_required: tuple[str, ...],
) -> frozenset[str]:
    """Run export-stage validators; return equipment mRID set."""
    if not xml_path.is_file():
        raise FileNotFoundError(f"CDPSM XML not found: {xml_path}")
    if xml_path.stat().st_size == 0:
        raise ValueError(f"CDPSM XML is empty: {xml_path}")
    assert_cim_namespace(xml_path, cim_namespace)
    assert_profiles_present(xml_path, profiles_required)
    return extract_mrids_from_cim_xml(xml_path)
