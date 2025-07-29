# subshift

[![Tests](https://github.com/rafa-garcia/subshift/actions/workflows/test.yml/badge.svg)](https://github.com/rafagarcia/subshift/actions/workflows/test.yml)

A CLI tool for adjusting SRT subtitle timestamps with precision and safety.

## Features

- **Precise timing adjustment** - Shift subtitles by milliseconds
- **Safe operations** - Optional backup creation before modifications  
- **Robust validation** - Input validation with helpful error messages

## Installation

Install from source:
```bash
git clone https://github.com/rafagarcia/subshift.git
cd subshift
pip install .
```

## Usage

### Basic Usage
```bash
# Shift subtitles 2 seconds later
subshift input.srt --offset 2000 output.srt

# Shift subtitles 1.5 seconds earlier  
subshift input.srt --offset -1500 output.srt
```

### Advanced Options
```bash
# Modify in-place with backup
subshift input.srt --offset 1000 --backup

# Short flags
subshift input.srt -o 1000 -b
```

## Development

### Running Tests
```bash
PYTHONPATH=src python -m pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

