from pdftoceditor.pdftoceditor import load_metadata_toc


class TestTocFromMetadata:
    """Test the toc_from_metadata function"""

    def test_toc_from_metadata_basic(self, tmp_path):
        """Test parsing basic table of contents from metadata using actual test PDF metadata"""
        # Use actual metadata from our test PDF
        sample_metadata = """InfoBegin
InfoKey: Creator
InfoValue: LaTeX with hyperref
InfoBegin
InfoKey: Producer
InfoValue: pdfTeX-1.40.27
NumberOfPages: 8
BookmarkBegin
BookmarkTitle: Introduction
BookmarkLevel: 1
BookmarkPageNumber: 2
BookmarkBegin
BookmarkTitle: Background
BookmarkLevel: 2
BookmarkPageNumber: 3
BookmarkBegin
BookmarkTitle: Motivation
BookmarkLevel: 2
BookmarkPageNumber: 4
BookmarkBegin
BookmarkTitle: Methodology
BookmarkLevel: 1
BookmarkPageNumber: 5
BookmarkBegin
BookmarkTitle: Data Collection
BookmarkLevel: 2
BookmarkPageNumber: 6
BookmarkBegin
BookmarkTitle: Results
BookmarkLevel: 1
BookmarkPageNumber: 7
BookmarkBegin
BookmarkTitle: Conclusion
BookmarkLevel: 1
BookmarkPageNumber: 8
"""

        metadata_file = tmp_path / "metadata.txt"
        metadata_file.write_text(sample_metadata)

        toc = load_metadata_toc(metadata_file)

        # Check that we got the expected number of entries
        assert len(toc) == 7

        # Check entries in sorted order by page number
        assert toc[0] == ("2", "1", "Introduction")
        assert toc[1] == ("3", "2", "Background")
        assert toc[2] == ("4", "2", "Motivation")
        assert toc[3] == ("5", "1", "Methodology")
        assert toc[4] == ("6", "2", "Data Collection")
        assert toc[5] == ("7", "1", "Results")
        assert toc[6] == ("8", "1", "Conclusion")

        # Check that entries are sorted by page number
        page_numbers = [int(entry[0]) for entry in toc]
        assert page_numbers == sorted(page_numbers)

    def test_toc_from_metadata_empty_file(self, tmp_path):
        """Test parsing empty metadata file"""
        metadata_file = tmp_path / "empty_metadata.txt"
        metadata_file.write_text("")

        toc = load_metadata_toc(metadata_file)
        assert toc == []

    def test_toc_from_metadata_no_bookmarks(self, tmp_path):
        """Test parsing metadata file with no bookmarks"""
        metadata_no_bookmarks = """InfoBegin
InfoKey: Creator
InfoValue: LaTeX with hyperref
InfoBegin
InfoKey: Producer
InfoValue: pdfTeX-1.40.25
NumberOfPages: 5
"""

        metadata_file = tmp_path / "no_bookmarks.txt"
        metadata_file.write_text(metadata_no_bookmarks)

        toc = load_metadata_toc(metadata_file)
        assert toc == []

    def test_toc_from_metadata_sorting(self, tmp_path):
        """Test that entries are sorted by page number"""
        # Create metadata with bookmarks in non-sequential order
        unsorted_metadata = """BookmarkBegin
BookmarkTitle: Chapter 3
BookmarkLevel: 1
BookmarkPageNumber: 15
BookmarkBegin
BookmarkTitle: Chapter 1
BookmarkLevel: 1
BookmarkPageNumber: 1
BookmarkBegin
BookmarkTitle: Chapter 2
BookmarkLevel: 1
BookmarkPageNumber: 8
"""

        metadata_file = tmp_path / "unsorted.txt"
        metadata_file.write_text(unsorted_metadata)

        toc = load_metadata_toc(metadata_file)

        # Check that entries are sorted by page number
        assert len(toc) == 3
        assert toc[0] == ("1", "1", "Chapter 1")
        assert toc[1] == ("8", "1", "Chapter 2")
        assert toc[2] == ("15", "1", "Chapter 3")
