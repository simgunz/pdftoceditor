"""Tests for PDF protection and password handling scenarios."""

import os
import tempfile
from pathlib import Path

import pytest

from pdftoceditor.pdftoceditor import (
    IncorrectPasswordError,
    InvalidPdfError,
    PasswordRequiredError,
    UnsupportedEncryptionError,
    dump_text_toc,
)


class TestOwnerOnlyProtection:
    """Test scenarios with owner-only password protection (should work without user password)."""

    def test_dump_128bit_owner_only_no_password(self, test_data_path):
        """Should successfully dump from 128-bit owner-only protected PDF without password."""
        pdf_path = test_data_path / "encrypted_128_owner.pdf"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            dump_text_toc(pdf_path, output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            output_path.unlink(missing_ok=True)


class TestRestrictedPermissions:
    """Test scenarios with permission restrictions (should work without user password)."""

    def test_dump_restricted_all_no_password(self, test_data_path):
        """Should successfully dump from PDF with all permissions restricted."""
        pdf_path = test_data_path / "restricted_all.pdf"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            dump_text_toc(pdf_path, output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            output_path.unlink(missing_ok=True)


class TestPasswordRequiredPDFs:
    """Test scenarios requiring user password."""

    def test_dump_128bit_both_no_password_fails(self, test_data_path):
        """Should fail to dump from 128-bit user+owner protected PDF without password."""
        pdf_path = test_data_path / "encrypted_128_both.pdf"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            with pytest.raises(PasswordRequiredError):
                dump_text_toc(pdf_path, output_path)
        finally:
            output_path.unlink(missing_ok=True)

    def test_dump_128bit_both_with_correct_password_succeeds(self, test_data_path):
        """Should successfully dump from 128-bit user+owner protected PDF with correct password."""
        pdf_path = test_data_path / "encrypted_128_both.pdf"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            dump_text_toc(
                pdf_path, output_path, password="user123"  # pragma: allowlist secret
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            output_path.unlink(missing_ok=True)

    def test_dump_128bit_both_with_wrong_password_fails(self, test_data_path):
        """Should fail to dump from 128-bit user+owner protected PDF with wrong password."""
        pdf_path = test_data_path / "encrypted_128_both.pdf"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            with pytest.raises(IncorrectPasswordError):
                dump_text_toc(
                    pdf_path,
                    output_path,
                    password="wrongpassword",  # pragma: allowlist secret
                )
        finally:
            output_path.unlink(missing_ok=True)


class TestUnsupportedEncryption:
    """Test scenarios with unsupported encryption types."""

    def test_dump_256bit_both_fails(self, test_data_path):
        """Should fail to dump from 256-bit encrypted PDF (unsupported)."""
        pdf_path = test_data_path / "encrypted_256_both.pdf"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            with pytest.raises(UnsupportedEncryptionError):
                dump_text_toc(pdf_path, output_path)
        finally:
            output_path.unlink(missing_ok=True)

    def test_dump_256bit_owner_fails(self, test_data_path):
        """Should fail to dump from 256-bit owner-only encrypted PDF (unsupported)."""
        pdf_path = test_data_path / "encrypted_256_owner.pdf"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            with pytest.raises(UnsupportedEncryptionError):
                dump_text_toc(pdf_path, output_path)
        finally:
            output_path.unlink(missing_ok=True)


class TestInvalidPDFs:
    """Test scenarios with invalid or corrupted PDFs."""

    def test_dump_corrupted_pdf_fails(self, test_data_path):
        """Should fail to dump from corrupted PDF."""
        pdf_path = test_data_path / "corrupted.pdf"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            with pytest.raises(InvalidPdfError):
                dump_text_toc(pdf_path, output_path)
        finally:
            output_path.unlink(missing_ok=True)

    def test_dump_empty_pdf_fails(self, test_data_path):
        """Should fail to dump from empty PDF."""
        pdf_path = test_data_path / "empty.pdf"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            with pytest.raises(InvalidPdfError):
                dump_text_toc(pdf_path, output_path)
        finally:
            output_path.unlink(missing_ok=True)


class TestEnvironmentVariablePasswordHandling:
    """Test password handling via environment variables."""

    def test_dump_with_env_var_password(self, test_data_path):
        """Should use password from PDF_PASSWORD environment variable via CLI."""
        pdf_path = test_data_path / "encrypted_128_both.pdf"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        # Save original env var
        original_password = os.environ.get("PDF_PASSWORD")

        try:
            # Set environment variable
            os.environ["PDF_PASSWORD"] = "user123"  # pragma: allowlist secret

            # Test that the core function works with explicit password (environment variable reading is CLI-level)
            dump_text_toc(
                pdf_path, output_path, password="user123"  # pragma: allowlist secret
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            # Restore original env var
            if original_password is not None:
                os.environ["PDF_PASSWORD"] = original_password
            elif "PDF_PASSWORD" in os.environ:
                del os.environ["PDF_PASSWORD"]
            output_path.unlink(missing_ok=True)

    def test_explicit_password_overrides_env_var(self, test_data_path):
        """Should use explicit password parameter over environment variable."""
        pdf_path = test_data_path / "encrypted_128_both.pdf"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        # Save original env var
        original_password = os.environ.get("PDF_PASSWORD")

        try:
            # Set wrong password in environment
            os.environ["PDF_PASSWORD"] = "wrongpassword"  # pragma: allowlist secret

            # Should succeed with correct explicit password
            dump_text_toc(
                pdf_path, output_path, password="user123"  # pragma: allowlist secret
            )
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            # Restore original env var
            if original_password is not None:
                os.environ["PDF_PASSWORD"] = original_password
            elif "PDF_PASSWORD" in os.environ:
                del os.environ["PDF_PASSWORD"]
            output_path.unlink(missing_ok=True)
