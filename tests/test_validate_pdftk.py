import shutil
from unittest.mock import patch

import pytest

from pdftoceditor.pdftoceditor import validate_pdftk_installed


def test_validate_pdftk_when_installed():
    with patch.object(shutil, "which", return_value="/usr/bin/pdftk"):
        # Should not raise any exception
        validate_pdftk_installed()


def test_validate_pdftk_when_not_installed():
    with patch.object(shutil, "which", return_value=None):
        with pytest.raises(FileNotFoundError) as exc_info:
            validate_pdftk_installed()

        error_message = str(exc_info.value)
        assert "pdftk command not found" in error_message
