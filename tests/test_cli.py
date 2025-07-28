import sys
from unittest.mock import patch

import pytest

from subshift.cli import main
from subshift.exceptions import (
    FileProcessingError,
    InvalidOffsetError,
    InvalidSRTFormatError,
    InvalidTimestampError,
    SubshiftError,
)


class TestCLIArgumentParsing:
    def test_basic_arguments(self):
        with patch("sys.argv", ["subshift", "input.srt", "--offset", "1000"]):
            with patch("subshift.cli.shift_srt") as mock_shift:
                with patch("builtins.print"):
                    main()
                mock_shift.assert_called_once_with("input.srt", "input.srt", 1000)

    def test_output_argument(self):
        with patch(
            "sys.argv", ["subshift", "input.srt", "--offset", "1000", "--output", "output.srt"]
        ):
            with patch("subshift.cli.shift_srt") as mock_shift:
                with patch("builtins.print"):
                    main()
                mock_shift.assert_called_once_with("input.srt", "output.srt", 1000)

    def test_short_flags(self):
        with patch("sys.argv", ["subshift", "input.srt", "-s", "2000", "-o", "out.srt"]):
            with patch("subshift.cli.shift_srt") as mock_shift:
                with patch("builtins.print"):
                    main()
                mock_shift.assert_called_once_with("input.srt", "out.srt", 2000)

    def test_missing_offset_argument(self):
        with patch("sys.argv", ["subshift", "input.srt"]):
            with pytest.raises(SystemExit):
                main()

    def test_help_argument(self):
        with patch("sys.argv", ["subshift", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0  # Help should exit with code 0


class TestCLIBackupFunctionality:
    @patch("subshift.cli.shift_srt")
    @patch("shutil.copy2")
    @patch("builtins.print")
    def test_backup_flag(self, mock_print, mock_copy, mock_shift):
        with patch("sys.argv", ["subshift", "input.srt", "--offset", "1000", "--backup"]):
            main()

        mock_copy.assert_called_once()
        # Verify backup path creation
        call_args = mock_copy.call_args[0]
        assert call_args[0] == "input.srt"
        assert str(call_args[1]).endswith(".srt.backup")

    @patch("subshift.cli.shift_srt")
    @patch("shutil.copy2")
    @patch("builtins.print")
    def test_no_backup_by_default(self, mock_print, mock_copy, mock_shift):
        with patch("sys.argv", ["subshift", "input.srt", "--offset", "1000"]):
            main()

        mock_copy.assert_not_called()


class TestCLIErrorHandling:
    @pytest.mark.parametrize(
        "exception,exit_code,error_message",
        [
            (FileProcessingError("File not found"), 1, "File error: File not found"),
            (InvalidSRTFormatError("Bad format"), 2, "SRT format error: Bad format"),
            (InvalidTimestampError("Bad timestamp"), 3, "Timestamp error: Bad timestamp"),
            (InvalidOffsetError("Bad offset"), 4, "Offset error: Bad offset"),
            (SubshiftError("Generic error"), 5, "Error: Generic error"),
            (KeyboardInterrupt(), 130, "\nOperation cancelled by user"),
            (RuntimeError("Unexpected"), 99, "Unexpected error: Unexpected"),
        ],
    )
    @patch("builtins.print")
    def test_error_handling(self, mock_print, exception, exit_code, error_message):
        with patch("sys.argv", ["subshift", "input.srt", "--offset", "1000"]):
            with patch("subshift.cli.shift_srt", side_effect=exception):
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == exit_code
                mock_print.assert_called_with(error_message, file=sys.stderr)


class TestCLISuccessMessages:
    @patch("subshift.cli.shift_srt")
    @patch("builtins.print")
    def test_success_message_different_output(self, mock_print, mock_shift):
        with patch(
            "sys.argv", ["subshift", "input.srt", "--offset", "1000", "--output", "output.srt"]
        ):
            main()

        # Check success message
        success_calls = [
            call for call in mock_print.call_args_list if call[1].get("file") != sys.stderr
        ]
        assert any(
            "Subtitles shifted by 1000 ms and saved to output.srt" in str(call)
            for call in success_calls
        )

    @patch("subshift.cli.shift_srt")
    @patch("builtins.print")
    def test_success_message_in_place(self, mock_print, mock_shift):
        with patch("sys.argv", ["subshift", "input.srt", "--offset", "1000"]):
            main()

        # Check success message
        success_calls = [
            call for call in mock_print.call_args_list if call[1].get("file") != sys.stderr
        ]
        assert any("Subtitles shifted by 1000 ms in-place" in str(call) for call in success_calls)


class TestCLIIntegration:
    def test_end_to_end_with_real_files(self, tmp_path):
        # Create test SRT file
        input_file = tmp_path / "test.srt"
        input_file.write_text("1\n00:00:01,000 --> 00:00:03,000\nTest subtitle\n")
        output_file = tmp_path / "output.srt"

        # Run CLI
        with patch(
            "sys.argv",
            ["subshift", str(input_file), "--offset", "1000", "--output", str(output_file)],
        ):
            with patch("builtins.print"):
                main()

        # Verify output
        assert output_file.exists()
        content = output_file.read_text()
        assert "00:00:02,000 --> 00:00:04,000" in content
        assert "Test subtitle" in content

    def test_backup_integration(self, tmp_path):
        # Create test SRT file
        input_file = tmp_path / "test.srt"
        original_content = "1\n00:00:01,000 --> 00:00:03,000\nTest subtitle\n"
        input_file.write_text(original_content)

        # Run CLI with backup
        with patch("sys.argv", ["subshift", str(input_file), "--offset", "1000", "--backup"]):
            with patch("builtins.print"):
                main()

        # Verify backup was created
        backup_file = input_file.with_suffix(".srt.backup")
        assert backup_file.exists()
        assert backup_file.read_text() == original_content

        # Verify original file was modified
        modified_content = input_file.read_text()
        assert "00:00:02,000 --> 00:00:04,000" in modified_content
