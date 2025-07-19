"""pdftoceditor CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from pdftoceditor import __version__
from pdftoceditor.pdftoceditor import (
    dump_text_toc,
    update_toc,
    validate_pdftk_installed,
)

app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="markdown",
)


def version_callback(value: bool) -> None:
    """Provides a version callback for the cli."""
    if value:
        typer.echo(f"pdftoceditor version {__version__}")
        raise typer.Exit()


def validate_pdf_file(path: Path) -> Path:
    """Validate that a file has .pdf extension."""
    if path.suffix.lower() != ".pdf":
        raise typer.BadParameter(f"File must have .pdf extension, got: {path.suffix}")
    return path


def validate_output_directory(output_path: Path) -> None:
    """Validate that the output directory exists."""
    if output_path.parent != Path(".") and not output_path.parent.exists():
        raise typer.BadParameter(
            f"Output directory does not exist: {output_path.parent}"
        )
    if output_path.parent.exists() and not output_path.parent.is_dir():
        raise typer.BadParameter(
            f"Output path parent is not a directory: {output_path.parent}"
        )


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
    """Edit a PDF table of contents using simple text files.

    **TOC file format**\n
    \n
    Page numbers are right-aligned with one space separating them from entries.\n
    Two spaces per indentation level for sub-entries.\n
    \n
    **Example**\n
    ```
    -------------\n
    1   Section 1\n
    2     Subsection 1.1\n
    3     Subsection 1.2\n
    4       Subsubsection 1.1.1\n
    10  Section 2\n
    100 Section 3\n
    ```
    """
    try:
        validate_pdftk_installed()
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def dump(
    input_pdf_path: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            exists=True,
            callback=validate_pdf_file,
            help="Input PDF file",
        ),
    ],
    output_toc_path: Annotated[
        Optional[Path],
        typer.Option(
            "--output-toc",
            "-t",
            help="Output table of content text file",
            show_default="input filename with .txt extension, next to original PDF",
        ),
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
    if output_toc_path:
        validate_output_directory(output_toc_path)
    dump_text_toc(input_pdf_path, output_toc_path, align_left)


@app.command()
def replace(
    input_pdf_path: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            exists=True,
            callback=validate_pdf_file,
            help="Input PDF file",
        ),
    ],
    toc_file_path: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            exists=True,
            help="Table of content text file",
        ),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output PDF file with updated table of content",
            show_default="input filename with '_updated_toc' suffix, next to original PDF",
        ),
    ] = None,
) -> None:
    """Replace the PDF's table of contents with entries from a text file."""
    if output:
        validate_output_directory(output)
    update_toc(input_pdf_path, toc_file_path, output, replace_toc=True)


@app.command()
def append(
    input_pdf_path: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            exists=True,
            callback=validate_pdf_file,
            help="Input PDF file",
        ),
    ],
    toc_file_path: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            exists=True,
            help="Table of content text file",
        ),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output PDF file with updated table of content",
            show_default="input filename with '_updated_toc' suffix, next to original PDF",
        ),
    ] = None,
) -> None:
    """Add new table of contents entries to the existing PDF bookmarks."""
    if output:
        validate_output_directory(output)
    update_toc(input_pdf_path, toc_file_path, output, replace_toc=False)
