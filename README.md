# subtune

[![Tests](https://github.com/rafa-garcia/subtune/actions/workflows/test.yml/badge.svg)](https://github.com/rafa-garcia/subtune/actions/workflows/test.yml)
[![Release](https://github.com/rafa-garcia/subtune/actions/workflows/release.yml/badge.svg)](https://github.com/rafa-garcia/subtune/actions/workflows/release.yml)

A CLI tool for adjusting SRT subtitle timestamps with precision and safety.

## Features

- **Precise timing adjustment** - Shift subtitles by milliseconds
- **Safe operations** - Optional backup creation before modifications  
- **Robust validation** - Input validation with helpful error messages

## Installation

Install from PyPI:
```bash
pip install subtune
```

Or install from source:
```bash
git clone https://github.com/rafa-garcia/subtune.git
cd subtune
pip install .
```

## Usage

### Basic Usage
```bash
# Shift subtitles 2 seconds later
subtune input.srt --offset 2000 output.srt

# Shift subtitles 1.5 seconds earlier  
subtune input.srt --offset -1500 output.srt
```

### Advanced Options
```bash
# Modify in-place with backup
subtune input.srt --offset 1000 --backup

# Short flags
subtune input.srt -o 1000 -b
```

### Command Reference
```
$ subtune --help
usage: subtune [-h] -o OFFSET [--output OUTPUT] [-b] [--version] input_file

Shift SRT subtitle timestamps by a specified offset

positional arguments:
  input_file            Input SRT file path

optional arguments:
  -h, --help            show this help message and exit
  -o OFFSET, --offset OFFSET
                        Time offset in milliseconds (positive=forward,
                        negative=backward)
  --output OUTPUT       Output file path (default: modify input file in-place)
  -b, --backup          Create backup of input file before modification
  --version             show program's version number and exit
```

## Development

### Quick Start
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Verbose output with details
pytest -v

# Run specific test file
pytest tests/test_cli.py

# Run tests with coverage
pytest --cov=src/subtune

# Generate HTML coverage report
pytest --cov=src/subtune --cov-report=html
open htmlcov/index.html

# Check code quality
ruff check src/ tests/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
