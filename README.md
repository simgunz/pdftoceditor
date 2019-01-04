PDF ToC editor update the table of content of a PDF using the one specified in a simple text file.


```
Usage:
  pdftoceditor.py replace [--output  FILE] <inputpdf> <tocfile>
  pdftoceditor.py append  [--output FILE] <inputpdf> <tocfile>
  pdftoceditor.py dump [--output-toc FILE --align-left] <inputpdf>

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
```

Basic usage
-----------
The table of content is specified in a simple text file with the following format:
- Page numbers are right aligned
- One space separates the page numbers to the table of content entries
- Add two extra spaces to create a table of content sub-entry

```
user_toc.txt
  1 Section 1
  2   Subsection 1.1
  3   Subsection 1.2
  4     Subsubsection 1.1.1
 10 Section 2
100 Section 3
```


Replace the table of content of the file `MyPDF.pdf` with the one specified in `user_toc.txt`
and obtain a new file `MyPDF_updated_toc.pdf`.
```
python pdftoceditor.py replace MyPDF.pdf user_toc.txt
```

Add the table of content specified in `user_toc.txt` to the one of the file `MyPDF.pdf`
and obtain a new file `MyNewPDF.pdf`.
```
python pdftoceditor.py append --output MyNewPDF.pdf MyPDF.pdf user_toc.txt
```

Dump the table of content of the file `MyPDF.pdf` to a text file named `original_toc.txt`
```
python pdftoceditor.py dump --output-toc original_toc.txt MyPDF.pdf
```

Notes
-----
- Currently it is not possible to updated the toc with text files with the page numbers left aligned

License MIT
-----------
Project License can be found [here](https://github.com/simgunz/ktouch-lesson-generator/blob/master/LICENSE.md).
