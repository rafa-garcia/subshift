from datetime import timedelta

import pytest

from subtune.core.exceptions import InvalidSRTFormatError
from subtune.core.processor import SRTFile, SRTSubtitle
from subtune.core.timestamp import SRTTimestamp


class TestSRTSubtitle:
    def test_valid_creation(self):
        start = SRTTimestamp(0, 0, 1, 0)
        end = SRTTimestamp(0, 0, 3, 0)
        text = ["Hello, world!"]
        subtitle = SRTSubtitle(1, start, end, text)

        assert subtitle.number == 1
        assert subtitle.start == start
        assert subtitle.end == end
        assert subtitle.text == text

    def test_invalid_subtitle_number(self):
        start = SRTTimestamp(0, 0, 1, 0)
        end = SRTTimestamp(0, 0, 3, 0)
        text = ["Hello"]

        with pytest.raises(InvalidSRTFormatError, match="Subtitle number must be positive"):
            SRTSubtitle(0, start, end, text)

    def test_end_before_start_auto_fix(self):
        start = SRTTimestamp(0, 0, 3, 0)
        end = SRTTimestamp(0, 0, 1, 0)
        text = ["Hello"]

        subtitle = SRTSubtitle(1, start, end, text)
        assert subtitle.end == start

    def test_from_lines_valid(self):
        lines = ["1", "00:00:01,000 --> 00:00:03,000", "Hello, world!", "Second line of text"]
        subtitle = SRTSubtitle.from_lines(lines)

        assert subtitle.number == 1
        assert subtitle.start.to_string() == "00:00:01,000"
        assert subtitle.end.to_string() == "00:00:03,000"
        assert subtitle.text == ["Hello, world!", "Second line of text"]

    @pytest.mark.parametrize(
        "lines,error_msg",
        [
            (["1", "00:00:01,000 --> 00:00:03,000"], "Subtitle must have at least 3 lines"),
            (["abc", "00:00:01,000 --> 00:00:03,000", "Text"], "Invalid subtitle number"),
            (["1", "invalid timing format", "Text"], "Invalid timing format"),
        ],
    )
    def test_from_lines_invalid(self, lines, error_msg):
        with pytest.raises(InvalidSRTFormatError, match=error_msg):
            SRTSubtitle.from_lines(lines)

    def test_to_lines(self):
        start = SRTTimestamp(0, 0, 1, 0)
        end = SRTTimestamp(0, 0, 3, 0)
        subtitle = SRTSubtitle(1, start, end, ["Hello", "World"])

        lines = subtitle.to_lines()
        expected = ["1", "00:00:01,000 --> 00:00:03,000", "Hello", "World", ""]
        assert lines == expected

    def test_shift(self):
        start = SRTTimestamp(0, 0, 1, 0)
        end = SRTTimestamp(0, 0, 3, 0)
        subtitle = SRTSubtitle(1, start, end, ["Text"])

        shifted = subtitle.shift(timedelta(seconds=1))
        assert shifted.start.to_string() == "00:00:02,000"
        assert shifted.end.to_string() == "00:00:04,000"
        assert shifted.text == ["Text"]
        assert shifted.number == 1

    def test_shift_with_end_correction(self):
        start = SRTTimestamp(0, 0, 1, 0)
        end = SRTTimestamp(0, 0, 1, 500)
        subtitle = SRTSubtitle(1, start, end, ["Text"])

        shifted = subtitle.shift(timedelta(seconds=-2))
        assert shifted.start.to_string() == "00:00:00,000"
        assert shifted.end.to_string() == "00:00:00,000"


class TestSRTFile:
    def test_valid_creation(self):
        start = SRTTimestamp(0, 0, 1, 0)
        end = SRTTimestamp(0, 0, 3, 0)
        subtitle = SRTSubtitle(1, start, end, ["Text"])
        srt_file = SRTFile([subtitle])

        assert len(srt_file) == 1
        assert list(srt_file)[0] == subtitle

    def test_empty_file_creation(self):
        with pytest.raises(
            InvalidSRTFormatError, match="SRT file must contain at least one subtitle"
        ):
            SRTFile([])

    def test_from_content_valid(self):
        content = """1
00:00:01,000 --> 00:00:03,000
Hello, world!

2
00:00:04,000 --> 00:00:06,000
Second subtitle
"""
        srt_file = SRTFile.from_content(content)
        assert len(srt_file) == 2

        first = list(srt_file)[0]
        assert first.number == 1
        assert first.text == ["Hello, world!"]

    def test_from_content_empty(self):
        with pytest.raises(InvalidSRTFormatError, match="File is empty"):
            SRTFile.from_content("")

    def test_from_content_no_valid_subtitles(self):
        content = "Just some random text\nNo subtitles here"
        with pytest.raises(
            InvalidSRTFormatError, match="No valid SRT timestamp format found in file"
        ):
            SRTFile.from_content(content)

    def test_from_content_mixed_valid_invalid(self):
        content = """1
00:00:01,000 --> 00:00:03,000
Valid subtitle

Invalid block
Not a subtitle

2
00:00:04,000 --> 00:00:06,000
Another valid subtitle
"""
        srt_file = SRTFile.from_content(content)
        assert len(srt_file) == 2

    def test_to_content(self):
        start1 = SRTTimestamp(0, 0, 1, 0)
        end1 = SRTTimestamp(0, 0, 3, 0)
        subtitle1 = SRTSubtitle(1, start1, end1, ["First"])

        start2 = SRTTimestamp(0, 0, 4, 0)
        end2 = SRTTimestamp(0, 0, 6, 0)
        subtitle2 = SRTSubtitle(2, start2, end2, ["Second"])

        srt_file = SRTFile([subtitle1, subtitle2])
        content = srt_file.to_content()

        expected = """1
00:00:01,000 --> 00:00:03,000
First

2
00:00:04,000 --> 00:00:06,000
Second
"""
        assert content == expected

    def test_shift(self):
        start = SRTTimestamp(0, 0, 1, 0)
        end = SRTTimestamp(0, 0, 3, 0)
        subtitle = SRTSubtitle(1, start, end, ["Text"])
        srt_file = SRTFile([subtitle])

        shifted = srt_file.shift(timedelta(seconds=1))
        shifted_subtitle = list(shifted)[0]
        assert shifted_subtitle.start.to_string() == "00:00:02,000"
        assert shifted_subtitle.end.to_string() == "00:00:04,000"

    def test_iteration_and_length(self):
        start = SRTTimestamp(0, 0, 1, 0)
        end = SRTTimestamp(0, 0, 3, 0)
        subtitle1 = SRTSubtitle(1, start, end, ["First"])
        subtitle2 = SRTSubtitle(2, start, end, ["Second"])

        srt_file = SRTFile([subtitle1, subtitle2])
        subtitles = list(srt_file)
        assert len(subtitles) == 2
        assert len(srt_file) == 2
        assert subtitles[0] == subtitle1
        assert subtitles[1] == subtitle2
