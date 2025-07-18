import pytest
from pathlib import Path


@pytest.fixture
def test_data_path():
    """Return the path to the test data directory"""
    return Path(__file__).parent / "data"


@pytest.fixture
def test_pdf_path(test_data_path):
    """Return the path to the test PDF file"""
    return test_data_path / "test_with_toc.pdf"


@pytest.fixture
def test_multi_page_pdf_path(test_data_path):
    """Return the path to the multi-page test PDF file"""
    return test_data_path / "test_multi_page_toc.pdf"