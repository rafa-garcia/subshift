class SubtuneError(Exception):
    """Base exception for all subtune errors."""

    pass


class InvalidTimestampError(SubtuneError):
    """Raised when a timestamp cannot be parsed."""

    pass


class FileProcessingError(SubtuneError):
    """Raised when file operations fail."""

    pass


class InvalidSRTFormatError(SubtuneError):
    """Raised when SRT file format is invalid."""

    pass


class InvalidOffsetError(SubtuneError):
    """Raised when offset value is invalid."""

    pass
