"""Typer CLI for alteia-grid-synth.

Exit codes (enforced in Story 3.3):
  0 — success
  1 — validation failure
  2 — infrastructure failure
"""

from __future__ import annotations

import typer

from alteia_grid_synth import __version__
from alteia_grid_synth.pipeline.export_cim100 import (
    ExportCim100Error,
    ExportCim100InfraError,
    run_export,
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
