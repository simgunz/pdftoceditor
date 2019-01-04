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
BookmarkLevel: {level:g}
BookmarkPageNumber: {page}\
"""


def toc_from_metadata(filename):
    toc = list()
    with open(filename) as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            if lines[i] == 'BookmarkBegin\n':
                title = lines[i+1][14:].strip('\n').strip(' ')
                level = int(lines[i+2][14:].strip('\n').strip(' '))
                page = lines[i+3][19:].strip('\n').strip(' ')
                toc.append((title, level, page))
                i += 4
            else:
                i += 1

        toc = sorted(toc, key=lambda t: int(t[2]))
    return toc


def add_toc_to_metadata(filename, toc, replace=False):
    with TemporaryDirectory() as tempdir:
        metadatafile = dump_toc(filename, tempdir)
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


def dump_toc(fname, tempdir):
    metadatafile = os.path.join(tempdir, "metadata.txt")
    cmd_dump_metadata = "pdftk '{pdfname}' dump_data output {metadatafile}".format(
        pdfname=fname, metadatafile=metadatafile)
    os.system(cmd_dump_metadata)
    return metadatafile


def dump_text_toc(inputpdf, outputpdf=None, align_page_right=False):
    with TemporaryDirectory() as tempdir:
        metadatafile = dump_toc(inputpdf, tempdir)
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


def load_toc(filename):
    toc = list()
    with open(filename) as f:
        for l in f:
            m = re.search(r'(\d+) ( *)(.*)', l)
            if m:
                title = m.group(3)
                level = (len(m.group(2))/2)+1
                page = m.group(1)
                toc.append((title, level, page))
    return toc


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
