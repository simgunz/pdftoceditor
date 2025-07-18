"""pdftoceditor CLI."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from pdftoceditor import __version__, logs
from pdftoceditor.logs import LogLevel

app = typer.Typer()


def version_callback(value: bool) -> None:
    """Provides a version callback for the cli."""
    if value:
        typer.echo(f"pdftoceditor version {__version__}")
        raise typer.Exit()


@app.command()
def cli(
    log_level: Annotated[
        Optional[LogLevel],
        typer.Option(
            case_sensitive=False,
            envvar="LOG_LEVEL",
            help="Set the logging level.",
        ),
    ] = LogLevel.INFO,
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
    if log_level is not None:
        logs.set_level(log_level.value)

