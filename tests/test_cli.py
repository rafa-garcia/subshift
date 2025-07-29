import sys
from unittest.mock import patch

import pytest

from subtune.cli import main
from subtune.core.exceptions import (
    FileProcessingError,
    InvalidOffsetError,
    InvalidSRTFormatError,
    InvalidTimestampError,
    SubtuneError,
)


class TestCLIArgumentParsing:
    def test_basic_arguments(self):
        with patch("sys.argv", ["subtune", "input.srt", "--offset", "1000"]):
            with patch("subtune.core.workflow.SubtitleProcessor.shift_srt_file") as mock_shift:
                with patch("builtins.print"):
                    mock_shift.return_value = 5
                    main()

                call_kwargs = mock_shift.call_args.kwargs
                assert str(call_kwargs["input_path"]).endswith("input.srt")
                assert str(call_kwargs["output_path"]).endswith("input.srt")  # Same file (in-place)
                assert call_kwargs["offset_ms"] == 1000
                assert call_kwargs["create_backup"] is False

    def test_output_argument(self):
        with patch(
            "sys.argv", ["subtune", "input.srt", "--offset", "1000", "--output", "output.srt"]
        ):
            with patch("subtune.core.workflow.SubtitleProcessor.shift_srt_file") as mock_shift:
                with patch("builtins.print"):
                    mock_shift.return_value = 5
                    main()

                call_kwargs = mock_shift.call_args.kwargs
                assert str(call_kwargs["input_path"]).endswith("input.srt")
                assert str(call_kwargs["output_path"]).endswith("output.srt")
                assert call_kwargs["offset_ms"] == 1000
                assert call_kwargs["create_backup"] is False

    def test_short_flags(self):
        with patch("sys.argv", ["subtune", "input.srt", "-o", "2000", "--output", "out.srt"]):
            with patch("subtune.core.workflow.SubtitleProcessor.shift_srt_file") as mock_shift:
                with patch("builtins.print"):
                    mock_shift.return_value = 5
                    main()

                call_kwargs = mock_shift.call_args.kwargs
                assert str(call_kwargs["input_path"]).endswith("input.srt")
                assert str(call_kwargs["output_path"]).endswith("out.srt")
                assert call_kwargs["offset_ms"] == 2000
                assert call_kwargs["create_backup"] is False

    def test_missing_offset_argument(self):
        with patch("sys.argv", ["subtune", "input.srt"]):
            with pytest.raises(SystemExit):
                main()

    def test_help_argument(self):
        with patch("sys.argv", ["subtune", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0  # Help should exit with code 0


class TestCLIBackupFunctionality:
    def test_backup_flag(self):
        with patch("sys.argv", ["subtune", "input.srt", "--offset", "1000", "--backup"]):
            with patch("subtune.core.workflow.SubtitleProcessor.shift_srt_file") as mock_shift:
                with patch("builtins.print"):
                    mock_shift.return_value = 5
                    main()

                call_kwargs = mock_shift.call_args.kwargs
                assert call_kwargs["create_backup"] is True

    def test_no_backup_by_default(self):
        with patch("sys.argv", ["subtune", "input.srt", "--offset", "1000"]):
            with patch("subtune.core.workflow.SubtitleProcessor.shift_srt_file") as mock_shift:
                with patch("builtins.print"):
                    mock_shift.return_value = 5
                    main()

                call_kwargs = mock_shift.call_args.kwargs
                assert call_kwargs["create_backup"] is False


class TestCLIErrorHandling:
    @pytest.mark.parametrize(
        "exception,exit_code,error_message",
        [
            (FileProcessingError("File not found"), 1, "File error: File not found"),
            (InvalidSRTFormatError("Bad format"), 2, "SRT format error: Bad format"),
            (InvalidTimestampError("Bad timestamp"), 3, "Timestamp error: Bad timestamp"),
            (InvalidOffsetError("Bad offset"), 4, "Offset error: Bad offset"),
            (SubtuneError("Generic error"), 5, "Error: Generic error"),
            (KeyboardInterrupt(), 130, "\nOperation cancelled by user"),
            (RuntimeError("Unexpected"), 99, "Unexpected error: Unexpected"),
        ],
    )
    @patch("builtins.print")
    def test_error_handling(self, mock_print, exception, exit_code, error_message):
        with patch("sys.argv", ["subtune", "input.srt", "--offset", "1000"]):
            with patch(
                "subtune.core.workflow.SubtitleProcessor.shift_srt_file", side_effect=exception
            ):
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == exit_code
                mock_print.assert_called_with(error_message, file=sys.stderr)


class TestCLISuccessMessages:
    @patch("subtune.core.workflow.SubtitleProcessor.shift_srt_file")
    @patch("builtins.print")
    def test_success_message_different_output(self, mock_print, mock_shift):
        mock_shift.return_value = 5
        with patch(
            "sys.argv", ["subtune", "input.srt", "--offset", "1000", "--output", "output.srt"]
        ):
            main()

        # Check success message
        success_calls = [
            call for call in mock_print.call_args_list if call[1].get("file") != sys.stderr
        ]
        assert any(
            "Shifted timestamps by 1000ms and saved to output.srt" in str(call)
            for call in success_calls
        )

    @patch("subtune.core.workflow.SubtitleProcessor.shift_srt_file")
    @patch("builtins.print")
    def test_success_message_in_place(self, mock_print, mock_shift):
        mock_shift.return_value = 5
        with patch("sys.argv", ["subtune", "input.srt", "--offset", "1000"]):
            main()

        # Check success message
        success_calls = [
            call for call in mock_print.call_args_list if call[1].get("file") != sys.stderr
        ]
        assert any("Shifted timestamps by 1000ms in-place" in str(call) for call in success_calls)


class TestCLIIntegration:
    def test_end_to_end_with_real_files(self, tmp_path):
        # Create test SRT file
        input_file = tmp_path / "test.srt"
        input_file.write_text("1\n00:00:01,000 --> 00:00:03,000\nTest subtitle\n")
        output_file = tmp_path / "output.srt"

        # Run CLI
        with patch(
            "sys.argv",
            ["subtune", str(input_file), "--offset", "1000", "--output", str(output_file)],
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
        with patch("sys.argv", ["subtune", str(input_file), "--offset", "1000", "--backup"]):
            with patch("builtins.print"):
                main()

        # Verify backup was created
        backup_file = input_file.with_suffix(".srt.backup")
        assert backup_file.exists()
        assert backup_file.read_text() == original_content

        # Verify original file was modified
        modified_content = input_file.read_text()
        assert "00:00:02,000 --> 00:00:04,000" in modified_content
