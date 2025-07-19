import pytest

from pdftoceditor.pdftoceditor import strip_meta_desc


def test_strip_meta_desc_basic_bookmark_title():
    """Test extracting value from BookmarkTitle entry"""
    metadata_entry = "BookmarkTitle: Introduction"
    result = strip_meta_desc(metadata_entry)
    assert result == "Introduction"


def test_strip_meta_desc_basic_bookmark_level():
    """Test extracting value from BookmarkLevel entry"""
    metadata_entry = "BookmarkLevel: 1"
    result = strip_meta_desc(metadata_entry)
    assert result == "1"


def test_strip_meta_desc_basic_bookmark_page():
    """Test extracting value from BookmarkPageNumber entry"""
    metadata_entry = "BookmarkPageNumber: 42"
    result = strip_meta_desc(metadata_entry)
    assert result == "42"


def test_strip_meta_desc_with_newline():
    """Test extracting value from entry with trailing newline"""
    metadata_entry = "BookmarkTitle: Chapter 1\n"
    result = strip_meta_desc(metadata_entry)
    assert result == "Chapter 1"


def test_strip_meta_desc_with_spaces_in_value():
    """Test extracting value with spaces"""
    metadata_entry = "BookmarkTitle: Chapter 1: Introduction to Python"
    result = strip_meta_desc(metadata_entry)
    assert result == "Chapter 1: Introduction to Python"


def test_strip_meta_desc_with_empty_value():
    """Test extracting empty value"""
    metadata_entry = "BookmarkTitle: "
    result = strip_meta_desc(metadata_entry)
    assert result == ""


def test_strip_meta_desc_with_multiple_colons_in_value():
    """Test extracting value that contains colons"""
    metadata_entry = "BookmarkTitle: Chapter 1: Section 2: Subsection 3"
    result = strip_meta_desc(metadata_entry)
    assert result == "Chapter 1: Section 2: Subsection 3"


def test_strip_meta_desc_with_special_characters():
    """Test extracting value with special characters"""
    metadata_entry = "BookmarkTitle: Chapter 1 (Advanced): Éxamples & More!"
    result = strip_meta_desc(metadata_entry)
    assert result == "Chapter 1 (Advanced): Éxamples & More!"


def test_strip_meta_desc_with_leading_trailing_spaces():
    """Test extracting value with leading/trailing spaces"""
    metadata_entry = "BookmarkTitle:   Chapter 1   "
    result = strip_meta_desc(metadata_entry)
    assert result == "  Chapter 1   "


def test_strip_meta_desc_no_colon_raises_error():
    """Test that malformed entry (no colon) raises ValueError"""
    metadata_entry = "BookmarkTitle Introduction"
    with pytest.raises(ValueError, match="Invalid metadata format"):
        strip_meta_desc(metadata_entry)


def test_strip_meta_desc_empty_string_raises_error():
    """Test that empty string raises ValueError"""
    metadata_entry = ""
    with pytest.raises(ValueError, match="Invalid metadata format"):
        strip_meta_desc(metadata_entry)


def test_strip_meta_desc_only_colon_raises_error():
    """Test that string with only colon raises ValueError"""
    metadata_entry = ":"
    with pytest.raises(ValueError, match="Invalid metadata format"):
        strip_meta_desc(metadata_entry)


def test_strip_meta_desc_colon_at_start():
    """Test string starting with colon"""
    metadata_entry = ": Some Value"
    result = strip_meta_desc(metadata_entry)
    assert result == "Some Value"
