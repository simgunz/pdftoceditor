#!/usr/bin/python
"""
Usage:
  pdfbookmark.py replace [--output  FILE] <inputpdf> <tocfile>
  pdfbookmark.py append  [--output FILE] <inputpdf> <tocfile>
  pdfbookmark.py dump [--output-toc FILE --align-right] <inputpdf>

Do something

Options:
  -o FILE, --output=FILE      Output PDF file with updated table of content.
  -t FILE, --output-toc=FILE  Output table of content text file.
  -r, --align-right           Align the page numbers to the right on the text table of content.
"""

import os
import os.path
import re

from docopt import docopt
from pathlib import Path
from tempfile import TemporaryDirectory

BM_TEMPLATE = """\
BookmarkBegin
BookmarkTitle: {title}
BookmarkLevel: {level}
BookmarkPageNumber: {page}\
"""
CMD_DUMP_METADATA = "pdftk '{pdfname}' dump_data output {metadatafile}"


def dump_metadata(inputpdf, tempdir):
    """Dump the metadata of the pdf to a temp file in the given temp directory using pdftk"""
    metadatafile = os.path.join(tempdir, "metadata.txt")
    cmd_dump_metadata = CMD_DUMP_METADATA.format(pdfname=inputpdf, metadatafile=metadatafile)
    os.system(cmd_dump_metadata)
    return metadatafile


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


def dump_text_toc(inputpdf, outputpdf=None, align_page_right=False):
    """Dump the table of content of the given PDF to a text file"""
    with TemporaryDirectory() as tempdir:
        metadatafile = dump_metadata(inputpdf, tempdir)
        toc = toc_from_metadata(metadatafile)
    max_page_number_len = len(max(toc, key=lambda t: len(t[2]))[2])
    if not outputpdf:
        outputpdf = Path(inputpdf).with_suffix('.txt')
    if align_page_right:
        text_toc_entry_template = "{pagepadspace}{page} {descspace}{description}"
    else:
        text_toc_entry_template = "{page}{pagepadspace} {descspace}{description}"
    with open(outputpdf, 'w') as outfile:
        for description, level, page in toc:
            pagepadspace = ' ' * (max_page_number_len - len(page))
            descspace = '  ' * (int(level)-1)
            text_toc_entry = text_toc_entry_template.format(page=page,
                                                            pagepadspace=pagepadspace,
                                                            descspace=descspace,
                                                            description=description)
            print(text_toc_entry, file=outfile)


def load_toc(text_toc):
    """Reads the ToC from the text file and returns a list of tuple (description, level, page)"""
    toc = list()
    with open(text_toc) as f:
        for line in f:
            m = re.search(r'(\d+) ( *)(.*)', line)
            if m:
                page = m.group(1)
                level = str((len(m.group(2))/2)+1)
                description = m.group(3)
                toc.append((description, level, page))
    return toc


def strip_meta_desc(metadata_entry):
    return re.search('[^:]*: ([^\n]*)', metadata_entry).group(1)


def add_toc_to_metadata(filename, toc, replace=False):
    with TemporaryDirectory() as tempdir:
        metadatafile = dump_metadata(filename, tempdir)
        with open(metadatafile) as f:
            lines = [l for l in f if not re.match('Bookmark.*', l)]
            if not replace:
                toc += toc_from_metadata(metadatafile)
                toc = sorted(toc, key=lambda t: int(t[2]))
        for t in toc:
            bm = BM_TEMPLATE.format(title=t[0], level=t[1], page=t[2])
            lines.append(bm + '\n')
        metadatafile = os.path.join(tempdir, "metadata.txt")
        with open(metadatafile, 'w') as f:
            f.write("".join(lines))

        cmd_update_metadata = "pdftk '{pdfname}' update_info {metadatafile} output '{pdfname}-new.pdf'".format(
            pdfname=filename, metadatafile=metadatafile)
        os.system(cmd_update_metadata)


if __name__ == "__main__":
    args = docopt(__doc__, version='1.0')
    if args["dump"]:
        dump_text_toc(args["<inputpdf>"], args["--output-toc"], args["--align-right"])
    elif args["replace"]:
        toc = load_toc(args["<tocfile>"])
        add_toc_to_metadata(args["<inputpdf>"], toc, replace=True)
    elif args["append"]:
        toc = load_toc(args["<tocfile>"])
        add_toc_to_metadata(args["<inputpdf>"], toc)
