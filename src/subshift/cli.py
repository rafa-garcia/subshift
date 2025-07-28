import argparse
import sys
from .core import shift_srt
from .exceptions import (
    SubshiftError,
    InvalidTimestampError,
    FileProcessingError,
    InvalidSRTFormatError,
    InvalidOffsetError,
)


def main():
    parser = argparse.ArgumentParser(
        description="Shift subtitle timings in milliseconds.",
        epilog="Examples:\n"
        "  subshift input.srt --offset -24000 --output output.srt\n"
        "  subshift input.srt -o output.srt --offset -5000\n"
        "  subshift input.srt --offset +2000  # overwrites input file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("input", help="Input .srt file")
    parser.add_argument(
        "--offset",
        "-s",
        type=int,
        required=True,
        help="Offset in milliseconds (e.g., -24000 for 24 seconds earlier)",
    )
    parser.add_argument(
        "--output", "-o", help="Output .srt file (default: overwrites input file)"
    )
    parser.add_argument(
        "--backup",
        "-b",
        action="store_true",
        help="Create backup of input file before processing",
    )

    args = parser.parse_args()

    # Set output file default
    if not args.output:
        args.output = args.input

    try:
        # Create backup if requested
        if args.backup:
            import shutil
            from pathlib import Path

            backup_path = Path(args.input).with_suffix(".srt.backup")
            shutil.copy2(args.input, backup_path)
            print(f"Backup created: {backup_path}")

        shift_srt(args.input, args.output, args.offset)

        if args.output == args.input:
            print(f"Subtitles shifted by {args.offset} ms in-place")
        else:
            print(f"Subtitles shifted by {args.offset} ms and saved to {args.output}")

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

    except SubshiftError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(5)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(99)
