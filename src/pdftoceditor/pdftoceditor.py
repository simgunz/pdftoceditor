import re
import shutil
import subprocess
import tempfile
from enum import Enum
from pathlib import Path
from typing import List, NamedTuple, Optional


class EmptyTocError(Exception):
    """Raised when attempting to process a PDF with no table of contents."""

    pass


class PdfProtectionError(Exception):
    """Base exception for PDF protection-related errors."""

    pass


class PasswordRequiredError(PdfProtectionError):
    """Raised when PDF requires a password to access."""

    pass


class IncorrectPasswordError(PdfProtectionError):
    """Raised when an incorrect password is provided for a PDF."""

    pass


class UnsupportedEncryptionError(PdfProtectionError):
    """Raised when PDF uses encryption that pdftk cannot handle."""

    pass


class InvalidPdfError(PdfProtectionError):
    """Raised when PDF file is corrupted or invalid."""

    pass


class PageAlignment(Enum):
    LEFT = "left"
    RIGHT = "right"


class TocEntry(NamedTuple):
    page: str
    level: str
    description: str


# Regex patterns
RE_TOC_LINE = re.compile(
    r"(?P<padding>\s*)(?P<page>\d+)(?P<spaces> *)(?P<description>.*)"
)
RE_METADATA_ENTRY = re.compile(r"[^:]*: (?P<value>[^\n]*)")
RE_BOOKMARK_LINE = re.compile(r"Bookmark.*")

# Metadata bookmark structure offsets from BookmarkBegin line
BOOKMARK_TITLE_OFFSET = 1
BOOKMARK_LEVEL_OFFSET = 2
BOOKMARK_PAGE_OFFSET = 3

# ToC formatting constants
LEVEL_INDENT_SPACES = 2  # Two spaces per indentation level
TOC_TEMPLATE_LEFT_ALIGN = "{page}{padding} {indent}{description}"
TOC_TEMPLATE_RIGHT_ALIGN = "{padding}{page} {indent}{description}"

# Update ToC constants
UPDATE_SUFFIX = "_new"

BM_TEMPLATE = """\
BookmarkBegin
BookmarkTitle: {description}
BookmarkLevel: {level}
BookmarkPageNumber: {page}\
"""


# Private/Helper Functions
# ========================


def parse_pdftk_error(stderr: str, pdf_path: Path) -> None:
    """Parse pdftk error output and raise appropriate exceptions."""
    error_text = stderr.lower()

    if "owner or user password required" in error_text:
        if "but incorrect" in error_text:
            raise IncorrectPasswordError(
                f"Incorrect password provided for PDF '{pdf_path}'"
            )
        elif "but not given" in error_text:
            raise PasswordRequiredError(
                f"PDF '{pdf_path}' requires a password to access"
            )
        else:
            # If we get here, pdftk's password error message format has changed
            raise PdfProtectionError(
                f"Unknown password error for PDF '{pdf_path}': {stderr.strip()}"
            )
    elif "unknown.encryption.type" in error_text:
        raise UnsupportedEncryptionError(
            f"PDF '{pdf_path}' uses unsupported encryption. "
            "Please decrypt the PDF with a modern tool first."
        )
    elif "failed to open input pdf file" in error_text:
        if "password" in error_text:
            raise PasswordRequiredError(
                f"PDF '{pdf_path}' requires a password to access"
            )
        else:
            raise InvalidPdfError(
                f"Cannot open PDF '{pdf_path}'. File may be corrupted or invalid."
            )
    elif "invalid pdf" in error_text:
        raise InvalidPdfError(f"PDF '{pdf_path}' is invalid or corrupted")
    elif stderr.strip():  # Any other error
        raise PdfProtectionError(f"Error processing PDF '{pdf_path}': {stderr.strip()}")


def strip_meta_desc(metadata_entry: str) -> str:
    """Extract value after colon from metadata entry.

    Raises:
        ValueError: If the metadata entry format is invalid
    """
    match = RE_METADATA_ENTRY.match(metadata_entry)
    if not match:
        raise ValueError(f"Invalid metadata format: '{metadata_entry}'")
    return match.group("value")


