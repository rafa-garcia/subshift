import os
import shutil
import tempfile
from datetime import timedelta
from pathlib import Path

from ..config import (
    BYTES_PER_MB,
    ERROR_MESSAGES,
    FILE_ENCODING,
    MAX_FILE_SIZE_BYTES,
    MAX_OFFSET_MS,
    TEMP_FILE_SUFFIX,
    VALID_SRT_EXTENSIONS,
)
from .exceptions import (
    FileProcessingError,
    InvalidOffsetError,
    InvalidSRTFormatError,
)
from .processor import SRTFile


class FileValidator:
    """Static file validation and I/O operations for SRT files."""

    @staticmethod
    def validate_input_file(file_path):
        if not file_path.exists():
            raise FileProcessingError(f"Input file does not exist: {file_path}")

        if not file_path.is_file():
            raise FileProcessingError(f"Input path is not a file: {file_path}")

        if not os.access(file_path, os.R_OK):
            raise FileProcessingError(f"Input file is not readable: {file_path}")

    @staticmethod
    def validate_output_location(file_path):
        parent_dir = file_path.parent

        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise FileProcessingError(f"Cannot create output directory: {e}") from e

        if not os.access(parent_dir, os.W_OK):
            raise FileProcessingError(f"Output directory is not writable: {parent_dir}")

    @staticmethod
    def check_file_warnings(file_path):
        if file_path.suffix.lower() not in [ext.lower() for ext in VALID_SRT_EXTENSIONS]:
            print(f"Warning: Input file does not have .srt extension: {file_path}")

        file_size = file_path.stat().st_size
        if file_size > MAX_FILE_SIZE_BYTES:
            print(f"Warning: Large file detected ({file_size / BYTES_PER_MB:.1f}MB)")

    @staticmethod
    def read_srt_file(file_path):
        try:
            with open(file_path, encoding=FILE_ENCODING) as f:
                content = f.read()
            return SRTFile.from_content(content)
        except UnicodeDecodeError as e:
            raise InvalidSRTFormatError(ERROR_MESSAGES["invalid_utf8"]) from e
        except OSError as e:
            raise FileProcessingError(f"Error reading input file: {e}") from e

    @staticmethod
    def write_srt_file(srt_file, output_path):
        parent_dir = output_path.parent
        temp_file = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding=FILE_ENCODING,
                delete=False,
                suffix=TEMP_FILE_SUFFIX,
                dir=parent_dir,
            ) as temp_file:
                temp_path = Path(temp_file.name)
                temp_file.write(srt_file.to_content())

            shutil.move(str(temp_path), str(output_path))

        except Exception as e:
            if temp_file and Path(temp_file.name).exists():
                try:
                    Path(temp_file.name).unlink()
                except Exception:
                    pass
            raise FileProcessingError(f"Error writing output file: {e}") from e

    @staticmethod
    def validate_offset(offset_ms):
        try:
            offset_int = int(offset_ms)
        except (ValueError, TypeError) as e:
            raise InvalidOffsetError(f"Offset must be a number: {e}") from e

        if abs(offset_int) > MAX_OFFSET_MS:
            raise InvalidOffsetError(f"Offset too large (max ±24 hours): {offset_int}ms")

        return timedelta(milliseconds=offset_int)
