#!/usr/bin/env python
"""Run pytest tests for bias tuner."""

import sys
import subprocess
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Run pytest
if __name__ == "__main__":
    cmd = [sys.executable, "-m", "pytest", "-v", "tests/"]
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    sys.exit(result.returncode)