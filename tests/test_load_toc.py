import pytest

from pdftoceditor.pdftoceditor import load_text_toc


class TestLoadToc:
    """Test the load_toc function"""

    def test_load_toc_basic(self, tmp_path):
        """Test loading basic table of contents from text file"""
        toc_content = """  1 Introduction
  2   Background
  3   Motivation
  4 Methodology
  5 Results"""

        toc_file = tmp_path / "test_toc.txt"
        toc_file.write_text(toc_content)

        toc = load_text_toc(toc_file)

        # Check that we got the expected number of entries
        assert len(toc) == 5

        # Check entries
        assert toc[0] == ("Introduction", "1.0", "  1")
        assert toc[1] == ("Background", "2.0", "  2")  # Subsection (2 spaces)
        assert toc[2] == ("Motivation", "2.0", "  3")  # Subsection (2 spaces)
        assert toc[3] == ("Methodology", "1.0", "  4")
        assert toc[4] == ("Results", "1.0", "  5")

    def test_load_toc_with_subsections(self, tmp_path):
        """Test loading table of contents with multiple levels"""
        toc_content = """  1 Chapter 1
  2   Section 1.1
  3     Subsection 1.1.1
  4     Subsection 1.1.2
  5   Section 1.2
 10 Chapter 2"""

        toc_file = tmp_path / "toc_with_subsections.txt"
        toc_file.write_text(toc_content)

        toc = load_text_toc(toc_file)

        assert len(toc) == 6

        # Check levels
        assert toc[0] == ("Chapter 1", "1.0", "  1")  # Level 1
        assert toc[1] == ("Section 1.1", "2.0", "  2")  # Level 2 (2 spaces)
        assert toc[2] == ("Subsection 1.1.1", "3.0", "  3")  # Level 3 (4 spaces)
        assert toc[3] == ("Subsection 1.1.2", "3.0", "  4")  # Level 3 (4 spaces)
        assert toc[4] == ("Section 1.2", "2.0", "  5")  # Level 2 (2 spaces)
        assert toc[5] == ("Chapter 2", "1.0", " 10")  # Level 1

    def test_load_toc_misaligned_pages(self, tmp_path):
        """Test that misaligned page numbers raise an exception"""
        misaligned_content = """1 Chapter 1
 10 Chapter 2
100 Chapter 3"""

        toc_file = tmp_path / "misaligned.txt"
        toc_file.write_text(misaligned_content)

        with pytest.raises(Exception, match="Page numbers are not properly aligned"):
            load_text_toc(toc_file)

    def test_load_toc_empty_file(self, tmp_path):
        """Test loading empty table of contents file"""
        toc_file = tmp_path / "empty_toc.txt"
        toc_file.write_text("")

        # Empty file should raise an exception due to page alignment check
        with pytest.raises(Exception, match="Page numbers are not properly aligned"):
            load_text_toc(toc_file)

    def test_load_toc_whitespace_only(self, tmp_path):
        """Test loading file with only whitespace"""
        toc_file = tmp_path / "whitespace_toc.txt"
        toc_file.write_text("   \n  \n\t\n")

        # File with only whitespace should raise an exception due to page alignment check
        with pytest.raises(Exception, match="Page numbers are not properly aligned"):
            load_text_toc(toc_file)

    def test_load_toc_large_page_numbers(self, tmp_path):
        """Test loading ToC with large page numbers"""
        toc_content = """100 Chapter 1
101   Section 1.1
999 Chapter 2"""

        toc_file = tmp_path / "large_pages.txt"
        toc_file.write_text(toc_content)

        toc = load_text_toc(toc_file)

        assert len(toc) == 3
        assert toc[0] == ("Chapter 1", "1.0", "100")
        assert toc[1] == ("Section 1.1", "2.0", "101")
        assert toc[2] == ("Chapter 2", "1.0", "999")
