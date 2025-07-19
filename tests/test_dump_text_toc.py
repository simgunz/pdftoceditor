from pathlib import Path

from pdftoceditor.pdftoceditor import dump_text_toc


class TestDumpTextToc:
    """Test the dump_text_toc function"""

    def test_dump_text_toc_default_output(self, test_pdf_path, tmp_path):
        """Test dumping ToC to default output file"""
        # Change to tmp_path to control where the output file is created
        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(tmp_path)

            # Use a copy of the test PDF in tmp_path
            test_pdf_copy = tmp_path / "test.pdf"
            test_pdf_copy.write_bytes(test_pdf_path.read_bytes())

            dump_text_toc(test_pdf_copy)

            # Check that the output file was created with .txt extension
            output_file = tmp_path / "test.txt"
            assert output_file.exists()

            # Check that the file contains ToC content
            content = output_file.read_text()
            assert len(content) > 0

            # Check for expected ToC structure (page numbers and titles)
            lines = content.strip().split("\n")
            assert len(lines) > 0

            # Should contain the expected ToC content
            expected_content = """2 Introduction
3   Background
4   Motivation
5 Methodology
6   Data Collection
7 Results
8 Conclusion"""
            assert expected_content in content

        finally:
            os.chdir(original_cwd)

    def test_dump_text_toc_custom_output(self, test_pdf_path, tmp_path):
        """Test dumping ToC to custom output file"""
        output_file = tmp_path / "custom_toc.txt"

        dump_text_toc(test_pdf_path, output_file)

        # Check that the custom output file was created
        assert output_file.exists()

        # Check that the file contains ToC content
        content = output_file.read_text()
        assert len(content) > 0

        # Check for expected ToC structure - should contain the expected ToC content
        expected_content = """2 Introduction
3   Background
4   Motivation
5 Methodology
6   Data Collection
7 Results
8 Conclusion"""
        assert expected_content in content

    def test_dump_text_toc_align_left(self, test_multi_page_pdf_path, tmp_path):
        """Test dumping ToC with left-aligned page numbers"""
        output_file = tmp_path / "left_aligned_toc.txt"

        dump_text_toc(test_multi_page_pdf_path, output_file, align_page_left=True)

        # Check that the output file was created
        assert output_file.exists()

        # Check that the file contains ToC content
        content = output_file.read_text()
        assert len(content) > 0

        # Check for expected ToC structure with left-aligned page numbers
        expected_content = """2  Introduction
3    Background
4    Motivation
5  Methodology
6    Data Collection
7    Analysis
8  Results
9    Discussion
10 Conclusion
11 References
12 Appendix"""
        assert expected_content in content

    def test_dump_text_toc_align_right(self, test_multi_page_pdf_path, tmp_path):
        """Test dumping ToC with right-aligned page numbers (default)"""
        output_file = tmp_path / "right_aligned_toc.txt"

        dump_text_toc(test_multi_page_pdf_path, output_file, align_page_left=False)

        # Check that the output file was created
        assert output_file.exists()

        # Check that the file contains ToC content
        content = output_file.read_text()
        assert len(content) > 0

        # Check for expected ToC structure with right-aligned page numbers
        expected_content = """ 2 Introduction
 3   Background
 4   Motivation
 5 Methodology
 6   Data Collection
 7   Analysis
 8 Results
 9   Discussion
10 Conclusion
11 References
12 Appendix"""
        assert expected_content in content
