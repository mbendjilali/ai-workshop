"""Unit tests for PF diff comparison logic."""

from __future__ import annotations

import pytest

from alteia_grid_synth.pipeline.pf_diff import PfDiffError, _compare_voltages


def test_compare_voltages_passes_within_tolerance() -> None:
    gold = {"BUS1_A": 1.0, "BUS2_B": 2.0}
    rt = {"BUS1_A": 1.0005, "BUS2_B": 1.9998}
    metrics = _compare_voltages(gold, rt)
    assert metrics.compared_nodes == 2
    assert metrics.vm_delta_pct_max == pytest.approx(0.05, abs=1e-6)


def test_compare_voltages_no_shared_nodes_raises() -> None:
    with pytest.raises(PfDiffError, match="No common bus-phase"):
        _compare_voltages({"A_A": 1.0}, {"B_A": 1.0})
