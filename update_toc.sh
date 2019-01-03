#!/bin/bash

fname="$1"

# Dump metadata
pdftk "$fname" dump_data output metadata.txt

# Convert text TOC and append to metadata.txt
python ../scripts/pdfbookmark.py "${fname%.*}.txt"

# Load new metadata to pdf
pdftk "$fname" update_info metadata.txt output "${fname%.pdf}-new.pdf"

# Clean folder
rm metadata.txt


