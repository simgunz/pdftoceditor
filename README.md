This code allows to add a manually created index to a pdf file.

This will replace all the bookmarks in `mynotebook.pdf` with the one in `mynotebook.txt`
and creates a new file called `mynotebook-new.pdf`

    # Copy the pdf and the index in the folder work
    cd work
    ../update_toc.sh mynotebook.pdf

## Text index format


      1 First Chapter
      2   Section
      3     Subsection
     70 Second Chapter
    120 Third Chapter

Mind the leading spaces on the numbering column!

## Advanced feature

The function `add_toc_to_metadata` can be called with a flag to append
bookmarks instead of replacing them


## Notes

- Use only ASCII