def calculate_toc_level(indentation_spaces: str) -> str:
    """Calculate ToC level from indentation spaces.

    Each level is indented by 2 spaces:
    - 0 spaces = level 1
    - 2 spaces = level 2
    - 4 spaces = level 3, etc.
    """
    spaces_count = len(indentation_spaces)
    level = (spaces_count // 2) + 1
    return str(float(level))


def validate_toc_format(text_toc_lines: list[str]) -> None:
    """Validate that the ToC text format is correct.

    Raises:
        ValueError: If the file is empty
        ValueError: If any line has invalid format
        ValueError: If page numbers are not properly aligned
    """
    non_empty_lines = [line for line in text_toc_lines if line.strip()]
    # ToC file cannot be empty
    if not non_empty_lines:
        raise ValueError("ToC file cannot be empty")

    # Validate all lines and extract page sections
    page_sections = []
    for line_num, line in enumerate(non_empty_lines, 1):
        match = RE_TOC_LINE.match(line)
        if not match:
            raise ValueError(f"Line {line_num} has invalid format: '{line}'")
        page_sections.append(match.group("padding") + match.group("page"))

    # All page sections must have the same length for alignment
    first_length = len(page_sections[0])
    if not all(len(section) == first_length for section in page_sections):
        raise ValueError("Page numbers are not properly aligned")


def dump_metadata(
    input_pdf_path: Path, metadata_file_path: Path, password: Optional[str] = None
) -> None:
    """Dump the metadata of the pdf to the specified file using pdftk"""
    cmd = ["pdftk", str(input_pdf_path)]
    if password:
        cmd.extend(["input_pw", password])
    cmd.extend(["dump_data", "output", str(metadata_file_path)])

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        parse_pdftk_error(e.stderr, input_pdf_path)


def load_metadata_toc(metadata_file_path: Path) -> List[TocEntry]:
    """Reads the ToC from the PDF metadata and returns a list of TocEntry objects"""
    lines = metadata_file_path.read_text().splitlines()
    # Each bookmark has: BookmarkTitle, BookmarkLevel, BookmarkPageNumber after BookmarkBegin
    toc = (
        TocEntry(
            page=strip_meta_desc(lines[i + BOOKMARK_PAGE_OFFSET]),
            level=strip_meta_desc(lines[i + BOOKMARK_LEVEL_OFFSET]),
            description=strip_meta_desc(lines[i + BOOKMARK_TITLE_OFFSET]),
        )
        for i, line in enumerate(lines)
        if "BookmarkBegin" in line
    )
    # Sort by page number
    return sorted(toc, key=lambda entry: int(entry.page))


def calculate_max_page_width(toc: List[TocEntry]) -> int:
    """Calculate the maximum width needed for page numbers."""
    longest_page_entry = max(toc, key=lambda entry: len(entry.page))
    return len(longest_page_entry.page)


def format_toc_entry(
    entry: TocEntry, max_page_width: int, alignment: PageAlignment
) -> str:
    """Format a single ToC entry as text."""
    # Calculate padding for page number alignment
    page_padding = " " * (max_page_width - len(entry.page))
    # Calculate indentation based on level
    level_number = int(float(entry.level)) - 1
    level_indent = " " * LEVEL_INDENT_SPACES * level_number
    # Select template and format entry
    template = (
        TOC_TEMPLATE_LEFT_ALIGN
        if alignment == PageAlignment.LEFT
        else TOC_TEMPLATE_RIGHT_ALIGN
    )
    return template.format(
        page=entry.page,
        padding=page_padding,
        indent=level_indent,
        description=entry.description,
    )


def load_text_toc(toc_file_path: Path) -> List[TocEntry]:
    """Reads the ToC from the text file and returns a list of TocEntry objects"""
    lines = toc_file_path.read_text().splitlines()
    validate_toc_format(lines)
    toc = [
        TocEntry(
            page=match.group("page"),
            level=calculate_toc_level(match.group("spaces")),
            description=match.group("description"),
        )
        for line in lines
        if (match := RE_TOC_LINE.match(line))
    ]
    return toc


# Public API Functions
# ===================


def validate_pdftk_installed() -> None:
    """Validate that pdftk is installed and accessible.

    Raises:
        FileNotFoundError: If pdftk command is not found in PATH
    """
    if shutil.which("pdftk") is None:
        raise FileNotFoundError("pdftk command not found. Please install pdftk.")


def dump_text_toc(
    input_pdf_path: Path,
    output_toc_path: Optional[Path] = None,
    alignment: PageAlignment = PageAlignment.RIGHT,
    password: Optional[str] = None,
) -> None:
    """Dump the table of content of the given PDF to a text file"""
    # Extract ToC from PDF metadata
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete_on_close=False
    ) as temp_file:
        metadata_file_path = Path(temp_file.name)
        dump_metadata(input_pdf_path, metadata_file_path, password)
        toc = load_metadata_toc(metadata_file_path)

    # Check if ToC is empty
    if not toc:
        raise EmptyTocError("PDF contains no table of contents")

    # Determine output path
    if not output_toc_path:
        output_toc_path = input_pdf_path.with_stem(
            f"{input_pdf_path.stem}_toc"
        ).with_suffix(".txt")

    # Format and write ToC entries
    max_page_width = calculate_max_page_width(toc)
    with output_toc_path.open("w") as outfile:
        for entry in toc:
            formatted_entry = format_toc_entry(entry, max_page_width, alignment)
            print(formatted_entry, file=outfile)


