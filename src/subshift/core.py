import re
from datetime import timedelta

def parse_timestamp(ts):
    h, m, s_ms = ts.split(":")
    s, ms = s_ms.split(",")
    return timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms))

def format_timestamp(td):
    total_seconds = int(td.total_seconds())
    ms = int(td.microseconds / 1000)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def shift_srt(input_file, output_file, offset_ms):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    offset = timedelta(milliseconds=offset_ms)

    with open(output_file, "w", encoding="utf-8") as f:
        for line in lines:
            match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", line)
            if match:
                start = parse_timestamp(match.group(1)) + offset
                end = parse_timestamp(match.group(2)) + offset
                start = max(start, timedelta(0))
                end = max(end, timedelta(0))
                f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            else:
                f.write(line)
