from datetime import timedelta

import pytest

from subshift.core import _validate_srt_format, format_timestamp, parse_timestamp, shift_srt
from subshift.exceptions import (
    FileProcessingError,
    InvalidOffsetError,
    InvalidSRTFormatError,
    InvalidTimestampError,
)


class TestParseTimestamp:
    @pytest.mark.parametrize(
        "timestamp,expected",
        [
            ("01:23:45,678", timedelta(hours=1, minutes=23, seconds=45, milliseconds=678)),
            ("00:00:00,000", timedelta(0)),
            ("99:59:59,999", timedelta(hours=99, minutes=59, seconds=59, milliseconds=999)),
        ],
    )
    def test_valid_timestamps(self, timestamp, expected):
        result = parse_timestamp(timestamp)
        assert result == expected

    @pytest.mark.parametrize(
        "invalid_timestamp",
        [
            "01:23:45.678",  # No comma
            "1:23:45,678",  # Wrong digits
            "100:23:45,678",  # 3 digits for hours
            "01:23:45,1000",  # 4 digits for ms
            "aa:bb:cc,ddd",  # Non-numeric
        ],
    )
    def test_invalid_format_errors(self, invalid_timestamp):
        with pytest.raises(InvalidTimestampError, match="Invalid timestamp format"):
            parse_timestamp(invalid_timestamp)

    @pytest.mark.parametrize(
        "timestamp,error_message",
        [
            ("01:60:45,678", "Minutes must be 0-59, got 60"),
            ("01:23:60,678", "Seconds must be 0-59, got 60"),
        ],
    )
    def test_range_validation_errors(self, timestamp, error_message):
        with pytest.raises(InvalidTimestampError, match=error_message):
            parse_timestamp(timestamp)


class TestFormatTimestamp:
    @pytest.mark.parametrize(
        "td,expected",
        [
            (timedelta(hours=1, minutes=23, seconds=45, milliseconds=678), "01:23:45,678"),
            (timedelta(0), "00:00:00,000"),
            (timedelta(hours=99, minutes=59, seconds=59, milliseconds=999), "99:59:59,999"),
        ],
    )
    def test_valid_formatting(self, td, expected):
        result = format_timestamp(td)
        assert result == expected

    @pytest.mark.parametrize(
        "td,error_message",
        [
            (timedelta(seconds=-1), "Cannot format negative timedelta"),
            (timedelta(hours=100), "Hours exceed SRT format limit"),
            ("not a timedelta", "Expected timedelta"),
        ],
    )
    def test_formatting_errors(self, td, error_message):
        with pytest.raises(InvalidTimestampError, match=error_message):
            format_timestamp(td)


class TestValidateSRTFormat:
    def test_valid_srt_content(self, tmp_path):
        srt_file = tmp_path / "test.srt"
        srt_file.write_text(
            "1\n"
            "00:00:01,000 --> 00:00:03,000\n"
            "Hello world\n"
            "\n"
            "2\n"
            "00:00:04,000 --> 00:00:06,000\n"
            "Second subtitle\n"
        )
        # Should not raise any exception
        _validate_srt_format(srt_file)

    def test_empty_file(self, tmp_path):
        srt_file = tmp_path / "empty.srt"
        srt_file.write_text("")
        with pytest.raises(InvalidSRTFormatError, match="File is empty"):
            _validate_srt_format(srt_file)

    def test_no_timestamps(self, tmp_path):
        srt_file = tmp_path / "no_timestamps.srt"
        srt_file.write_text("Just some text\nNo timestamps here\n")
        with pytest.raises(InvalidSRTFormatError, match="No valid SRT timestamp format found"):
            _validate_srt_format(srt_file)

    def test_invalid_utf8(self, tmp_path):
        srt_file = tmp_path / "invalid.srt"
        with open(srt_file, "wb") as f:
            f.write(b"\xff\xfe invalid utf-8")
        with pytest.raises(InvalidSRTFormatError, match="File is not valid UTF-8 text"):
            _validate_srt_format(srt_file)


class TestShiftSRT:
    @pytest.mark.parametrize(
        "offset,expected_timestamps",
        [
            (1000, ["00:00:02,000 --> 00:00:04,000", "00:00:05,000 --> 00:00:07,000"]),
            (-500, ["00:00:00,500 --> 00:00:02,500", "00:00:03,500 --> 00:00:05,500"]),
            (-2000, ["00:00:00,000 --> 00:00:01,000"]),  # Clamped to zero
        ],
    )
    def test_timestamp_shifting(self, simple_srt_file, output_file, offset, expected_timestamps):
        shift_srt(simple_srt_file, output_file, offset)
        content = output_file.read_text()

        for timestamp in expected_timestamps:
            assert timestamp in content

        # Check content is preserved for positive shifts
        if offset > 0:
            assert "Hello, world!" in content
            assert "This is a test subtitle." in content

    def test_input_file_not_found(self, output_file, tmp_path):
        nonexistent = tmp_path / "nonexistent.srt"

        with pytest.raises(FileProcessingError, match="Input file does not exist"):
            shift_srt(nonexistent, output_file, 1000)

    def test_input_not_readable(self, output_file, tmp_path):
        srt_file = tmp_path / "unreadable.srt"
        srt_file.write_text("test")
        srt_file.chmod(0o000)  # Remove all permissions

        try:
            with pytest.raises(FileProcessingError, match="Input file is not readable"):
                shift_srt(srt_file, output_file, 1000)
        finally:
            srt_file.chmod(0o644)  # Restore permissions for cleanup

    def test_output_directory_creation(self, simple_srt_file, nested_output_file):
        shift_srt(simple_srt_file, nested_output_file, 1000)

        assert nested_output_file.exists()
        assert "00:00:02,000 --> 00:00:04,000" in nested_output_file.read_text()

    @pytest.mark.parametrize(
        "invalid_offset,error_message",
        [
            ("not a number", "Offset must be a number"),
            (90000000, "Offset too large"),  # > 24 hours
        ],
    )
    def test_offset_validation_errors(
        self, simple_srt_file, output_file, invalid_offset, error_message
    ):
        with pytest.raises(InvalidOffsetError, match=error_message):
            shift_srt(simple_srt_file, output_file, invalid_offset)

    def test_no_subtitles_found(self, no_timestamps_file, output_file):
        with pytest.raises(
            InvalidSRTFormatError, match="No valid SRT timestamp format found in file"
        ):
            shift_srt(no_timestamps_file, output_file, 1000)

    def test_in_place_modification(self, simple_srt_file):
        original_content = simple_srt_file.read_text()
        shift_srt(simple_srt_file, simple_srt_file, 1000)  # Modify in place

        new_content = simple_srt_file.read_text()
        assert new_content != original_content
        assert "00:00:02,000 --> 00:00:04,000" in new_content

    def test_end_before_start_fix(self, output_file, tmp_path):
        # Create SRT with problematic timing that would cause end < start after shift
        srt_file = tmp_path / "problem.srt"
        srt_file.write_text("1\n00:00:00,500 --> 00:00:01,000\nShort subtitle\n")

        # Shift back by 1 second - start would go to 0, end to 0
        shift_srt(srt_file, output_file, -1000)

        content = output_file.read_text()
        assert "00:00:00,000 --> 00:00:00,000" in content  # End adjusted to match start
