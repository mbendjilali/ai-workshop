"""CIM XML validation helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from alteia_grid_synth.pipeline.cim_xml import (
    assert_cim_namespace,
    assert_profiles_present,
    extract_mrids_from_cim_xml,
    validate_combined_cdpsm_xml,
)

NAMESPACE = "http://iec.ch/TC57/CIM100#"
PROFILES = ("FUN", "EP", "TOPO", "CAT", "GEO", "SSH")
MRID = "49AD8E07-3BF9-A4E2-CB8F-C3722F837B62"

FIXTURE_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:cim="{NAMESPACE}">
  <cim:Feeder rdf:about="urn:uuid:{MRID}">
    <cim:IdentifiedObject.mRID>{MRID}</cim:IdentifiedObject.mRID>
  </cim:Feeder>
  <cim:Substation rdf:about="urn:uuid:6C62C905-6FC7-653D-9F1E-1340F974A587"/>
  <cim:GeographicalRegion rdf:about="urn:uuid:73C512BD-7249-4F50-50DA-D93849B89C43"/>
  <cim:ACLineSegment rdf:about="urn:uuid:A04CDFB1-E951-4FC4-8882-0323CD70AE3C"/>
  <cim:ConnectivityNode rdf:about="urn:uuid:A8A25B50-3AE3-4A31-A18B-B3FA13397ED3"/>
  <cim:Terminal rdf:about="urn:uuid:A55AC772-D3F2-48AF-8C84-E80F43198C72"/>
  <cim:TransformerTankInfo rdf:about="urn:uuid:70FD7F8F-EF10-425E-AA73-955F13E4486C"/>
  <cim:PositionPoint rdf:about="urn:uuid:05F2AFBD-33EC-4FD0-9AB6-AEF3DA2EA417"/>
  <cim:Location rdf:about="urn:uuid:8E4E3C92-0B7A-4F74-8FD2-CC10F74E452F"/>
  <cim:TopologicalNode rdf:about="urn:uuid:A7CAAC2F-EC2B-4DF3-BD28-C8CCA20D7B7A"/>
  <cim:PowerElectronicsConnection.p>1000</cim:PowerElectronicsConnection.p>
</rdf:RDF>
"""


@pytest.fixture
def fixture_path(tmp_path: Path) -> Path:
    path = tmp_path / "ieee13cdpsm.xml"
    path.write_text(FIXTURE_XML, encoding="utf-8")
    return path


def test_extract_mrids(fixture_path: Path):
    mrids = extract_mrids_from_cim_xml(fixture_path)
    assert MRID in mrids


def test_validate_combined_cdpsm_xml(fixture_path: Path):
    mrids = validate_combined_cdpsm_xml(
        fixture_path,
        cim_namespace=NAMESPACE,
        profiles_required=PROFILES,
    )
    assert MRID in mrids


def test_missing_namespace(tmp_path: Path):
    path = tmp_path / "bad.xml"
    path.write_text("<rdf:RDF/>", encoding="utf-8")
    with pytest.raises(ValueError, match="namespace"):
        assert_cim_namespace(path, NAMESPACE)


def test_missing_profiles(fixture_path: Path):
    text = fixture_path.read_text(encoding="utf-8").replace(
        "<cim:PowerElectronicsConnection.p>", ""
    ).replace("<cim:TopologicalNode ", "")
    path = fixture_path.parent / "no_ssh.xml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="SSH"):
        assert_profiles_present(path, PROFILES)
