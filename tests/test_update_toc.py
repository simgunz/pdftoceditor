import tempfile
from pathlib import Path

import pytest

from pdftoceditor.pdftoceditor import dump_text_toc, update_toc


def test_append_toc_to_empty_pdf_same_as_replace(basic_no_toc_pdf_path, tmp_path):
    """Test appending ToC to PDF with no existing bookmarks - should behave same as replace"""
    test_pdf = tmp_path / "test_input.pdf"
    test_pdf.write_bytes(basic_no_toc_pdf_path.read_bytes())

    # Create a simple ToC file
    toc_content = """  1 Introduction
  2 Conclusion"""
    toc_file = tmp_path / "new_toc.txt"
    toc_file.write_text(toc_content)

    output_pdf = tmp_path / "output.pdf"

    # Append ToC to empty PDF - should add the ToC
    update_toc(test_pdf, toc_file, output_pdf, replace_toc=False)

    # Verify output PDF exists
    assert output_pdf.exists()

    # Verify the ToC was added by dumping it back
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete=False
    ) as temp_file:
        temp_path = Path(temp_file.name)

    dump_text_toc(output_pdf, temp_path)
    result_content = temp_path.read_text().strip()

    # Should contain the appended entries
    assert "Introduction" in result_content
    assert "Conclusion" in result_content


def test_append_toc_to_pdf_with_existing_toc(basic_no_toc_pdf_path, tmp_path):
    """Test appending ToC to PDF that already has bookmarks"""
    test_pdf = tmp_path / "test_input.pdf"
    test_pdf.write_bytes(basic_no_toc_pdf_path.read_bytes())

    # Add initial ToC
    initial_toc_content = """  1 Chapter 1
  5 Chapter 2"""
    initial_toc_file = tmp_path / "initial_toc.txt"
    initial_toc_file.write_text(initial_toc_content)

    intermediate_pdf = tmp_path / "intermediate.pdf"
    update_toc(test_pdf, initial_toc_file, intermediate_pdf, replace_toc=True)

    # Now append additional ToC entries
    additional_toc_content = """  3 Section 1.1
  7 Appendix"""
    additional_toc_file = tmp_path / "additional_toc.txt"
    additional_toc_file.write_text(additional_toc_content)

    final_pdf = tmp_path / "final.pdf"
    update_toc(intermediate_pdf, additional_toc_file, final_pdf, replace_toc=False)

    # Verify all entries are present and sorted by page
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete=False
    ) as temp_file:
        temp_path = Path(temp_file.name)

    dump_text_toc(final_pdf, temp_path)
    result_content = temp_path.read_text()

    # Check all entries are present
    assert "Chapter 1" in result_content
    assert "Section 1.1" in result_content
    assert "Chapter 2" in result_content
    assert "Appendix" in result_content


def test_append_toc_default_output_path(basic_no_toc_pdf_path, tmp_path):
    """Test append ToC with default output path generation"""
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_bytes(basic_no_toc_pdf_path.read_bytes())

    toc_content = """  1 Test Chapter"""
    toc_file = tmp_path / "toc.txt"
    toc_file.write_text(toc_content)

    # Don't specify output path - should create file with _updated_toc suffix
    update_toc(test_pdf, toc_file, replace_toc=False)

    expected_output = test_pdf.with_stem("test_updated_toc")
    assert expected_output.exists()


def test_replace_empty_toc_adds_toc(basic_no_toc_pdf_path, tmp_path):
    """Test replacing ToC in PDF with no existing bookmarks - should add the ToC"""
    test_pdf = tmp_path / "test_input.pdf"
    test_pdf.write_bytes(basic_no_toc_pdf_path.read_bytes())

    toc_content = """  1 New Chapter
  2   New Section
  3 Another Chapter"""
    toc_file = tmp_path / "replacement_toc.txt"
    toc_file.write_text(toc_content)

    output_pdf = tmp_path / "output.pdf"

    # Replace ToC in empty PDF - should add the ToC
    update_toc(test_pdf, toc_file, output_pdf, replace_toc=True)

    # Verify the ToC was added
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete=False
    ) as temp_file:
        temp_path = Path(temp_file.name)

    dump_text_toc(output_pdf, temp_path)
    result_content = temp_path.read_text().strip()

    # Should contain the replacement entries
    assert "New Chapter" in result_content
    assert "New Section" in result_content
    assert "Another Chapter" in result_content


