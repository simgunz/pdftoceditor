from pathlib import Path

import pytest


@pytest.fixture
def test_data_path():
    """Return the path to the test data directory"""
    return Path(__file__).parent / "data"


@pytest.fixture
def basic_no_toc_pdf_path(test_data_path):
    """Return the path to the simple PDF with no TOC"""
    return test_data_path / "basic_no_toc.pdf"


@pytest.fixture
def basic_with_toc_pdf_path(test_data_path):
    """Return the path to the test PDF file"""
    return test_data_path / "basic_with_toc.pdf"


@pytest.fixture
def double_digit_pages_with_toc_pdf_path(test_data_path):
    """Return the path to the multi-page test PDF file"""
    return test_data_path / "double_digit_pages_with_toc.pdf"
