"""Binding pack loader tests."""

from __future__ import annotations

from alteia_grid_synth.config.binding_pack import load_binding_pack


def test_load_cim_namespace():
    pack = load_binding_pack()
    assert pack.cim_namespace == "http://iec.ch/TC57/CIM100#"
    assert pack.profiles_required == ("FUN", "EP", "TOPO", "CAT", "GEO", "SSH")
