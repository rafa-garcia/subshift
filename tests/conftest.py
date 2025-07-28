import pytest


@pytest.fixture
def simple_srt_content():
    """Simple SRT content for basic testing"""
    return """1
00:00:01,000 --> 00:00:03,000
Hello, world!

2
00:00:04,000 --> 00:00:06,000
This is a test subtitle.

3
00:00:08,500 --> 00:00:10,200
Final subtitle here.

"""


@pytest.fixture
def complex_srt_content():
    """More complex SRT content with edge cases"""
    return """1
00:00:00,100 --> 00:00:02,900
First subtitle with timing

2
00:01:23,456 --> 00:01:25,789
Subtitle with larger timestamps

3
00:00:05,000 --> 00:00:05,500
Very short duration

4
01:30:45,000 --> 01:30:50,000
Subtitle after an hour

"""


@pytest.fixture
def malformed_srt_content():
    """SRT content with various formatting issues"""
    return """1
00:00:01,000 -> 00:00:03,000
Missing second dash

2
00:00:04,000 --> 00:00:06,000
Normal subtitle

3
25:00:08,500 --> 25:00:10,200
Invalid hour value

"""


@pytest.fixture
def empty_srt_content():
    """Empty SRT content"""
    return ""


@pytest.fixture
def no_timestamps_content():
    """Content without any valid timestamps"""
    return """This is just plain text
with no subtitle timestamps
at all in the content.
"""


@pytest.fixture
def simple_srt_file(tmp_path, simple_srt_content):
    """Create a temporary SRT file with simple content"""
    srt_file = tmp_path / "simple.srt"
    srt_file.write_text(simple_srt_content)
    return srt_file


@pytest.fixture
def complex_srt_file(tmp_path, complex_srt_content):
    """Create a temporary SRT file with complex content"""
    srt_file = tmp_path / "complex.srt"
    srt_file.write_text(complex_srt_content)
    return srt_file


@pytest.fixture
def malformed_srt_file(tmp_path, malformed_srt_content):
    """Create a temporary SRT file with malformed content"""
    srt_file = tmp_path / "malformed.srt"
    srt_file.write_text(malformed_srt_content)
    return srt_file


@pytest.fixture
def empty_srt_file(tmp_path, empty_srt_content):
    """Create a temporary empty SRT file"""
    srt_file = tmp_path / "empty.srt"
    srt_file.write_text(empty_srt_content)
    return srt_file


@pytest.fixture
def no_timestamps_file(tmp_path, no_timestamps_content):
    """Create a temporary file with no timestamps"""
    srt_file = tmp_path / "no_timestamps.srt"
    srt_file.write_text(no_timestamps_content)
    return srt_file


@pytest.fixture
def non_utf8_file(tmp_path):
    """Create a file with invalid UTF-8 encoding"""
    file_path = tmp_path / "invalid_utf8.srt"
    with open(file_path, "wb") as f:
        f.write(b"\xff\xfe\x00Invalid UTF-8 content")
    return file_path


@pytest.fixture
def output_file(tmp_path):
    """Standard output file path for tests"""
    return tmp_path / "output.srt"


@pytest.fixture
def nested_output_file(tmp_path):
    """Output file in nested directory for testing directory creation"""
    return tmp_path / "nested" / "subdir" / "output.srt"
