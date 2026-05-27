# IEEE 13 OpenDSS seed (`ieee13`)

Synthetic IEEE 13-node test feeder (CDPSM-oriented OpenDSS model) for the P0 pipeline spine.

## Provenance

Derived from [GRIDAPPSD/Powergrid-Models](https://github.com/GRIDAPPSD/Powergrid-Models) (`models/feeders/OpenDSS/IEEE/IEEE13_CDPSM/`), commit lineage tracked at import time (2026-05-27). No real utility or customer identifiers (NFR-3).

| File | Upstream |
|------|----------|
| `Master.dss` | `IEEE13_CDPSM.dss` + `uuids file=uuids.dat` |
| `uuids.dat` | `ieee13_uuids.dat` |
| `IEEE13NodeExtra_BusXY.csv` | same |

## CIM export parameters (Story 1.3)

From upstream `convert.json` (not executed in this story):

| Parameter | mRID / value |
|-----------|----------------|
| Feeder | `49AD8E07-3BF9-A4E2-CB8F-C3722F837B62` |
| Substation | `6C62C905-6FC7-653D-9F1E-1340F974A587` |
| Geo region | `73C512BD-7249-4F50-50DA-D93849B89C43` |
| Sub geo region | `ABEB635F-729D-24BF-B8A4-E2EF268D8B9E` |

## Verification

From repo root:

```bash
./scripts/verify-ieee13-mrid-stability.sh
```

Or: `pytest tests/integration/test_ieee13_seed.py -m opendss` when OpenDSS is on PATH.

## Naming

- CLI / pipeline feeder id: `ieee13`
- Future combined CDPSM XML: `ieee13cdpsm.xml`
- Dataset id: `ieee13-asbuilt`
