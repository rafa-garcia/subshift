# subshift

[![Tests](https://github.com/rafa-garcia/subshift/actions/workflows/test.yml/badge.svg)](https://github.com/rafa-garcia/subshift/actions/workflows/test.yml)

A CLI tool for adjusting SRT subtitle timestamps with precision and safety.

## Features

- **Precise timing adjustment** - Shift subtitles by milliseconds
- **Safe operations** - Optional backup creation before modifications  
- **Robust validation** - Input validation with helpful error messages

## Installation

Iinstall from source:
```bash
git clone https://github.com/rafa-garcia/subshift.git
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

### Command Reference
```
$ subshift --help
usage: subshift [-h] -o OFFSET [--output OUTPUT] [-b] [--version] input_file

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
pytest --cov=src/subshift

# Generate HTML coverage report
pytest --cov=src/subshift --cov-report=html
open htmlcov/index.html

# Check code quality
ruff check src/ tests/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
