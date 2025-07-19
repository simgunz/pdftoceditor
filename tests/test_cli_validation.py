import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from pdftoceditor.cli import app, validate_output_directory, validate_pdf_file

runner = CliRunner()


def test_validate_pdf_file_valid_extension():
    """Test PDF validation with valid .pdf extension"""
    valid_path = Path("test.pdf")
    result = validate_pdf_file(valid_path)
    assert result == valid_path


def test_validate_pdf_file_case_insensitive():
    """Test PDF validation is case insensitive"""
    valid_path = Path("test.PDF")
    result = validate_pdf_file(valid_path)
    assert result == valid_path


def test_validate_pdf_file_invalid_extension():
    """Test PDF validation rejects non-PDF files"""
    invalid_path = Path("test.txt")
    with pytest.raises(typer.BadParameter) as exc_info:
        validate_pdf_file(invalid_path)
    assert "must have .pdf extension" in str(exc_info.value)
    assert ".txt" in str(exc_info.value)


def test_validate_pdf_file_no_extension():
    """Test PDF validation rejects files without extension"""
    invalid_path = Path("test")
    with pytest.raises(typer.BadParameter) as exc_info:
        validate_pdf_file(invalid_path)
    assert "must have .pdf extension" in str(exc_info.value)


def test_validate_output_directory_nonexistent_fails(tmp_path):
    """Test output directory validation fails for nonexistent directories"""
    output_path = tmp_path / "nonexistent" / "output.txt"
    with pytest.raises(typer.BadParameter) as exc_info:
        validate_output_directory(output_path)
    assert "Output directory does not exist" in str(exc_info.value)


def test_validate_output_directory_current_dir_passes():
    """Test output directory validation passes for current directory"""
    output_path = Path("output.txt")
    # Should not raise any exception
    validate_output_directory(output_path)


def test_validate_output_directory_existing_dir_passes(tmp_path):
    """Test output directory validation passes for existing directories"""
    existing_dir = tmp_path / "existing"
    existing_dir.mkdir()
    output_path = existing_dir / "output.txt"
    # Should not raise any exception
    validate_output_directory(output_path)


def test_validate_output_directory_file_not_dir_fails(tmp_path):
    """Test output directory validation fails when parent is a file"""
    existing_file = tmp_path / "file.txt"
    existing_file.write_text("content")
    output_path = existing_file / "output.txt"
    with pytest.raises(typer.BadParameter) as exc_info:
        validate_output_directory(output_path)
    assert "is not a directory" in str(exc_info.value)


def test_cli_validates_pdf_extension():
    """Test CLI rejects non-PDF files"""
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        with patch("shutil.which", return_value="/usr/bin/pdftk"):
            result = runner.invoke(app, ["dump", temp_file.name])
            assert result.exit_code != 0
            assert "must have .pdf extension" in result.stderr


def test_cli_validates_file_exists():
    """Test CLI rejects non-existent files"""
    with patch("shutil.which", return_value="/usr/bin/pdftk"):
        result = runner.invoke(app, ["dump", "nonexistent.pdf"])
        assert result.exit_code != 0
        assert "does not exist" in result.stderr.lower()


def test_cli_validates_output_directory_exists(tmp_path):
    """Test CLI validates output directory exists"""
    # Create a valid PDF file for testing
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_text("fake pdf content")

    # Try to output to nonexistent directory
    output_path = tmp_path / "nonexistent" / "output.txt"

    with patch("shutil.which", return_value="/usr/bin/pdftk"):
        result = runner.invoke(
            app, ["dump", str(test_pdf), "--output-toc", str(output_path)]
        )

        # Should fail with directory validation error
        assert result.exit_code != 0
        assert "Output directory does not exist" in result.stderr


def test_cli_accepts_existing_output_directory(tmp_path):
    """Test CLI accepts output paths in existing directories"""
    # Create a valid PDF file for testing
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_text("fake pdf content")

    # Create existing output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    output_path = output_dir / "output.txt"

    with patch("shutil.which", return_value="/usr/bin/pdftk"):
        with patch("subprocess.run") as mock_subprocess:
            with patch("pdftoceditor.pdftoceditor.toc_from_metadata", return_value=[]):
                result = runner.invoke(
                    app, ["dump", str(test_pdf), "--output-toc", str(output_path)]
                )

                # Should succeed with existing directory
                assert result.exit_code == 0 or mock_subprocess.called
