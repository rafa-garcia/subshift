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
    parser = argparse.ArgumentParser(description="Shift subtitle timings in milliseconds.")
    parser.add_argument("input", help="Input .srt file")
    parser.add_argument("offset", type=int, help="Offset in milliseconds (e.g., -24000)")
    parser.add_argument("output", help="Output .srt file")
    args = parser.parse_args()

    try:
        shift_srt(args.input, args.output, args.offset)
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