def test_replace_existing_toc(basic_no_toc_pdf_path, tmp_path):
    """Test replacing existing ToC completely"""
    test_pdf = tmp_path / "test_input.pdf"
    test_pdf.write_bytes(basic_no_toc_pdf_path.read_bytes())

    # Add initial ToC
    initial_toc_content = """  1 Old Chapter 1
  2 Old Chapter 2
  3 Old Chapter 3"""
    initial_toc_file = tmp_path / "initial_toc.txt"
    initial_toc_file.write_text(initial_toc_content)

    intermediate_pdf = tmp_path / "intermediate.pdf"
    update_toc(test_pdf, initial_toc_file, intermediate_pdf, replace_toc=True)

    # Replace with completely new ToC
    replacement_toc_content = """  5 New Chapter A
 10 New Chapter B"""
    replacement_toc_file = tmp_path / "replacement_toc.txt"
    replacement_toc_file.write_text(replacement_toc_content)

    final_pdf = tmp_path / "final.pdf"
    update_toc(intermediate_pdf, replacement_toc_file, final_pdf, replace_toc=True)

    # Verify only new entries are present
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete=False
    ) as temp_file:
        temp_path = Path(temp_file.name)

    dump_text_toc(final_pdf, temp_path)
    result_content = temp_path.read_text()

    # Should only contain replacement entries
    assert "New Chapter A" in result_content
    assert "New Chapter B" in result_content

    # Should NOT contain old entries
    assert "Old Chapter" not in result_content


def test_replace_with_complex_hierarchy(basic_no_toc_pdf_path, tmp_path):
    """Test replacing ToC with complex multi-level hierarchy"""
    test_pdf = tmp_path / "test_input.pdf"
    test_pdf.write_bytes(basic_no_toc_pdf_path.read_bytes())

    complex_toc_content = """  1 Chapter 1
  2   Section 1.1
  3     Subsection 1.1.1
  4     Subsection 1.1.2
  5   Section 1.2
 10 Chapter 2
 11   Section 2.1"""
    toc_file = tmp_path / "complex_toc.txt"
    toc_file.write_text(complex_toc_content)

    output_pdf = tmp_path / "output.pdf"
    update_toc(test_pdf, toc_file, output_pdf, replace_toc=True)

    # Verify the PDF was created successfully
    assert output_pdf.exists()

    # Verify we can dump the ToC back and it contains expected content
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete=False
    ) as temp_file:
        temp_path = Path(temp_file.name)

    dump_text_toc(output_pdf, temp_path)
    result_content = temp_path.read_text()

    # Should contain all the hierarchical entries
    assert "Chapter 1" in result_content
    assert "Section 1.1" in result_content
    assert "Subsection 1.1.1" in result_content
    assert "Subsection 1.1.2" in result_content
    assert "Section 1.2" in result_content
    assert "Chapter 2" in result_content
    assert "Section 2.1" in result_content


def test_update_toc_with_invalid_toc_format_should_fail(
    basic_no_toc_pdf_path, tmp_path
):
    """Test that update_toc fails gracefully with invalid ToC format"""
    test_pdf = tmp_path / "test_input.pdf"
    test_pdf.write_bytes(basic_no_toc_pdf_path.read_bytes())

    # Create an invalid ToC file (missing page numbers)
    invalid_toc_content = """Introduction
Chapter 1
Conclusion"""
    toc_file = tmp_path / "invalid_toc.txt"
    toc_file.write_text(invalid_toc_content)

    output_pdf = tmp_path / "output.pdf"

    # This should raise an exception due to invalid format
    with pytest.raises(ValueError, match="Line .* has invalid format"):
        update_toc(test_pdf, toc_file, output_pdf, replace_toc=True)


def test_update_toc_with_empty_toc_file_should_fail(basic_no_toc_pdf_path, tmp_path):
    """Test that update_toc fails gracefully with empty ToC file"""
    test_pdf = tmp_path / "test_input.pdf"
    test_pdf.write_bytes(basic_no_toc_pdf_path.read_bytes())

    # Create an empty ToC file
    toc_file = tmp_path / "empty_toc.txt"
    toc_file.write_text("")

    output_pdf = tmp_path / "output.pdf"

    # This should raise an exception due to empty file
    with pytest.raises(ValueError, match="ToC file cannot be empty"):
        update_toc(test_pdf, toc_file, output_pdf, replace_toc=True)
