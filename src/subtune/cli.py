import sys
from argparse import ArgumentParser
from pathlib import Path

from .core.exceptions import (
    FileProcessingError,
    InvalidOffsetError,
    InvalidSRTFormatError,
    InvalidTimestampError,
    SubtuneError,
)
from .core.workflow import SubtitleProcessor


def create_parser():
    parser = ArgumentParser(
        prog="subtune",
        description="Shift SRT subtitle timestamps by a specified offset",
        epilog="Examples:\n"
        "  subtune input.srt --offset 2000 --output output.srt  # Shift forward 2 seconds\n"
        "  subtune input.srt -o -1500 --backup                  # Shift back 1.5s with backup\n"
        "  subtune input.srt -o 500                             # Shift forward 0.5s in-place",
        formatter_class=ArgumentParser().formatter_class,
    )

    parser.add_argument("input_file", help="Input SRT file path")

    parser.add_argument(
        "-o",
        "--offset",
        type=int,
        required=True,
        help="Time offset in milliseconds (positive=forward, negative=backward)",
    )

    parser.add_argument("--output", help="Output file path (default: modify input file in-place)")

    parser.add_argument(
        "-b",
        "--backup",
        action="store_true",
        help="Create backup of input file before modification",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    return parser


def main():
    parser = create_parser()

    try:
        args = parser.parse_args()

        input_path = Path(args.input_file)
        output_path = Path(args.output) if args.output else input_path

        processor = SubtitleProcessor()

        processor.shift_srt_file(
            input_path=input_path,
            output_path=output_path,
            offset_ms=args.offset,
            create_backup=args.backup,
        )

        if args.output:
            print(f"Shifted timestamps by {args.offset}ms and saved to {args.output}")
        else:
            print(f"Shifted timestamps by {args.offset}ms in-place")

    except FileProcessingError as e:
        print(f"File error: {e}", file=sys.stderr)
        sys.exit(1)

    except InvalidSRTFormatError as e:
        print(f"SRT format error: {e}", file=sys.stderr)
        sys.exit(2)

    except InvalidTimestampError as e:
        print(f"Timestamp error: {e}", file=sys.stderr)
        sys.exit(3)

    except InvalidOffsetError as e:
        print(f"Offset error: {e}", file=sys.stderr)
        sys.exit(4)

    except SubtuneError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(5)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(99)


if __name__ == "__main__":
    main()
