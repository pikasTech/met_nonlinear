# Logger Module Documentation

## Overview

This module provides tools for converting print statements to structured logging. All actual log file creation is handled by the subprocess wrapper (`cli_wrapper.py`).

## Key Components

### print_replacer.py  
Automated tool to convert print() statements to logger calls:
- Uses AST to parse Python code
- Intelligently detects log levels based on content
- Handles f-string syntax limitations

### print_checker.py
Tool to scan codebase for print() usage:
- Returns file paths and line numbers
- Used for identifying print statements to replace

## Usage

### Running print replacement
```bash
python -m logger.print_replacer cli.py
python -m logger.print_replacer inference/ --recursive
```

### Checking for print statements
```bash
python -m logger.print_checker . --recursive
```

### Running tests
```bash
pytest logger/tests/ -v
```

## Common Issues

### F-string Syntax Errors
When replacing print statements, watch for:
- `f'{'=' * 60}'` → Use variable: `separator = '=' * 60; f'{separator}'`
- `f'{dict['key']}'` → Use double quotes: `f"{dict['key']}"`
- `f'{func('arg')}'` → Extract to variable first

### Missing Imports
If you see `NameError: name 'logging' is not defined`:
- Add `import logging` at the top of the file
- Ensure it's before any `logger = logging.getLogger()` calls

## Important Notes

1. **Single Log File**: Only `cli_wrapper.py` creates log files. The main program (`cli.py`) uses standard logging to stdout/stderr.

2. **No Dual Logging**: All logging goes through the wrapper to avoid creating multiple log files.

## Lint/Check Commands

```bash
# Check all print statements have been replaced
python -m logger.print_checker . --recursive | grep -v "logger/"

# Run linting on logger code
ruff check logger/
black logger/ --check
```