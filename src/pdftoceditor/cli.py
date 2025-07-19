"""pdftoceditor CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from pdftoceditor import __version__
from pdftoceditor.pdftoceditor import dump_text_toc, update_toc

app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="markdown",
    help="""Edit a PDF table of contents using simple text files.

    **TOC file format**\n
    \n
    Page numbers are right-aligned with one space separating them from entries.\n
    Two spaces per indentation level for sub-entries.\n
    \n
    **Example**\n
    ```
    1   Chapter 1. This line is not rendered by typer for some reason.\n
    1   Section 1\n
    2     Subsection 1.1\n
    3     Subsection 1.2\n
    4       Subsubsection 1.1.1\n
    10  Section 2\n
    100 Section 3\n
    ```
    """,
)


def version_callback(value: bool) -> None:
    """Provides a version callback for the cli."""
    if value:
        typer.echo(f"pdftoceditor version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show the application's version and exit",
        ),
    ] = None,
) -> None:
    pass


@app.command()
def dump(
    input_pdf_path: Annotated[Path, typer.Argument(help="Input PDF file")],
    output_toc_path: Annotated[
        Optional[Path],
        typer.Option("--output-toc", "-t", help="Output table of content text file"),
    ] = None,
    align_left: Annotated[
        bool,
        typer.Option(
            "--align-left",
            "-r",
            help="Align the page numbers to the left on the text table of content",
        ),
    ] = False,
) -> None:
    """Extract the existing table of contents from a PDF to a text file."""
    dump_text_toc(input_pdf_path, output_toc_path, align_left)


@app.command()
def replace(
    input_pdf_path: Annotated[Path, typer.Argument(help="Input PDF file")],
    toc_file_path: Annotated[Path, typer.Argument(help="Table of content text file")],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o", help="Output PDF file with updated table of content"
        ),
    ] = None,
) -> None:
    """Replace the PDF's table of contents with entries from a text file."""
    update_toc(input_pdf_path, toc_file_path, output, replace_toc=True)


@app.command()
def append(
    input_pdf_path: Annotated[Path, typer.Argument(help="Input PDF file")],
    toc_file_path: Annotated[Path, typer.Argument(help="Table of content text file")],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o", help="Output PDF file with updated table of content"
        ),
    ] = None,
) -> None:
    """Add new table of contents entries to the existing PDF bookmarks."""
    update_toc(input_pdf_path, toc_file_path, output, replace_toc=False)
