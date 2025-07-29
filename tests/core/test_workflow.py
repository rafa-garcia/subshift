import pytest

from subtune.core.exceptions import (
    FileProcessingError,
    InvalidOffsetError,
    InvalidSRTFormatError,
)
from subtune.core.validator import FileValidator
from subtune.core.workflow import SubtitleProcessor
from subtune.utils.backup import BackupManager


class TestSubtitleProcessor:
    def test_initialization(self):
        service = SubtitleProcessor()
        assert isinstance(service.validator, FileValidator)
        assert isinstance(service.backup_manager, BackupManager)

    def test_shift_srt_file_success(self, tmp_path, capsys):
        input_content = """1
00:00:01,000 --> 00:00:03,000
Test subtitle
"""
        input_file = tmp_path / "input.srt"
        input_file.write_text(input_content)

        output_file = tmp_path / "output.srt"

        service = SubtitleProcessor()
        result = service.shift_srt_file(input_file, output_file, 1000)

        assert result == 1  # One subtitle processed
        assert output_file.exists()

        content = output_file.read_text()
        assert "00:00:02,000 --> 00:00:04,000" in content

        captured = capsys.readouterr()
        assert "Successfully processed 1 subtitles" in captured.out

    def test_shift_srt_file_with_backup(self, tmp_path, capsys):
        input_content = """1
00:00:01,000 --> 00:00:03,000
Test subtitle
"""
        input_file = tmp_path / "input.srt"
        input_file.write_text(input_content)

        service = SubtitleProcessor()
        service.shift_srt_file(input_file, input_file, 1000, create_backup=True)

        backup_file = input_file.with_suffix(".srt.backup")
        assert backup_file.exists()
        assert backup_file.read_text() == input_content

        captured = capsys.readouterr()
        assert "Created backup:" in captured.out

    def test_shift_srt_file_input_validation_error(self, tmp_path):
        nonexistent = tmp_path / "nonexistent.srt"
        output_file = tmp_path / "output.srt"

        service = SubtitleProcessor()
        with pytest.raises(FileProcessingError, match="Input file does not exist"):
            service.shift_srt_file(nonexistent, output_file, 1000)

    def test_shift_srt_file_offset_validation_error(self, tmp_path):
        input_file = tmp_path / "input.srt"
        input_file.write_text("1\n00:00:01,000 --> 00:00:03,000\nTest\n")
        output_file = tmp_path / "output.srt"

        service = SubtitleProcessor()
        with pytest.raises(InvalidOffsetError, match="Offset must be a number"):
            service.shift_srt_file(input_file, output_file, "invalid")

    def test_shift_srt_file_srt_format_error(self, tmp_path):
        input_file = tmp_path / "invalid.srt"
        input_file.write_text("Not a valid SRT file")
        output_file = tmp_path / "output.srt"

        service = SubtitleProcessor()
        with pytest.raises(
            InvalidSRTFormatError, match="No valid SRT timestamp format found in file"
        ):
            service.shift_srt_file(input_file, output_file, 1000)

    def test_shift_srt_file_warnings(self, tmp_path, capsys):
        input_content = """1
00:00:01,000 --> 00:00:03,000
Test
"""
        # Use .txt extension to trigger warning
        input_file = tmp_path / "input.txt"
        input_file.write_text(input_content)
        output_file = tmp_path / "output.srt"

        service = SubtitleProcessor()
        service.shift_srt_file(input_file, output_file, 1000)

        captured = capsys.readouterr()
        assert "Warning: Input file does not have .srt extension" in captured.out

    def test_shift_srt_file_nested_output_directory(self, tmp_path):
        input_content = """1
00:00:01,000 --> 00:00:03,000
Test
"""
        input_file = tmp_path / "input.srt"
        input_file.write_text(input_content)

        nested_output = tmp_path / "nested" / "dirs" / "output.srt"

        service = SubtitleProcessor()
        service.shift_srt_file(input_file, nested_output, 1000)

        assert nested_output.exists()
        assert nested_output.parent.exists()

    def test_shift_srt_file_multiple_subtitles(self, tmp_path):
        input_content = """1
00:00:01,000 --> 00:00:03,000
First subtitle

2
00:00:04,000 --> 00:00:06,000
Second subtitle

3
00:00:07,000 --> 00:00:09,000
Third subtitle
"""
        input_file = tmp_path / "input.srt"
        input_file.write_text(input_content)
        output_file = tmp_path / "output.srt"

        service = SubtitleProcessor()
        result = service.shift_srt_file(input_file, output_file, 1000)

        assert result == 3

        content = output_file.read_text()
        assert "00:00:02,000 --> 00:00:04,000" in content  # First shifted
        assert "00:00:05,000 --> 00:00:07,000" in content  # Second shifted
        assert "00:00:08,000 --> 00:00:10,000" in content  # Third shifted
