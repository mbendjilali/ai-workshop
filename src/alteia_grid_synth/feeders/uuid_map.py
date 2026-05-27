"""Parse and compare OpenDSS UUID map files (uuids.dat)."""

from __future__ import annotations

import re
from pathlib import Path

_UUID_LINE = re.compile(
    r"^\s*(?P<kind>[A-Za-z0-9_.]+)\s*\{(?P<mrid>[0-9A-Fa-f-]{36})\}\s*$"
)

# GridAPPS-D IEEE13_CDPSM reference feeder circuit mRID (line 1 of uuids.dat).
IEEE13_CIRCUIT_MRID = "49AD8E07-3BF9-A4E2-CB8F-C3722F837B62"

# Patterns that must not appear in synthetic-only seeds (NFR-3).
_FORBIDDEN_PATTERNS = (
    re.compile(r"\b\d{3}-\d{3}-\d{4}\b"),  # phone-like
    re.compile(r"\b[A-Z]{2,}-\d{4,}-\d+\b"),  # utility-style feeder codes
)


def parse_uuids_dat(path: Path) -> dict[str, str]:
    """Return mapping of OpenDSS object key (lowercase) to normalized mRID."""
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _UUID_LINE.match(line)
        if not match:
            continue
        key = match.group("kind").lower()
        mrid = match.group("mrid").upper()
        entries[key] = mrid
    return entries


def mrid_set(path: Path) -> frozenset[str]:
    """Unique mRIDs in a uuid map file."""
    return frozenset(parse_uuids_dat(path).values())


def assert_no_forbidden_identifiers(*paths: Path) -> None:
    """Raise ValueError if seed text looks like real utility/customer data."""
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in _FORBIDDEN_PATTERNS:
            if pattern.search(text):
                raise ValueError(
                    f"Forbidden identifier pattern {pattern.pattern!r} in {path}"
                )


def compare_uuid_exports(path_a: Path, path_b: Path) -> None:
    """Assert two OpenDSS UUID export files describe the same mRID set."""
    set_a = mrid_set(path_a)
    set_b = mrid_set(path_b)
    if set_a != set_b:
        only_a = set_a - set_b
        only_b = set_b - set_a
        raise AssertionError(
            f"mRID sets differ: only in A ({len(only_a)}), only in B ({len(only_b)})"
        )
