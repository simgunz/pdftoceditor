from pdftoceditor.pdftoceditor import dump_metadata


class TestDumpMetadata:
    """Test the dump_metadata function"""

    def test_dump_metadata_creates_file(self, test_pdf_path, tmp_path):
        """Test that dump_metadata creates a metadata file"""
        metadata_path = tmp_path / "metadata.txt"
        dump_metadata(test_pdf_path, metadata_path)

        # Check that the metadata file was created
        assert metadata_path.exists()
        assert metadata_path.name == "metadata.txt"

        # Check that the file contains expected metadata content
        content = metadata_path.read_text()
        assert len(content) > 0

        # Check for the complete bookmark section (what the app actually cares about)
        expected_bookmark_section = """BookmarkBegin
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
BookmarkPageNumber: 8"""

        # Verify the complete bookmark section is present
        assert expected_bookmark_section in content

    def test_dump_metadata_file_location(self, test_pdf_path, tmp_path):
        """Test that dump_metadata creates file in correct location"""
        expected_path = tmp_path / "metadata.txt"
        dump_metadata(test_pdf_path, expected_path)

        assert expected_path.exists()

    def test_dump_metadata_nonexistent_pdf(self, tmp_path):
        """Test dump_metadata with non-existent PDF file"""
        nonexistent_pdf = "nonexistent.pdf"
        expected_path = tmp_path / "metadata.txt"

        # Function should execute without error, but pdftk will fail silently
        dump_metadata(nonexistent_pdf, expected_path)
