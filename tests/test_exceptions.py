import pytest

from subtune.core.exceptions import (
    FileProcessingError,
    InvalidOffsetError,
    InvalidSRTFormatError,
    InvalidTimestampError,
    SubtuneError,
)


class TestExceptionHierarchy:
    @pytest.mark.parametrize(
        "exc_class",
        [
            InvalidTimestampError,
            FileProcessingError,
            InvalidSRTFormatError,
            InvalidOffsetError,
        ],
    )
    def test_all_exceptions_inherit_from_subtune_error(self, exc_class):
        assert issubclass(exc_class, SubtuneError)

    def test_subtune_error_inherits_from_exception(self):
        assert issubclass(SubtuneError, Exception)

    @pytest.mark.parametrize(
        "exc_class",
        [
            SubtuneError,
            InvalidTimestampError,
            FileProcessingError,
            InvalidSRTFormatError,
            InvalidOffsetError,
        ],
    )
    def test_all_exceptions_inherit_from_exception(self, exc_class):
        assert issubclass(exc_class, Exception)


class TestExceptionInstantiation:
    @pytest.mark.parametrize(
        "exc_class,message",
        [
            (SubtuneError, "Test error"),
            (InvalidTimestampError, "Invalid timestamp"),
            (FileProcessingError, "File error"),
            (InvalidSRTFormatError, "Format error"),
            (InvalidOffsetError, "Offset error"),
        ],
    )
    def test_exception_creation_with_message(self, exc_class, message):
        error = exc_class(message)
        assert str(error) == message

    def test_exceptions_without_message(self):
        for exc_class in [
            SubtuneError,
            InvalidTimestampError,
            FileProcessingError,
            InvalidSRTFormatError,
            InvalidOffsetError,
        ]:
            error = exc_class()
            assert isinstance(error, exc_class)


class TestExceptionRaising:
    @pytest.mark.parametrize(
        "exc_class,message",
        [
            (SubtuneError, "Base error"),
            (InvalidTimestampError, "Bad timestamp"),
            (FileProcessingError, "File issue"),
            (InvalidSRTFormatError, "Format issue"),
            (InvalidOffsetError, "Offset issue"),
        ],
    )
    def test_raise_exceptions(self, exc_class, message):
        with pytest.raises(exc_class, match=message):
            raise exc_class(message)


class TestExceptionCatching:
    @pytest.mark.parametrize(
        "exc_class",
        [
            InvalidTimestampError,
            FileProcessingError,
            InvalidSRTFormatError,
            InvalidOffsetError,
        ],
    )
    def test_catch_specific_exceptions_as_subtune_error(self, exc_class):
        with pytest.raises(SubtuneError):
            raise exc_class("Test error")

    @pytest.mark.parametrize(
        "exc_class",
        [
            SubtuneError,
            InvalidTimestampError,
            FileProcessingError,
            InvalidSRTFormatError,
            InvalidOffsetError,
        ],
    )
    def test_catch_all_exceptions_as_exception(self, exc_class):
        # Test that our custom exceptions are instances of Exception
        try:
            raise exc_class("Test error")
        except Exception as e:
            assert isinstance(e, exc_class)
            assert isinstance(e, Exception)
            assert str(e) == "Test error"

    def test_exception_chaining_compatibility(self):
        original_error = ValueError("Original error")

        with pytest.raises(InvalidTimestampError) as exc_info:
            try:
                raise original_error
            except ValueError as e:
                raise InvalidTimestampError("Timestamp error") from e

        assert exc_info.value.__cause__ is original_error
