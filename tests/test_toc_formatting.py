from pdftoceditor.pdftoceditor import (
    PageAlignment,
    TocEntry,
    calculate_max_page_width,
    format_toc_entry,
)


def test_calculate_max_page_width():
    """Test finding the longest page number string"""
    toc = [
        TocEntry(page="1", level="1.0", description="Chapter 1"),
        TocEntry(page="10", level="1.0", description="Chapter 2"),
        TocEntry(page="100", level="1.0", description="Chapter 3"),
    ]
    assert calculate_max_page_width(toc) == 3


def test_calculate_max_page_width_single_entry():
    """Test with single entry"""
    toc = [TocEntry(page="42", level="1.0", description="Answer")]
    assert calculate_max_page_width(toc) == 2


def test_format_toc_entry_right_align():
    """Test right-aligned formatting with padding"""
    entry = TocEntry(page="1", level="1.0", description="Introduction")
    result = format_toc_entry(entry, max_page_width=3, alignment=PageAlignment.RIGHT)
    assert result == "  1 Introduction"


def test_format_toc_entry_left_align():
    """Test left-aligned formatting"""
    entry = TocEntry(page="1", level="1.0", description="Introduction")
    result = format_toc_entry(entry, max_page_width=3, alignment=PageAlignment.LEFT)
    assert result == "1   Introduction"


def test_format_toc_entry_with_indentation():
    """Test level 2 indentation"""
    entry = TocEntry(page="2", level="2.0", description="Section")
    result = format_toc_entry(entry, max_page_width=2, alignment=PageAlignment.RIGHT)
    assert result == " 2   Section"


def test_format_toc_entry_no_padding():
    """Test when no padding is needed"""
    entry = TocEntry(page="100", level="1.0", description="Chapter")
    result = format_toc_entry(entry, max_page_width=3, alignment=PageAlignment.RIGHT)
    assert result == "100 Chapter"
