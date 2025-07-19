"""Tests for the --in-place option in CLI commands."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from pdftoceditor.cli import app

runner = CliRunner()


class TestInPlaceOption:
    """Test the --in-place option functionality."""

    def test_replace_with_in_place_option(self, tmp_path):
        """Test replace command with --in-place option."""
        # Create test files
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("fake pdf content")
        test_toc = tmp_path / "toc.txt"
        test_toc.write_text("1 Chapter One")

        with patch("shutil.which", return_value="/usr/bin/pdftk"):
            with patch("subprocess.run") as mock_subprocess:
                result = runner.invoke(
                    app, ["replace", str(test_pdf), str(test_toc), "--in-place"]
                )

                # Should succeed
                assert result.exit_code == 0
                # Should have called subprocess (pdftk)
                assert mock_subprocess.called

    def test_append_with_in_place_option(self, tmp_path):
        """Test append command with --in-place option."""
        # Create test files
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("fake pdf content")
        test_toc = tmp_path / "toc.txt"
        test_toc.write_text("1 Chapter One")

        with patch("shutil.which", return_value="/usr/bin/pdftk"):
            with patch("subprocess.run") as mock_subprocess:
                result = runner.invoke(
                    app, ["append", str(test_pdf), str(test_toc), "--in-place"]
                )

                # Should succeed
                assert result.exit_code == 0
                # Should have called subprocess (pdftk)
                assert mock_subprocess.called

    def test_conflicting_output_and_in_place_options_replace(self, tmp_path):
        """Test that --output and --in-place options conflict in replace command."""
        # Create test files
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("fake pdf content")
        test_toc = tmp_path / "toc.txt"
        test_toc.write_text("1 Chapter One")
        output_pdf = tmp_path / "output.pdf"

        with patch("shutil.which", return_value="/usr/bin/pdftk"):
            result = runner.invoke(
                app,
                [
                    "replace",
                    str(test_pdf),
                    str(test_toc),
                    "--output",
                    str(output_pdf),
                    "--in-place",
                ],
            )

            # Should fail with error
            assert result.exit_code == 1
            assert (
                "Cannot use both --output and --in-place options together"
                in result.stderr
            )

    def test_conflicting_output_and_in_place_options_append(self, tmp_path):
        """Test that --output and --in-place options conflict in append command."""
        # Create test files
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("fake pdf content")
        test_toc = tmp_path / "toc.txt"
        test_toc.write_text("1 Chapter One")
        output_pdf = tmp_path / "output.pdf"

        with patch("shutil.which", return_value="/usr/bin/pdftk"):
            result = runner.invoke(
                app,
                [
                    "append",
                    str(test_pdf),
                    str(test_toc),
                    "--output",
                    str(output_pdf),
                    "--in-place",
                ],
            )

            # Should fail with error
            assert result.exit_code == 1
            assert (
                "Cannot use both --output and --in-place options together"
                in result.stderr
            )

    def test_in_place_short_option(self, tmp_path):
        """Test the short form -i for --in-place option."""
        # Create test files
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("fake pdf content")
        test_toc = tmp_path / "toc.txt"
        test_toc.write_text("1 Chapter One")

        with patch("shutil.which", return_value="/usr/bin/pdftk"):
            with patch("subprocess.run") as mock_subprocess:
                result = runner.invoke(
                    app, ["replace", str(test_pdf), str(test_toc), "-i"]
                )

                # Should succeed
                assert result.exit_code == 0
                # Should have called subprocess (pdftk)
                assert mock_subprocess.called

    def test_in_place_uses_temporary_file(self, tmp_path):
        """Test that in-place option uses temporary file to avoid pdftk input=output error."""
        # Create test files
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("fake pdf content")
        test_toc = tmp_path / "toc.txt"
        test_toc.write_text("1 Chapter One")

        # Track the subprocess calls to verify temp file usage
        subprocess_calls = []

        def mock_subprocess_run(*args, **kwargs):
            subprocess_calls.append(args[0])  # Store the command
            # Create a fake output file at the specified path
            if len(args[0]) >= 6 and args[0][-2] == "output":
                output_path = Path(args[0][-1])
                output_path.write_text("fake updated pdf")
            return type("Result", (), {"returncode": 0})()

        with patch("shutil.which", return_value="/usr/bin/pdftk"):
            with patch("subprocess.run", side_effect=mock_subprocess_run):
                with patch("shutil.move") as mock_move:
                    result = runner.invoke(
                        app, ["replace", str(test_pdf), str(test_toc), "--in-place"]
                    )

                    # Should succeed
                    assert result.exit_code == 0

                    # Should have called subprocess (pdftk)
                    assert len(subprocess_calls) >= 1

                    # The output path in the pdftk command should NOT be the same as input
                    pdftk_update_cmd = next(
                        (cmd for cmd in subprocess_calls if "update_info" in cmd), None
                    )
                    assert pdftk_update_cmd is not None

                    # Find input and output paths in the command
                    input_path = pdftk_update_cmd[1]  # pdftk INPUT_PATH ...
                    output_index = pdftk_update_cmd.index("output")
                    output_path = pdftk_update_cmd[output_index + 1]

                    # Output should be different from input (temporary file)
                    assert input_path != output_path
                    assert str(test_pdf) == input_path

                    # Should have called shutil.move to replace the original
                    assert mock_move.called
