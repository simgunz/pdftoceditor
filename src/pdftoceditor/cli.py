"""pdftoceditor CLI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Optional

import typer

from pdftoceditor import __version__
from pdftoceditor.pdftoceditor import (
    EmptyTocError,
    PageAlignment,
    PasswordRequiredError,
    PdfProtectionError,
    dump_text_toc,
    update_toc,
    validate_pdftk_installed,
)

app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="markdown",
)


def validate_pdf_file(path: Path) -> Path:
    """Validate that a file has .pdf extension."""
    if path.suffix.lower() != ".pdf":
        raise typer.BadParameter(f"File must have .pdf extension, got: {path.suffix}")
    return path


def validate_output_directory(output_path: Path) -> None:
    """Validate that the output directory exists."""
    parent = output_path.parent
    if not parent.exists():
        raise typer.BadParameter(f"Output directory does not exist: {parent}")


def get_pdf_password(prompt_for_password: bool) -> Optional[str]:
    """Get PDF password from flag prompting or environment variable.

    Args:
        prompt_for_password: If True, prompt user for password

    Returns:
        Password string or None if no password needed
    """
    if prompt_for_password:
        return typer.prompt("Password", hide_input=True)
    return os.environ.get("PDF_PASSWORD")


def handle_pdf_error(e: Exception, input_pdf_path: Path) -> None:
    """Handle common PDF protection errors with consistent messaging."""
    if isinstance(e, PasswordRequiredError):
        typer.echo(
            f"Error: PDF '{input_pdf_path}' requires a password.\n"
            "Use --password to prompt for password, or set PDF_PASSWORD environment variable.",
            err=True,
        )
    elif isinstance(e, PdfProtectionError):
        typer.echo(f"Error: {e}", err=True)
    elif isinstance(e, EmptyTocError):
        typer.echo(
            f"Error: The PDF '{input_pdf_path}' contains no table of contents to extract.",
            err=True,
        )
    else:
        raise e
    raise typer.Exit(1)


def validate_exclusive_options(
    output: Optional[Path], in_place: bool
) -> Optional[Path]:
    """Validate that --output and --in-place are not used together and return final output path."""
    if output and in_place:
        typer.echo(
            "Error: Cannot use both --output and --in-place options together.", err=True
        )
        raise typer.Exit(1)

    if output:
        validate_output_directory(output)

    return output


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
    pdf_file: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            exists=True,
            callback=validate_pdf_file,
            help="PDF file to extract table of contents from",
        ),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output table of contents text file",
            show_default="PDF filename with _toc.txt extension",
        ),
    ] = None,
    pages_alignment: Annotated[
        PageAlignment,
        typer.Option(
            "--pages-alignment",
            "-a",
            help="Alignment of page numbers in the table of contents",
        ),
    ] = PageAlignment.RIGHT,
    password: Annotated[
        bool,
        typer.Option(
            "--password",
            "-p",
            help="Prompt for password to open protected PDF (or set PDF_PASSWORD env var).",
        ),
    ] = False,
) -> None:
    """Extract the existing table of contents from a PDF to a text file."""
    if output:
        validate_output_directory(output)

    pdf_password = get_pdf_password(password)

    # Convert PageAlignment enum to boolean for align_page_left parameter
    align_page_left = pages_alignment == PageAlignment.LEFT

    try:
        dump_text_toc(pdf_file, output, align_page_left, pdf_password)
    except (PasswordRequiredError, PdfProtectionError, EmptyTocError) as e:
        handle_pdf_error(e, pdf_file)


@app.command()
def replace(
    pdf_file: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            exists=True,
            callback=validate_pdf_file,
            help="PDF file to modify",
        ),
    ],
    toc_file: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            exists=True,
            help="Table of contents text file",
        ),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output PDF file with updated table of contents",
            show_default="PDF filename with '_new' suffix",
        ),
    ] = None,
    in_place: Annotated[
        bool,
        typer.Option(
            "--in-place",
            "-i",
            help="Update the PDF file in place (overwrite original)",
        ),
    ] = False,
    password: Annotated[
        bool,
        typer.Option(
            "--password",
            "-p",
            help="Prompt for password to open protected PDF (or set PDF_PASSWORD env var).",
        ),
    ] = False,
) -> None:
    """Replace the PDF's table of contents with entries from a text file."""
    validated_output = validate_exclusive_options(output, in_place)
    final_output = pdf_file if in_place else validated_output

    pdf_password = get_pdf_password(password)

    try:
        update_toc(
            pdf_file, toc_file, final_output, replace_toc=True, password=pdf_password
        )
    except (PasswordRequiredError, PdfProtectionError) as e:
        handle_pdf_error(e, pdf_file)


@app.command()
def append(
    pdf_file: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            exists=True,
            callback=validate_pdf_file,
            help="PDF file to modify",
        ),
    ],
    toc_file: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            exists=True,
            help="Table of contents text file",
        ),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output PDF file with updated table of contents",
            show_default="PDF filename with '_new' suffix",
        ),
    ] = None,
    in_place: Annotated[
        bool,
        typer.Option(
            "--in-place",
            "-i",
            help="Update the PDF file in place (overwrite original)",
        ),
    ] = False,
    password: Annotated[
        bool,
        typer.Option(
            "--password",
            "-p",
            help="Prompt for password to open protected PDF (or set PDF_PASSWORD env var).",
        ),
    ] = False,
) -> None:
    """Add new table of contents entries to the existing PDF bookmarks."""
    validated_output = validate_exclusive_options(output, in_place)
    final_output = pdf_file if in_place else validated_output

    pdf_password = get_pdf_password(password)

    try:
        update_toc(
            pdf_file, toc_file, final_output, replace_toc=False, password=pdf_password
        )
    except (PasswordRequiredError, PdfProtectionError) as e:
        handle_pdf_error(e, pdf_file)
