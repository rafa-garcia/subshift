import re
from dataclasses import dataclass

from ..config import SRT_TIMING_LINE_PATTERN
from .exceptions import InvalidSRTFormatError
from .timestamp import SRTTimestamp


@dataclass(frozen=True)
class SRTSubtitle:
    """Immutable SRT subtitle entry with parsing and formatting capabilities."""

    number: int
    start: SRTTimestamp
    end: SRTTimestamp
    text: list

    def __post_init__(self):
        if self.number <= 0:
            raise InvalidSRTFormatError(f"Subtitle number must be positive, got {self.number}")

        if self.end.to_timedelta() < self.start.to_timedelta():
            object.__setattr__(self, "end", self.start)

    @classmethod
    def from_lines(cls, lines):
        if len(lines) < 3:
            raise InvalidSRTFormatError(
                "Subtitle must have at least 3 lines (number, timing, text)"
            )

        try:
            number = int(lines[0].strip())
        except ValueError as e:
            raise InvalidSRTFormatError(f"Invalid subtitle number: {lines[0]}") from e

        timing_match = re.match(SRT_TIMING_LINE_PATTERN, lines[1])
        if not timing_match:
            raise InvalidSRTFormatError(f"Invalid timing format: {lines[1]}")

        start_str, end_str = timing_match.groups()
        start = SRTTimestamp.from_string(start_str)
        end = SRTTimestamp.from_string(end_str)

        text = [line.rstrip() for line in lines[2:]]

        return cls(number, start, end, text)

    def to_lines(self):
        lines = [
            str(self.number),
            f"{self.start.to_string()} --> {self.end.to_string()}",
            *self.text,
            "",
        ]
        return lines

    def shift(self, offset):
        new_start = self.start.shift(offset)
        new_end = self.end.shift(offset)

        if new_end.to_timedelta() < new_start.to_timedelta():
            new_end = new_start

        return SRTSubtitle(self.number, new_start, new_end, self.text)


@dataclass
class SRTFile:
    """SRT file container with parsing, validation, and content generation."""

    subtitles: list

    def __post_init__(self):
        if not self.subtitles:
            raise InvalidSRTFormatError("SRT file must contain at least one subtitle")

    @classmethod
    def from_content(cls, content):
        if not content.strip():
            raise InvalidSRTFormatError("File is empty")

        subtitles = []
        current_subtitle_lines = []

        for line in content.split("\n"):
            line = line.rstrip()

            if line == "" and current_subtitle_lines:
                if len(current_subtitle_lines) >= 3:
                    try:
                        subtitle = SRTSubtitle.from_lines(current_subtitle_lines)
                        subtitles.append(subtitle)
                    except InvalidSRTFormatError:
                        pass
                current_subtitle_lines = []
            elif line:
                current_subtitle_lines.append(line)

        if current_subtitle_lines and len(current_subtitle_lines) >= 3:
            try:
                subtitle = SRTSubtitle.from_lines(current_subtitle_lines)
                subtitles.append(subtitle)
            except InvalidSRTFormatError:
                pass

        if not subtitles:
            raise InvalidSRTFormatError("No valid SRT timestamp format found in file")

        return cls(subtitles)

    def to_content(self):
        lines = []
        for subtitle in self.subtitles:
            lines.extend(subtitle.to_lines())

        return "\n".join(lines)

    def shift(self, offset):
        shifted_subtitles = [subtitle.shift(offset) for subtitle in self.subtitles]
        return SRTFile(shifted_subtitles)

    def __len__(self):
        return len(self.subtitles)

    def __iter__(self):
        return iter(self.subtitles)
