"""pdftoceditor CLI."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from pdftoceditor import __version__

app = typer.Typer(no_args_is_help=True)


def version_callback(value: bool) -> None:
    """Provides a version callback for the cli."""
    if value:
        typer.echo(f"pdftoceditor version {__version__}")
        raise typer.Exit()


@app.command()
def cli(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show the application's version and exit.",
        ),
    ] = None,
) -> None:
    """Engage with pdftoceditor using this CLI."""
    pass
