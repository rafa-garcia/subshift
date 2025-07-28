import os
import re
import shutil
import tempfile
from datetime import timedelta
from pathlib import Path

from .exceptions import (
    FileProcessingError,
    InvalidOffsetError,
    InvalidSRTFormatError,
    InvalidTimestampError,
)


def parse_timestamp(ts):
    try:
        if not re.match(r"^\d{2}:\d{2}:\d{2},\d{3}$", ts):
            raise InvalidTimestampError(f"Invalid timestamp format: {ts}")

        h, m, s_ms = ts.split(":")
        s, ms = s_ms.split(",")

        hours = int(h)
        minutes = int(m)
        seconds = int(s)
        milliseconds = int(ms)

        if not (
            0 <= hours <= 99
            and 0 <= minutes <= 59
            and 0 <= seconds <= 59
            and 0 <= milliseconds <= 999
        ):
            raise InvalidTimestampError(f"Timestamp values out of range: {ts}")

        return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

    except ValueError as e:
        raise InvalidTimestampError(f"Could not parse timestamp '{ts}': {e}") from e


def format_timestamp(td):
    if td.total_seconds() < 0:
        raise InvalidTimestampError("Cannot format negative timestamp")

    total_seconds = int(td.total_seconds())
    ms = int(td.microseconds / 1000)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60

    if h > 99:
        raise InvalidTimestampError(f"Hours exceed SRT format limit: {h}")

    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _validate_srt_format(file_path):
    """Quick validation that file looks like an SRT file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            # Read first few lines to check basic SRT structure
            lines = []
            for i, line in enumerate(f):
                lines.append(line.strip())
                if i >= 10:  # Check first 10 lines
                    break

            if not lines:
                raise InvalidSRTFormatError("File is empty")

            # Look for at least one timestamp line
            timestamp_found = False
            for line in lines:
                if re.match(r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$", line):
                    timestamp_found = True
                    break

            if not timestamp_found:
                raise InvalidSRTFormatError("No valid SRT timestamp format found in file")

    except UnicodeDecodeError as e:
        raise InvalidSRTFormatError("File is not valid UTF-8 text") from e
    except OSError as e:
        raise FileProcessingError(f"Cannot read file for validation: {e}") from e


def shift_srt(input_file, output_file, offset_ms):
    # Validate input file
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileProcessingError(f"Input file does not exist: {input_path}")
    if not input_path.is_file():
        raise FileProcessingError(f"Input path is not a file: {input_path}")
    if not os.access(input_path, os.R_OK):
        raise FileProcessingError(f"Input file is not readable: {input_path}")

    # Check file extension
    if input_path.suffix.lower() != ".srt":
        print(f"Warning: Input file does not have .srt extension: {input_path}")

    # Validate file size (warn if > 10MB)
    file_size = input_path.stat().st_size
    if file_size > 10 * 1024 * 1024:
        print(f"Warning: Large file detected ({file_size / (1024 * 1024):.1f}MB)")

    # Validate SRT format
    _validate_srt_format(input_path)

    # Validate output location
    output_path = Path(output_file)
    parent_dir = output_path.parent
    if not parent_dir.exists():
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileProcessingError(f"Cannot create output directory: {e}") from e

    if not os.access(parent_dir, os.W_OK):
        raise FileProcessingError(f"Output directory is not writable: {parent_dir}")

    # Validate offset
    try:
        offset_int = int(offset_ms)
    except (ValueError, TypeError) as e:
        raise InvalidOffsetError(f"Offset must be a number: {e}") from e

    if abs(offset_int) > 86400000:  # 24 hours in ms
        raise InvalidOffsetError(f"Offset too large (max ±24 hours): {offset_int}ms")

    offset = timedelta(milliseconds=offset_int)
    subtitle_count = 0
    temp_file = None

    try:
        # Use temporary file for atomic write
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, suffix=".srt.tmp", dir=parent_dir
        ) as temp_file:
            temp_path = Path(temp_file.name)

            try:
                with open(input_path, encoding="utf-8") as input_f:
                    for line_num, line in enumerate(input_f, 1):
                        match = re.match(
                            r"^(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s*$",
                            line,
                        )
                        if match:
                            subtitle_count += 1
                            try:
                                start_str, end_str = match.groups()
                                start = parse_timestamp(start_str) + offset
                                end = parse_timestamp(end_str) + offset

                                start = max(start, timedelta(0))
                                end = max(end, timedelta(0))

                                if end < start:
                                    end = start

                                temp_file.write(
                                    f"{format_timestamp(start)} --> {format_timestamp(end)}\n"
                                )

                            except InvalidTimestampError as e:
                                raise InvalidSRTFormatError(
                                    f"Invalid timestamp on line {line_num}: {e}"
                                ) from e
                        else:
                            temp_file.write(line)

            except UnicodeDecodeError as e:
                raise FileProcessingError(f"Could not decode input file as UTF-8: {e}") from e
            except OSError as e:
                raise FileProcessingError(f"Error reading input file: {e}") from e

        if subtitle_count == 0:
            raise InvalidSRTFormatError("No valid subtitle timestamps found")

        # Atomically move temp file to final location
        try:
            shutil.move(str(temp_path), str(output_path))
        except Exception as e:
            raise FileProcessingError(f"Error writing output file: {e}") from e

    except Exception:
        # Clean up temp file on error
        if temp_file and Path(temp_file.name).exists():
            try:
                Path(temp_file.name).unlink()
            except Exception:
                pass
        raise

    print(f"Successfully processed {subtitle_count} subtitles")
