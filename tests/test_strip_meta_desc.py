import pytest

from pdftoceditor.pdftoceditor import strip_meta_desc


class TestStripMetaDesc:
    """Test the strip_meta_desc function"""

    def test_strip_meta_desc_basic_bookmark_title(self):
        """Test extracting value from BookmarkTitle entry"""
        metadata_entry = "BookmarkTitle: Introduction"
        result = strip_meta_desc(metadata_entry)
        assert result == "Introduction"

    def test_strip_meta_desc_basic_bookmark_level(self):
        """Test extracting value from BookmarkLevel entry"""
        metadata_entry = "BookmarkLevel: 1"
        result = strip_meta_desc(metadata_entry)
        assert result == "1"

    def test_strip_meta_desc_basic_bookmark_page(self):
        """Test extracting value from BookmarkPageNumber entry"""
        metadata_entry = "BookmarkPageNumber: 42"
        result = strip_meta_desc(metadata_entry)
        assert result == "42"

    def test_strip_meta_desc_with_newline(self):
        """Test extracting value from entry with trailing newline"""
        metadata_entry = "BookmarkTitle: Chapter 1\n"
        result = strip_meta_desc(metadata_entry)
        assert result == "Chapter 1"

    def test_strip_meta_desc_with_spaces_in_value(self):
        """Test extracting value with spaces"""
        metadata_entry = "BookmarkTitle: Chapter 1: Introduction to Python"
        result = strip_meta_desc(metadata_entry)
        assert result == "Chapter 1: Introduction to Python"

    def test_strip_meta_desc_with_empty_value(self):
        """Test extracting empty value"""
        metadata_entry = "BookmarkTitle: "
        result = strip_meta_desc(metadata_entry)
        assert result == ""

    def test_strip_meta_desc_with_multiple_colons_in_value(self):
        """Test extracting value that contains colons"""
        metadata_entry = "BookmarkTitle: Chapter 1: Section 2: Subsection 3"
        result = strip_meta_desc(metadata_entry)
        assert result == "Chapter 1: Section 2: Subsection 3"

    def test_strip_meta_desc_with_special_characters(self):
        """Test extracting value with special characters"""
        metadata_entry = "BookmarkTitle: Chapter 1 (Advanced): Éxamples & More!"
        result = strip_meta_desc(metadata_entry)
        assert result == "Chapter 1 (Advanced): Éxamples & More!"

    def test_strip_meta_desc_with_leading_trailing_spaces(self):
        """Test extracting value with leading/trailing spaces"""
        metadata_entry = "BookmarkTitle:   Chapter 1   "
        result = strip_meta_desc(metadata_entry)
        assert result == "  Chapter 1   "

    def test_strip_meta_desc_no_colon_raises_error(self):
        """Test that malformed entry (no colon) raises AttributeError"""
        metadata_entry = "BookmarkTitle Introduction"
        with pytest.raises(AttributeError):
            strip_meta_desc(metadata_entry)

    def test_strip_meta_desc_empty_string_raises_error(self):
        """Test that empty string raises AttributeError"""
        metadata_entry = ""
        with pytest.raises(AttributeError):
            strip_meta_desc(metadata_entry)

    def test_strip_meta_desc_only_colon_raises_error(self):
        """Test that string with only colon raises AttributeError"""
        metadata_entry = ":"
        with pytest.raises(AttributeError):
            strip_meta_desc(metadata_entry)

    def test_strip_meta_desc_colon_at_start(self):
        """Test string starting with colon"""
        metadata_entry = ": Some Value"
        result = strip_meta_desc(metadata_entry)
        assert result == "Some Value"
