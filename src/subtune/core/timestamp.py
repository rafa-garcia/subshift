import re
from dataclasses import dataclass
from datetime import timedelta

from ..config import SRT_TIMESTAMP_PATTERN
from .exceptions import InvalidTimestampError


@dataclass(frozen=True)
class SRTTimestamp:
    """Immutable SRT timestamp representation with validation and conversion utilities."""

    hours: int
    minutes: int
    seconds: int
    milliseconds: int

    def __post_init__(self):
        if not (0 <= self.hours <= 99):
            raise InvalidTimestampError(f"Hours must be 0-99, got {self.hours}")
        if not (0 <= self.minutes <= 59):
            raise InvalidTimestampError(f"Minutes must be 0-59, got {self.minutes}")
        if not (0 <= self.seconds <= 59):
            raise InvalidTimestampError(f"Seconds must be 0-59, got {self.seconds}")
        if not (0 <= self.milliseconds <= 999):
            raise InvalidTimestampError(f"Milliseconds must be 0-999, got {self.milliseconds}")

    @classmethod
    def from_string(cls, timestamp_str):
        if not re.match(SRT_TIMESTAMP_PATTERN, timestamp_str):
            raise InvalidTimestampError(f"Invalid timestamp format: {timestamp_str}")

        try:
            h, m, s_ms = timestamp_str.split(":")
            s, ms = s_ms.split(",")
            return cls(int(h), int(m), int(s), int(ms))
        except ValueError as e:
            raise InvalidTimestampError(f"Could not parse timestamp '{timestamp_str}': {e}") from e

    @classmethod
    def from_timedelta(cls, td):
        if not isinstance(td, timedelta):
            raise InvalidTimestampError(f"Expected timedelta, got {type(td)}")

        if td.total_seconds() < 0:
            raise InvalidTimestampError("Cannot format negative timedelta")

        total_seconds = int(td.total_seconds())
        ms = int(td.microseconds / 1000)
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60

        if h > 99:
            raise InvalidTimestampError(f"Hours exceed SRT format limit: {h}")

        return cls(h, m, s, ms)

    def to_timedelta(self):
        return timedelta(
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds,
            milliseconds=self.milliseconds,
        )

    def to_string(self):
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d},{self.milliseconds:03d}"

    def shift(self, offset):
        new_time = max(self.to_timedelta() + offset, timedelta(0))
        return self.from_timedelta(new_time)
