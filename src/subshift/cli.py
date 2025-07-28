import argparse
from .core import shift_srt

def main():
    parser = argparse.ArgumentParser(description="Shift subtitle timings in milliseconds.")
    parser.add_argument("input", help="Input .srt file")
    parser.add_argument("offset", type=int, help="Offset in milliseconds (e.g., -24000)")
    parser.add_argument("output", help="Output .srt file")
    args = parser.parse_args()

    shift_srt(args.input, args.output, args.offset)
    print(f"Subtitles shifted by {args.offset} ms and saved to {args.output}")
