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
    help="""Update the table of content of a PDF using a text file.

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
    """Replace the table of content of input PDF with the one specified in ToC file."""
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
    """Append the table of content specified in ToC file to the existing one of input PDF."""
    update_toc(input_pdf_path, toc_file_path, output, replace_toc=False)


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
    """Dump the table of content of input PDF to a text file."""
    dump_text_toc(input_pdf_path, output_toc_path, align_left)
