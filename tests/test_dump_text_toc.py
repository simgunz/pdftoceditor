from pathlib import Path

import pytest

from pdftoceditor.pdftoceditor import EmptyTocError, PageAlignment, dump_text_toc


def test_dump_text_toc_default_output(basic_with_toc_pdf_path, tmp_path):
    """Test dumping ToC to default output file"""
    # Change to tmp_path to control where the output file is created
    original_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)

        # Use a copy of the test PDF in tmp_path
        test_pdf_copy = tmp_path / "test.pdf"
        test_pdf_copy.write_bytes(basic_with_toc_pdf_path.read_bytes())

        dump_text_toc(test_pdf_copy)

        # Check that the output file was created with _toc.txt extension
        output_file = tmp_path / "test_toc.txt"
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


def test_dump_text_toc_custom_output(basic_with_toc_pdf_path, tmp_path):
    """Test dumping ToC to custom output file"""
    output_file = tmp_path / "custom_toc.txt"

    dump_text_toc(basic_with_toc_pdf_path, output_file)

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


def test_dump_text_toc_align_left(double_digit_pages_with_toc_pdf_path, tmp_path):
    """Test dumping ToC with left-aligned page numbers"""
    output_file = tmp_path / "left_aligned_toc.txt"

    dump_text_toc(double_digit_pages_with_toc_pdf_path, output_file, PageAlignment.LEFT)

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


def test_dump_text_toc_align_right(double_digit_pages_with_toc_pdf_path, tmp_path):
    """Test dumping ToC with right-aligned page numbers (default)"""
    output_file = tmp_path / "right_aligned_toc.txt"

    dump_text_toc(
        double_digit_pages_with_toc_pdf_path, output_file, PageAlignment.RIGHT
    )

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


def test_dump_text_toc_empty_pdf_should_raise_empty_toc_error(
    basic_no_toc_pdf_path, tmp_path
):
    """Test dumping ToC from PDF with no bookmarks should raise EmptyTocError"""
    output_path = tmp_path / "empty_toc.txt"

    # This should raise EmptyTocError when trying to process empty ToC
    with pytest.raises(EmptyTocError):
        dump_text_toc(basic_no_toc_pdf_path, output_path)


def test_dump_text_toc_empty_pdf_default_output_should_raise_empty_toc_error(
    basic_no_toc_pdf_path, tmp_path
):
    """Test dumping empty ToC with default output path should raise EmptyTocError"""
    # Copy PDF to tmp_path so default output doesn't interfere
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_bytes(basic_no_toc_pdf_path.read_bytes())

    # This should raise EmptyTocError
    with pytest.raises(EmptyTocError):
        dump_text_toc(test_pdf)


def test_dump_text_toc_empty_pdf_with_alignment_should_raise_empty_toc_error(
    basic_no_toc_pdf_path, tmp_path
):
    """Test dumping empty ToC with alignment options should raise EmptyTocError"""
    output_left = tmp_path / "empty_left.txt"
    output_right = tmp_path / "empty_right.txt"

    # Both alignment options should raise EmptyTocError with empty TOC
    with pytest.raises(EmptyTocError):
        dump_text_toc(basic_no_toc_pdf_path, output_left, PageAlignment.LEFT)

    with pytest.raises(EmptyTocError):
        dump_text_toc(basic_no_toc_pdf_path, output_right, PageAlignment.RIGHT)
