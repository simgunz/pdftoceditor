import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, NamedTuple, Optional


class TocEntry(NamedTuple):
    description: str
    level: str
    page: str


BM_TEMPLATE = """\
BookmarkBegin
BookmarkTitle: {description}
BookmarkLevel: {level}
BookmarkPageNumber: {page}\
"""


# Private/Helper Functions
# ========================


def strip_meta_desc(metadata_entry: str) -> str:
    return re.search("[^:]*: ([^\n]*)", metadata_entry).group(1)


def verify_page_alignment(toc: List[TocEntry]) -> bool:
    """Return False if the page numbers are not properly right-aligned"""
    if len({len(toc_entry.page) for toc_entry in toc}) != 1:
        return False
    return True


def dump_metadata(input_pdf_path: Path, metadata_file_path: Path) -> None:
    """Dump the metadata of the pdf to the specified file using pdftk"""
    subprocess.run(
        ["pdftk", str(input_pdf_path), "dump_data", "output", str(metadata_file_path)],
        check=True,
    )


def toc_from_metadata(metadata_file_path: Path) -> List[TocEntry]:
    """Reads the ToC from the PDF metadata and returns a list of TocEntry objects"""
    with metadata_file_path.open() as f:
        lines = f.readlines()

        # Each bookmark has: BookmarkTitle, BookmarkLevel, BookmarkPageNumber on lines i+1, i+2, i+3
        toc = (
            TocEntry(
                description=strip_meta_desc(lines[i + 1]),
                level=strip_meta_desc(lines[i + 2]),
                page=strip_meta_desc(lines[i + 3]),
            )
            for i, line in enumerate(lines)
            if "BookmarkBegin" in line
        )

        # Sort by page number
        return sorted(toc, key=lambda entry: int(entry.page))


def load_toc(toc_file_path: Path) -> List[TocEntry]:
    """Reads the ToC from the text file and returns a list of TocEntry objects"""
    toc = list()
    with toc_file_path.open() as f:
        for line in f:
            m = re.search(r"(\s*\d+) ( *)(.*)", line)
            if m:
                page = m.group(1)
                level = str((len(m.group(2)) / 2) + 1)
                description = m.group(3)
                toc.append(TocEntry(description=description, level=level, page=page))
    if not verify_page_alignment(toc):
        raise Exception("Page numbers are not properly aligned.")
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
        toc = toc_from_metadata(metadata_file_path)
    max_page_number_len = len(max(toc, key=lambda entry: len(entry.page)).page)
    if not output_toc_path:
        output_toc_path = input_pdf_path.with_suffix(".txt")
    if align_page_left:
        text_toc_entry_template = "{page}{pagepadspace} {descspace}{description}"
    else:
        text_toc_entry_template = "{pagepadspace}{page} {descspace}{description}"
    with output_toc_path.open("w") as outfile:
        for description, level, page in toc:
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
    toc = load_toc(toc_file_path)
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
                toc += toc_from_metadata(metadata_file_path)
                toc = sorted(toc, key=lambda entry: int(entry.page))
        for description, level, page in toc:
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
