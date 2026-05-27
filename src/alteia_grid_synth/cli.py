"""Typer CLI for alteia-grid-synth.

Exit codes (enforced in Story 3.3):
  0 — success
  1 — validation failure
  2 — infrastructure failure
"""

from __future__ import annotations

import logging

import typer

from alteia_grid_synth import __version__
from alteia_grid_synth.pipeline.cimhub_roundtrip import (
    CimhubRoundtripError,
    CimhubRoundtripInfraError,
    run_roundtrip,
)
from alteia_grid_synth.pipeline.export_cim100 import (
    ExportCim100Error,
    ExportCim100InfraError,
    run_export,
)
from alteia_grid_synth.pipeline.ingest_blazegraph import (
    IngestBlazegraphError,
    IngestBlazegraphInfraError,
    run_ingest,
)
from alteia_grid_synth.pipeline.pf_diff import (
    PfDiffError,
    PfDiffInfraError,
    run_pf_diff,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s %(message)s",
)

app = typer.Typer(
    name="grid-synth",
    help="Alteia Synthetic Grid Network Data Generator",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show package version and exit.",
    ),
) -> None:
    """Alteia Synthetic Grid Network Data Generator."""


@app.command("export-cim100")
def export_cim100(
    feeder: str = typer.Argument(
        "ieee13",
        help="Feeder id (e.g. ieee13).",
    ),
) -> None:
    """Export combined CDPSM XML via OpenDSS export cim100."""
    try:
        out = run_export(feeder)
    except ExportCim100Error as exc:
        typer.echo(f"export-cim100 validation failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except ExportCim100InfraError as exc:
        typer.echo(f"export-cim100 infrastructure error: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(str(out))


@app.command("ingest-blazegraph")
def ingest_blazegraph(
    feeder: str = typer.Argument(
        "ieee13",
        help="Feeder id (e.g. ieee13).",
    ),
) -> None:
    """Load combined CDPSM XML into Blazegraph."""
    try:
        run_ingest(feeder)
    except IngestBlazegraphError as exc:
        typer.echo(f"ingest-blazegraph validation failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except IngestBlazegraphInfraError as exc:
        typer.echo(f"ingest-blazegraph infrastructure error: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(f"ingest-blazegraph OK: {feeder}")


@app.command("cimhub-roundtrip")
def cimhub_roundtrip(
    feeder: str = typer.Argument(
        "ieee13",
        help="Feeder id (e.g. ieee13).",
    ),
) -> None:
    """Run CIMHub roundtrip to OpenDSS and GridLAB-D render mirrors."""
    try:
        paths = run_roundtrip(feeder)
    except CimhubRoundtripError as exc:
        typer.echo(f"cimhub-roundtrip validation failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except CimhubRoundtripInfraError as exc:
        typer.echo(f"cimhub-roundtrip infrastructure error: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(str(paths.render_root))


@app.command("pf-diff")
def pf_diff(
    feeder: str = typer.Argument(
        "ieee13",
        help="Feeder id (e.g. ieee13).",
    ),
) -> None:
    """Compare OpenDSS gold PF vs CIMHub roundtrip OpenDSS mirror."""
    try:
        report = run_pf_diff(feeder)
    except PfDiffError as exc:
        typer.echo(f"pf-diff validation failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except PfDiffInfraError as exc:
        typer.echo(f"pf-diff infrastructure error: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(str(report))


@app.command()
def run() -> None:
    """Run the full CDPSM hub pipeline for a feeder."""
    typer.echo("Not implemented — see Story 3.3", err=True)
    raise typer.Exit(code=2)


@app.command()
def validate() -> None:
    """Run the validation gate for a feeder."""
    typer.echo("Not implemented — see Story 3.3", err=True)
    raise typer.Exit(code=2)


@app.command()
def pack() -> None:
    """Package validated Tier A artifacts for registry publish."""
    typer.echo("Not implemented — see Story 3.3", err=True)
    raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
