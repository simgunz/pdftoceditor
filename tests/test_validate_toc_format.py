import pytest

from pdftoceditor.pdftoceditor import validate_toc_format


def test_validate_toc_format_valid_basic():
    """Test validation with valid basic ToC format"""
    lines = ["  1 Introduction", "  2 Methodology", "  3 Results"]
    # Should not raise any exception
    validate_toc_format(lines)


def test_validate_toc_format_valid_with_subsections():
    """Test validation with valid ToC including subsections"""
    lines = [
        "  1 Chapter 1",
        "  2   Section 1.1",
        "  3     Subsection 1.1.1",
        "  4   Section 1.2",
        " 10 Chapter 2",
    ]
    # Should not raise any exception
    validate_toc_format(lines)


def test_validate_toc_format_valid_large_page_numbers():
    """Test validation with large page numbers"""
    lines = ["100 Chapter 1", "101 Chapter 2", "999 Chapter 3"]
    # Should not raise any exception
    validate_toc_format(lines)


def test_validate_toc_format_empty_file():
    """Test validation fails for empty file"""
    lines = []
    with pytest.raises(ValueError, match="ToC file cannot be empty"):
        validate_toc_format(lines)


def test_validate_toc_format_whitespace_only():
    """Test validation fails for file with only whitespace"""
    lines = ["", "   ", "\t", "  \n  "]
    with pytest.raises(ValueError, match="ToC file cannot be empty"):
        validate_toc_format(lines)


def test_validate_toc_format_invalid_line_format():
    """Test validation fails for invalid line format"""
    lines = ["  1 Introduction", "Not a valid ToC line", "  3 Results"]
    with pytest.raises(
        ValueError, match="Line 2 has invalid format: 'Not a valid ToC line'"
    ):
        validate_toc_format(lines)


def test_validate_toc_format_missing_page_number():
    """Test validation fails for line missing page number"""
    lines = ["  1 Introduction", "    Missing page number", "  3 Results"]
    with pytest.raises(ValueError, match="Line 2 has invalid format"):
        validate_toc_format(lines)


def test_validate_toc_format_misaligned_pages():
    """Test validation fails for misaligned page numbers"""
    lines = [
        "  1 Chapter 1",  # 3 total chars
        " 10 Chapter 2",  # 3 total chars
        "100 Chapter 3",  # 3 total chars - this should be aligned
    ]
    # This should actually pass - all have 3 characters
    validate_toc_format(lines)

    # Now test misaligned
    misaligned_lines = [
        "  1 Chapter 1",  # 3 total chars
        " 10 Chapter 2",  # 3 total chars
        "1000 Chapter 3",  # 4 total chars - misaligned!
    ]
    with pytest.raises(ValueError, match="Page numbers are not properly aligned"):
        validate_toc_format(misaligned_lines)


def test_validate_toc_format_inconsistent_alignment():
    """Test validation fails for inconsistent page number alignment"""
    lines = [
        "1 Chapter 1",  # 1 total char
        "10 Chapter 2",  # 2 total chars - different length!
        "100 Chapter 3",  # 3 total chars - different length!
    ]
    with pytest.raises(ValueError, match="Page numbers are not properly aligned"):
        validate_toc_format(lines)


def test_validate_toc_format_mixed_valid_invalid():
    """Test validation stops at first invalid line"""
    lines = [
        "  1 Introduction",
        "Invalid line here",
        "  3 Results",
        "Another invalid line",  # This should not be reached
    ]
    with pytest.raises(
        ValueError, match="Line 2 has invalid format: 'Invalid line here'"
    ):
        validate_toc_format(lines)


def test_validate_toc_format_ignores_empty_lines():
    """Test validation ignores empty lines between valid content"""
    lines = [
        "",
        "  1 Introduction",
        "",
        "  2 Methodology",
        "   ",  # whitespace only
        "  3 Results",
        "",
    ]
    # Should not raise any exception - empty lines are ignored
    validate_toc_format(lines)


def test_validate_toc_format_zero_page_number():
    """Test validation allows zero page numbers"""
    lines = ["  0 Preface", "  1 Introduction"]
    # Should not raise any exception
    validate_toc_format(lines)


def test_validate_toc_format_single_entry():
    """Test validation works with single entry"""
    lines = ["  1 Only Chapter"]
    # Should not raise any exception
    validate_toc_format(lines)
