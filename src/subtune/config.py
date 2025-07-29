"""Configuration constants for subtune application."""

# File validation settings
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB warning threshold
FILE_ENCODING = "utf-8"
BACKUP_SUFFIX = ".backup"
TEMP_FILE_SUFFIX = ".srt.tmp"

# Offset validation limits
MAX_OFFSET_MS = 86400000  # 24 hours in milliseconds
MIN_OFFSET_MS = -86400000  # -24 hours in milliseconds

# SRT format validation patterns
SRT_TIMESTAMP_PATTERN = r"^\d{2}:\d{2}:\d{2},\d{3}$"
SRT_TIMING_LINE_PATTERN = r"^(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s*$"

# File extension validation
VALID_SRT_EXTENSIONS = [".srt", ".SRT"]

# Size calculation constants
BYTES_PER_MB = 1024 * 1024

# Warning and error messages
WARNINGS = {
    "large_file": "Large file detected (>{size}MB). Processing may take time.",
    "invalid_extension": "Input file does not have .srt extension. Proceeding anyway.",
    "backup_failed": "Could not create backup file: {error}",
}

ERROR_MESSAGES = {
    "invalid_utf8": "File is not valid UTF-8 text",
}

# Timestamp validation ranges
TIMESTAMP_LIMITS = {
    "hours": (0, 99),
    "minutes": (0, 59),
    "seconds": (0, 59),
    "milliseconds": (0, 999),
}
