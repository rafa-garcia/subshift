"""Custom exceptions for subshift."""


class SubshiftError(Exception):
    """Base exception for all subshift errors."""

    pass


class InvalidTimestampError(SubshiftError):
    """Raised when a timestamp cannot be parsed."""

    pass


class FileProcessingError(SubshiftError):
    """Raised when file operations fail."""

    pass


class InvalidSRTFormatError(SubshiftError):
    """Raised when SRT file format is invalid."""

    pass


class InvalidOffsetError(SubshiftError):
    """Raised when offset value is invalid."""

    pass