def update_toc(
    input_pdf_path: Path,
    toc_file_path: Path,
    output_pdf_path: Optional[Path] = None,
    replace_toc: bool = False,
    password: Optional[str] = None,
) -> None:
    """Update the table of contents of the PDF with new entries"""
    new_toc = load_text_toc(toc_file_path)

    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete_on_close=False
    ) as temp_file:
        metadata_file_path = Path(temp_file.name)
        dump_metadata(input_pdf_path, metadata_file_path, password)

        # Filter out existing bookmarks from metadata
        metadata_lines = metadata_file_path.read_text().splitlines(keepends=True)
        new_metadata_lines = [
            line for line in metadata_lines if not RE_BOOKMARK_LINE.match(line)
        ]

        # Combine ToC entries
        if replace_toc:
            final_toc = new_toc
        else:
            existing_toc = load_metadata_toc(metadata_file_path)
            final_toc = sorted(
                new_toc + existing_toc, key=lambda entry: int(entry.page)
            )

        # Add formatted ToC entries to metadata
        for entry in final_toc:
            bookmark_entry = BM_TEMPLATE.format(
                description=entry.description,
                level=entry.level,
                page=entry.page.strip(),
            )
            new_metadata_lines.append(bookmark_entry + "\n")

        # Write updated metadata and create output PDF
        metadata_file_path.write_text("".join(new_metadata_lines))

        output_path = output_pdf_path or input_pdf_path.with_stem(
            f"{input_pdf_path.stem}{UPDATE_SUFFIX}"
        )

        # Always use a temporary file to avoid pdftk input=output issues
        with tempfile.NamedTemporaryFile(
            suffix=".pdf", delete_on_close=False
        ) as temp_pdf:
            temp_output_path = Path(temp_pdf.name)

            cmd = ["pdftk", str(input_pdf_path)]
            if password:
                cmd.extend(["input_pw", password])
            cmd.extend(
                [
                    "update_info",
                    str(metadata_file_path),
                    "output",
                    str(temp_output_path),
                ]
            )

            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                shutil.move(str(temp_output_path), str(output_path))
            except subprocess.CalledProcessError as e:
                parse_pdftk_error(e.stderr, input_pdf_path)
