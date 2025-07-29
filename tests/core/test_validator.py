import os
from datetime import timedelta
from unittest.mock import patch

import pytest

from subtune.core.exceptions import (
    FileProcessingError,
    InvalidOffsetError,
    InvalidSRTFormatError,
)
from subtune.core.processor import SRTFile, SRTSubtitle
from subtune.core.timestamp import SRTTimestamp
from subtune.core.validator import FileValidator


class TestFileValidator:
    def test_validate_input_file_exists(self, tmp_path):
        test_file = tmp_path / "test.srt"
        test_file.write_text("test content")

        FileValidator.validate_input_file(test_file)

    def test_validate_input_file_not_exists(self, tmp_path):
        nonexistent = tmp_path / "nonexistent.srt"

        with pytest.raises(FileProcessingError, match="Input file does not exist"):
            FileValidator.validate_input_file(nonexistent)

    def test_validate_input_file_is_directory(self, tmp_path):
        directory = tmp_path / "test_dir"
        directory.mkdir()

        with pytest.raises(FileProcessingError, match="Input path is not a file"):
            FileValidator.validate_input_file(directory)

    def test_validate_input_file_not_readable(self, tmp_path):
        test_file = tmp_path / "test.srt"
        test_file.write_text("test")
        test_file.chmod(0o000)

        try:
            with pytest.raises(FileProcessingError, match="Input file is not readable"):
                FileValidator.validate_input_file(test_file)
        finally:
            test_file.chmod(0o644)

    def test_validate_output_location_exists(self, tmp_path):
        test_file = tmp_path / "output.srt"

        FileValidator.validate_output_location(test_file)

    def test_validate_output_location_creates_directory(self, tmp_path):
        nested_file = tmp_path / "nested" / "dir" / "output.srt"

        FileValidator.validate_output_location(nested_file)
        assert nested_file.parent.exists()

    def test_validate_output_location_permission_denied(self, tmp_path):
        if os.name == "nt":  # Skip on Windows
            pytest.skip("Permission test not reliable on Windows")

        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)

        try:
            with pytest.raises(FileProcessingError, match="Output directory is not writable"):
                FileValidator.validate_output_location(readonly_dir / "output.srt")
        finally:
            readonly_dir.chmod(0o755)

    @pytest.mark.parametrize(
        "filename,should_warn",
        [
            ("test.srt", False),
            ("test.SRT", False),
            ("test.txt", True),
            ("test", True),
        ],
    )
    def test_check_file_warnings_extension(self, tmp_path, filename, should_warn, capsys):
        test_file = tmp_path / filename
        test_file.write_text("test")

        FileValidator.check_file_warnings(test_file)

        captured = capsys.readouterr()
        if should_warn:
            assert "Warning: Input file does not have .srt extension" in captured.out
        else:
            assert "Warning" not in captured.out

    def test_check_file_warnings_large_file(self, tmp_path, capsys):
        test_file = tmp_path / "large.srt"
        large_content = "x" * (11 * 1024 * 1024)  # 11MB
        test_file.write_text(large_content)

        FileValidator.check_file_warnings(test_file)

        captured = capsys.readouterr()
        assert "Warning: Large file detected" in captured.out

    def test_read_srt_file_valid(self, tmp_path):
        content = """1
00:00:01,000 --> 00:00:03,000
Test subtitle
"""
        test_file = tmp_path / "test.srt"
        test_file.write_text(content)

        srt_file = FileValidator.read_srt_file(test_file)
        assert len(srt_file) == 1

    def test_read_srt_file_invalid_utf8(self, tmp_path):
        test_file = tmp_path / "invalid.srt"
        with open(test_file, "wb") as f:
            f.write(b"\xff\xfe invalid utf-8")

        with pytest.raises(InvalidSRTFormatError, match="File is not valid UTF-8 text"):
            FileValidator.read_srt_file(test_file)

    def test_write_srt_file(self, tmp_path):
        start = SRTTimestamp(0, 0, 1, 0)
        end = SRTTimestamp(0, 0, 3, 0)
        subtitle = SRTSubtitle(1, start, end, ["Test"])
        srt_file = SRTFile([subtitle])

        output_file = tmp_path / "output.srt"
        FileValidator.write_srt_file(srt_file, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "00:00:01,000 --> 00:00:03,000" in content
        assert "Test" in content

    def test_write_srt_file_atomic_operation(self, tmp_path):
        start = SRTTimestamp(0, 0, 1, 0)
        end = SRTTimestamp(0, 0, 3, 0)
        subtitle = SRTSubtitle(1, start, end, ["Test"])
        srt_file = SRTFile([subtitle])

        output_file = tmp_path / "output.srt"

        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_temp.side_effect = Exception("Temp file error")

            with pytest.raises(FileProcessingError, match="Error writing output file"):
                FileValidator.write_srt_file(srt_file, output_file)

    def test_validate_offset_valid_integers(self):
        # Test valid integer values
        result = FileValidator.validate_offset(1000)
        expected = timedelta(milliseconds=1000)
        assert result == expected

        result = FileValidator.validate_offset(-1000)
        expected = timedelta(milliseconds=-1000)
        assert result == expected

        result = FileValidator.validate_offset(0)
        expected = timedelta(milliseconds=0)
        assert result == expected

    def test_validate_offset_valid_strings(self):
        # Test valid string representations
        result = FileValidator.validate_offset("1000")
        expected = timedelta(milliseconds=1000)
        assert result == expected

        result = FileValidator.validate_offset("-1000")
        expected = timedelta(milliseconds=-1000)
        assert result == expected

    def test_validate_offset_invalid_values(self):
        # Test invalid string values
        with pytest.raises(InvalidOffsetError, match="Offset must be a number"):
            FileValidator.validate_offset("abc")

        with pytest.raises(InvalidOffsetError, match="Offset must be a number"):
            FileValidator.validate_offset("1.5")

        with pytest.raises(InvalidOffsetError, match="Offset must be a number"):
            FileValidator.validate_offset(None)

        with pytest.raises(InvalidOffsetError, match="Offset must be a number"):
            FileValidator.validate_offset([])

    def test_validate_offset_too_large(self):
        # Test values exceeding 24 hours (86400000 ms)
        with pytest.raises(InvalidOffsetError, match="Offset too large"):
            FileValidator.validate_offset(86400001)

        with pytest.raises(InvalidOffsetError, match="Offset too large"):
            FileValidator.validate_offset(-86400001)

    def test_validate_offset_boundary_values(self):
        # Test boundary values (exactly 24 hours)
        result = FileValidator.validate_offset(86400000)
        expected = timedelta(milliseconds=86400000)
        assert result == expected

        result = FileValidator.validate_offset(-86400000)
        expected = timedelta(milliseconds=-86400000)
        assert result == expected
