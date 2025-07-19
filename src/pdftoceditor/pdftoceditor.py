import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

BM_TEMPLATE = """\
BookmarkBegin
BookmarkTitle: {description}
BookmarkLevel: {level}
BookmarkPageNumber: {page}\
"""
CMD_UPDATE_METADATA = (
    "pdftk '{inputpdf}' update_info {metadatafile} output '{outputpdf}'"
)


def validate_pdftk_installed() -> None:
    """Validate that pdftk is installed and accessible.

    Raises:
        FileNotFoundError: If pdftk command is not found in PATH
    """
    if shutil.which("pdftk") is None:
        raise FileNotFoundError("pdftk command not found. Please install pdftk.")


def dump_metadata(input_pdf_path: Path, metadata_file_path: Path) -> None:
    """Dump the metadata of the pdf to the specified file using pdftk"""
    subprocess.run(
        ["pdftk", str(input_pdf_path), "dump_data", "output", str(metadata_file_path)],
        check=True,
    )


def strip_meta_desc(metadata_entry: str) -> str:
    return re.search("[^:]*: ([^\n]*)", metadata_entry).group(1)


def toc_from_metadata(metadata_file_path: Path) -> List[Tuple[str, str, str]]:
    """Reads the ToC from the PDF metadata and returns a list of tuple (description, level, page)"""
    toc = list()
    with metadata_file_path.open() as f:
        lines = f.readlines()
        indices = [i for i, s in enumerate(lines) if "BookmarkBegin" in s]
        for i in indices:
            rawdescription, rawlevel, rawpage = tuple(lines[i + 1 : i + 4])
            description = strip_meta_desc(rawdescription)
            level = strip_meta_desc(rawlevel)
            page = strip_meta_desc(rawpage)
            toc.append((description, level, page))
        # Sort by page number
        toc = sorted(toc, key=lambda t: int(t[2]))
    return toc


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
    max_page_number_len = len(max(toc, key=lambda t: len(t[2]))[2])
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


def verify_page_alignment(toc: List[Tuple[str, str, str]]) -> bool:
    """Return False if the page numbers are not properly right-aligned"""
    if len({len(toc_entry[2]) for toc_entry in toc}) != 1:
        return False
    return True


def load_toc(toc_file_path: Path) -> List[Tuple[str, str, str]]:
    """Reads the ToC from the text file and returns a list of tuple (description, level, page)"""
    toc = list()
    with toc_file_path.open() as f:
        for line in f:
            m = re.search(r"(\s*\d+) ( *)(.*)", line)
            if m:
                page = m.group(1)
                level = str((len(m.group(2)) / 2) + 1)
                description = m.group(3)
                toc.append((description, level, page))
    if not verify_page_alignment(toc):
        raise Exception("Page numbers are not properly aligned.")
    return toc


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
                toc = sorted(toc, key=lambda t: int(t[2]))
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
        cmd_update_metadata = CMD_UPDATE_METADATA.format(
            inputpdf=input_pdf_path,
            metadatafile=metadata_file_path,
            outputpdf=output_pdf_path,
        )
        os.system(cmd_update_metadata)
