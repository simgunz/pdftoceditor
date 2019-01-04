#!/usr/bin/python
"""
Usage:
  pdfbookmark.py replace [--output  FILE] <inputpdf> <tocfile>
  pdfbookmark.py append  [--output FILE] <inputpdf> <tocfile>
  pdfbookmark.py dump [--output-toc FILE --align-left] <inputpdf>

Update the table of content of a PDF using the one specified in a text file.

Format of table of content text file:
  1 Section 1
  2   Subsection 1.1
  3   Subsection 1.2
  4     Subsubsection 1.1.1
 10 Section 2
100 Section 3


Operations:
  replace <inputpdf> <tocfile>  Replace the table of content of <inputpdf> with the one
                                specified in <tocfile>
  append <inputpdf> <tocfile>   Append the table of content specified in <tocfile> to the existing
                                one of <inputpdf>
  dump <inputpdf>               Dump the table of content of <inputpdf> to a text file


Options:
  -o FILE, --output=FILE        Output PDF file with updated table of content.
  -t FILE, --output-toc=FILE    Output table of content text file.
  -r, --align-left              Align the page numbers to the left on the text table of content.
  -h, --help                    Show this help message and exit
  -v, --version                 Show version and exit
"""

import os
import os.path
import re

from docopt import docopt
from pathlib import Path
from tempfile import TemporaryDirectory

BM_TEMPLATE = """\
BookmarkBegin
BookmarkTitle: {description}
BookmarkLevel: {level}
BookmarkPageNumber: {page}\
"""
CMD_DUMP_METADATA = "pdftk '{inputpdf}' dump_data output {metadatafile}"
CMD_UPDATE_METADATA = "pdftk '{inputpdf}' update_info {metadatafile} output '{outputpdf}'"


def dump_metadata(inputpdf, tempdir):
    """Dump the metadata of the pdf to a temp file in the given temp directory using pdftk"""
    metadatafile = os.path.join(tempdir, "metadata.txt")
    cmd_dump_metadata = CMD_DUMP_METADATA.format(inputpdf=inputpdf, metadatafile=metadatafile)
    os.system(cmd_dump_metadata)
    return metadatafile


def strip_meta_desc(metadata_entry):
    return re.search('[^:]*: ([^\n]*)', metadata_entry).group(1)


def toc_from_metadata(metadatafile):
    """Reads the ToC from the PDF metadata and returns a list of tuple (description, level, page)"""
    toc = list()
    with open(metadatafile) as f:
        lines = f.readlines()
        indices = [i for i, s in enumerate(lines) if 'BookmarkBegin' in s]
        for i in indices:
            rawdescription, rawlevel, rawpage = tuple(lines[i+1:i+4])
            description = strip_meta_desc(rawdescription)
            level = strip_meta_desc(rawlevel)
            page = strip_meta_desc(rawpage)
            toc.append((description, level, page))
        # Sort by page number
        toc = sorted(toc, key=lambda t: int(t[2]))
    return toc


def dump_text_toc(inputpdf, outputpdf=None, align_page_left=False):
    """Dump the table of content of the given PDF to a text file"""
    with TemporaryDirectory() as tempdir:
        metadatafile = dump_metadata(inputpdf, tempdir)
        toc = toc_from_metadata(metadatafile)
    max_page_number_len = len(max(toc, key=lambda t: len(t[2]))[2])
    if not outputpdf:
        outputpdf = Path(inputpdf).with_suffix('.txt')
    if align_page_left:
        text_toc_entry_template = "{page}{pagepadspace} {descspace}{description}"
    else:
        text_toc_entry_template = "{pagepadspace}{page} {descspace}{description}"
    with open(outputpdf, 'w') as outfile:
        for description, level, page in toc:
            pagepadspace = ' ' * (max_page_number_len - len(page))
            descspace = '  ' * (int(level)-1)
            text_toc_entry = text_toc_entry_template.format(page=page,
                                                            pagepadspace=pagepadspace,
                                                            descspace=descspace,
                                                            description=description)
            print(text_toc_entry, file=outfile)


def verify_page_alignment(toc):
    """Return False if the page numbers are not properly right-aligned"""
    if len({len(toc_entry[2]) for toc_entry in toc}) != 1:
        return False
    return True


def load_toc(text_toc):
    """Reads the ToC from the text file and returns a list of tuple (description, level, page)"""
    toc = list()
    with open(text_toc) as f:
        for line in f:
            m = re.search(r'(\s*\d+) ( *)(.*)', line)
            if m:
                page = m.group(1)
                level = str((len(m.group(2))/2)+1)
                description = m.group(3)
                toc.append((description, level, page))
    if not verify_page_alignment(toc):
        raise Exception("Page numbers are not properly aligned.")
    return toc


def update_toc(inputpdf, tocfile, outputpdf=None, replace_toc=False):
    toc = load_toc(tocfile)
    with TemporaryDirectory() as tempdir:
        metadatafile = dump_metadata(inputpdf, tempdir)
        with open(metadatafile) as f:
            # Acquire the metadata lines not related to the ToC
            metadata = [l for l in f if not re.match('Bookmark.*', l)]
            if not replace_toc:
                toc += toc_from_metadata(metadatafile)
                toc = sorted(toc, key=lambda t: int(t[2]))
        for description, level, page in toc:
            metadata_toc_entry = BM_TEMPLATE.format(description=description,
                                                    level=level,
                                                    page=page.strip())
            metadata.append(metadata_toc_entry + '\n')
        with open(metadatafile, 'w') as f:
            f.write("".join(metadata))
        if not outputpdf:
            fname, ext = inputpdf.rsplit('.', 1)
            outputpdf = "{0}_updated_toc.{1}".format(fname, ext)
        cmd_update_metadata = CMD_UPDATE_METADATA.format(inputpdf=inputpdf,
                                                         metadatafile=metadatafile,
                                                         outputpdf=outputpdf)
        os.system(cmd_update_metadata)


if __name__ == "__main__":
    args = docopt(__doc__, version='1.0')
    if args["dump"]:
        dump_text_toc(args["<inputpdf>"], args["--output-toc"], args["--align-left"])
    else:
        update_toc(args["<inputpdf>"], args["<tocfile>"], args["--output"], replace_toc=args["replace"])
