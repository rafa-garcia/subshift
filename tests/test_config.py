from subtune.config import (
    BACKUP_SUFFIX,
    BYTES_PER_MB,
    ERROR_MESSAGES,
    FILE_ENCODING,
    MAX_FILE_SIZE_BYTES,
    MAX_OFFSET_MS,
    MIN_OFFSET_MS,
    SRT_TIMESTAMP_PATTERN,
    SRT_TIMING_LINE_PATTERN,
    TEMP_FILE_SUFFIX,
    TIMESTAMP_LIMITS,
    VALID_SRT_EXTENSIONS,
    WARNINGS,
)


class TestConfigConstants:
    def test_file_validation_constants(self):
        assert MAX_FILE_SIZE_BYTES == 10 * 1024 * 1024
        assert FILE_ENCODING == "utf-8"
        assert BACKUP_SUFFIX == ".backup"
        assert TEMP_FILE_SUFFIX == ".srt.tmp"
        assert BYTES_PER_MB == 1024 * 1024

    def test_offset_limits(self):
        assert MAX_OFFSET_MS == 86400000  # 24 hours
        assert MIN_OFFSET_MS == -86400000  # -24 hours
        assert MAX_OFFSET_MS > 0
        assert MIN_OFFSET_MS < 0

    def test_regex_patterns(self):
        # Test valid SRT timestamp pattern (format only, not semantic validation)
        import re

        valid_format = ["00:00:00,000", "01:23:45,678", "99:59:59,999", "01:60:45,678"]
        invalid_format = ["1:23:45,678", "01:23:45.678", "100:23:45,678", "01:23:45,1000"]

        for timestamp in valid_format:
            assert re.match(SRT_TIMESTAMP_PATTERN, timestamp)

        for timestamp in invalid_format:
            assert not re.match(SRT_TIMESTAMP_PATTERN, timestamp)

    def test_timing_line_pattern(self):
        import re

        valid_timing = "00:00:01,000 --> 00:00:03,000"
        invalid_timing = "00:00:01,000 -> 00:00:03,000"

        assert re.match(SRT_TIMING_LINE_PATTERN, valid_timing)
        assert not re.match(SRT_TIMING_LINE_PATTERN, invalid_timing)

    def test_valid_extensions(self):
        assert ".srt" in VALID_SRT_EXTENSIONS
        assert ".SRT" in VALID_SRT_EXTENSIONS
        assert len(VALID_SRT_EXTENSIONS) == 2

    def test_warning_messages(self):
        assert "large_file" in WARNINGS
        assert "invalid_extension" in WARNINGS
        assert "backup_failed" in WARNINGS

        # Test that warning messages have placeholders
        assert "{size}" in WARNINGS["large_file"]
        assert "{error}" in WARNINGS["backup_failed"]

    def test_error_messages(self):
        assert "invalid_utf8" in ERROR_MESSAGES
        assert ERROR_MESSAGES["invalid_utf8"] == "File is not valid UTF-8 text"

    def test_timestamp_limits(self):
        assert TIMESTAMP_LIMITS["hours"] == (0, 99)
        assert TIMESTAMP_LIMITS["minutes"] == (0, 59)
        assert TIMESTAMP_LIMITS["seconds"] == (0, 59)
        assert TIMESTAMP_LIMITS["milliseconds"] == (0, 999)

        # Ensure all limits are tuples with min/max values
        for _field, (min_val, max_val) in TIMESTAMP_LIMITS.items():
            assert min_val >= 0
            assert max_val > min_val
