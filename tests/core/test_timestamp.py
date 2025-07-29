from datetime import timedelta

import pytest

from subtune.core.exceptions import InvalidTimestampError
from subtune.core.timestamp import SRTTimestamp


class TestSRTTimestamp:
    @pytest.mark.parametrize(
        "hours,minutes,seconds,milliseconds",
        [
            (0, 0, 0, 0),
            (1, 23, 45, 678),
            (99, 59, 59, 999),
        ],
    )
    def test_valid_creation(self, hours, minutes, seconds, milliseconds):
        timestamp = SRTTimestamp(hours, minutes, seconds, milliseconds)
        assert timestamp.hours == hours
        assert timestamp.minutes == minutes
        assert timestamp.seconds == seconds
        assert timestamp.milliseconds == milliseconds

    @pytest.mark.parametrize(
        "hours,minutes,seconds,milliseconds,error_msg",
        [
            (-1, 0, 0, 0, "Hours must be 0-99, got -1"),
            (100, 0, 0, 0, "Hours must be 0-99, got 100"),
            (0, -1, 0, 0, "Minutes must be 0-59, got -1"),
            (0, 60, 0, 0, "Minutes must be 0-59, got 60"),
            (0, 0, -1, 0, "Seconds must be 0-59, got -1"),
            (0, 0, 60, 0, "Seconds must be 0-59, got 60"),
            (0, 0, 0, -1, "Milliseconds must be 0-999, got -1"),
            (0, 0, 0, 1000, "Milliseconds must be 0-999, got 1000"),
        ],
    )
    def test_invalid_creation(self, hours, minutes, seconds, milliseconds, error_msg):
        with pytest.raises(InvalidTimestampError, match=error_msg):
            SRTTimestamp(hours, minutes, seconds, milliseconds)

    @pytest.mark.parametrize(
        "timestamp_str,expected_hours,expected_minutes,expected_seconds,expected_ms",
        [
            ("00:00:00,000", 0, 0, 0, 0),
            ("01:23:45,678", 1, 23, 45, 678),
            ("99:59:59,999", 99, 59, 59, 999),
        ],
    )
    def test_from_string_valid(
        self, timestamp_str, expected_hours, expected_minutes, expected_seconds, expected_ms
    ):
        timestamp = SRTTimestamp.from_string(timestamp_str)
        assert timestamp.hours == expected_hours
        assert timestamp.minutes == expected_minutes
        assert timestamp.seconds == expected_seconds
        assert timestamp.milliseconds == expected_ms

    @pytest.mark.parametrize(
        "invalid_timestamp",
        [
            "1:23:45,678",
            "01:23:45.678",
            "01:23:45,1000",
            "100:23:45,678",
            "01:60:45,678",
            "01:23:60,678",
            "aa:bb:cc,ddd",
        ],
    )
    def test_from_string_invalid(self, invalid_timestamp):
        with pytest.raises(InvalidTimestampError):
            SRTTimestamp.from_string(invalid_timestamp)

    @pytest.mark.parametrize(
        "td,expected_str",
        [
            (timedelta(0), "00:00:00,000"),
            (timedelta(hours=1, minutes=23, seconds=45, milliseconds=678), "01:23:45,678"),
            (timedelta(hours=99, minutes=59, seconds=59, milliseconds=999), "99:59:59,999"),
        ],
    )
    def test_from_timedelta_valid(self, td, expected_str):
        timestamp = SRTTimestamp.from_timedelta(td)
        assert timestamp.to_string() == expected_str

    def test_from_timedelta_invalid(self):
        with pytest.raises(InvalidTimestampError, match="Cannot format negative timedelta"):
            SRTTimestamp.from_timedelta(timedelta(seconds=-1))

        with pytest.raises(InvalidTimestampError, match="Hours exceed SRT format limit"):
            SRTTimestamp.from_timedelta(timedelta(hours=100))

        with pytest.raises(InvalidTimestampError, match="Expected timedelta"):
            SRTTimestamp.from_timedelta("not a timedelta")

    def test_to_timedelta(self):
        timestamp = SRTTimestamp(1, 23, 45, 678)
        td = timestamp.to_timedelta()
        expected = timedelta(hours=1, minutes=23, seconds=45, milliseconds=678)
        assert td == expected

    @pytest.mark.parametrize(
        "hours,minutes,seconds,milliseconds,expected",
        [
            (0, 0, 0, 0, "00:00:00,000"),
            (1, 23, 45, 678, "01:23:45,678"),
            (99, 59, 59, 999, "99:59:59,999"),
        ],
    )
    def test_to_string(self, hours, minutes, seconds, milliseconds, expected):
        timestamp = SRTTimestamp(hours, minutes, seconds, milliseconds)
        assert timestamp.to_string() == expected

    def test_shift_positive(self):
        timestamp = SRTTimestamp(0, 0, 1, 0)
        offset = timedelta(seconds=1)
        shifted = timestamp.shift(offset)
        assert shifted.to_string() == "00:00:02,000"

    def test_shift_negative_clamped(self):
        timestamp = SRTTimestamp(0, 0, 1, 0)
        offset = timedelta(seconds=-2)
        shifted = timestamp.shift(offset)
        assert shifted.to_string() == "00:00:00,000"

    def test_round_trip_conversion(self):
        original = "01:23:45,678"
        timestamp = SRTTimestamp.from_string(original)
        td = timestamp.to_timedelta()
        back_to_timestamp = SRTTimestamp.from_timedelta(td)
        assert back_to_timestamp.to_string() == original
