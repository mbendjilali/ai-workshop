"""Typer CLI for alteia-grid-synth.

Exit codes (enforced in Story 3.3):
  0 — success
  1 — validation failure
  2 — infrastructure failure
"""

from __future__ import annotations

import typer

from alteia_grid_synth import __version__

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
