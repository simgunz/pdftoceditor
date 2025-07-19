import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, NamedTuple, Optional


class TocEntry(NamedTuple):
    page: str
    level: str
    description: str


# Regex patterns
RE_TOC_LINE = re.compile(
    r"(?P<padding>\s*)(?P<page>\d+)(?P<spaces> *)(?P<description>.*)"
)
RE_METADATA_ENTRY = re.compile(r"[^:]*: (?P<value>[^\n]*)")

# Metadata bookmark structure offsets from BookmarkBegin line
BOOKMARK_TITLE_OFFSET = 1
BOOKMARK_LEVEL_OFFSET = 2
BOOKMARK_PAGE_OFFSET = 3

BM_TEMPLATE = """\
BookmarkBegin
BookmarkTitle: {description}
BookmarkLevel: {level}
BookmarkPageNumber: {page}\
"""


# Private/Helper Functions
# ========================


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


def dump_metadata(input_pdf_path: Path, metadata_file_path: Path) -> None:
    """Dump the metadata of the pdf to the specified file using pdftk"""
    subprocess.run(
        ["pdftk", str(input_pdf_path), "dump_data", "output", str(metadata_file_path)],
        check=True,
    )


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
    align_page_left: bool = False,
) -> None:
    """Dump the table of content of the given PDF to a text file"""
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete_on_close=False
    ) as temp_file:
        metadata_file_path = Path(temp_file.name)
        dump_metadata(input_pdf_path, metadata_file_path)
        toc = load_metadata_toc(metadata_file_path)
    max_page_number_len = len(max(toc, key=lambda entry: len(entry.page)).page)
    if not output_toc_path:
        output_toc_path = input_pdf_path.with_suffix(".txt")
    if align_page_left:
        text_toc_entry_template = "{page}{pagepadspace} {descspace}{description}"
    else:
        text_toc_entry_template = "{pagepadspace}{page} {descspace}{description}"
    with output_toc_path.open("w") as outfile:
        for page, level, description in toc:
            pagepadspace = " " * (max_page_number_len - len(page))
            descspace = "  " * (int(level) - 1)
            text_toc_entry = text_toc_entry_template.format(
                page=page,
                pagepadspace=pagepadspace,
                descspace=descspace,
                description=description,
            )
            print(text_toc_entry, file=outfile)


def update_toc(
    input_pdf_path: Path,
    toc_file_path: Path,
    output_pdf_path: Optional[Path] = None,
    replace_toc: bool = False,
) -> None:
    """Update the table of contents of the PDF with new entries"""
    toc = load_text_toc(toc_file_path)
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete_on_close=False
    ) as temp_file:
        metadata_file_path = Path(temp_file.name)
        dump_metadata(input_pdf_path, metadata_file_path)
        with metadata_file_path.open() as metadata_file:
            # Acquire the metadata lines not related to the ToC
            metadata = [
                line for line in metadata_file if not re.match("Bookmark.*", line)
            ]
            if not replace_toc:
                toc += load_metadata_toc(metadata_file_path)
                toc = sorted(toc, key=lambda entry: int(entry.page))
        for page, level, description in toc:
            metadata_toc_entry = BM_TEMPLATE.format(
                description=description, level=level, page=page.strip()
            )
            metadata.append(metadata_toc_entry + "\n")
        with metadata_file_path.open("w") as metadata_file:
            metadata_file.write("".join(metadata))
        if not output_pdf_path:
            output_pdf_path = input_pdf_path.with_stem(
                f"{input_pdf_path.stem}_updated_toc"
            )
        subprocess.run(
            [
                "pdftk",
                str(input_pdf_path),
                "update_info",
                str(metadata_file_path),
                "output",
                str(output_pdf_path),
            ],
            check=True,
        )
