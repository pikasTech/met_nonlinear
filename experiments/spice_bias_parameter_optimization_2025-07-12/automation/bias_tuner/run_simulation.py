#!/usr/bin/env python
"""
Run the simulation test with proper module setup.
"""

import sys
import os
from pathlib import Path

# Set up module path
bias_tuner_path = Path(__file__).parent.parent
sys.path.insert(0, str(bias_tuner_path))

# Now we can import and run the simulation
from bias_tuner import simulation_test

if __name__ == "__main__":
    success = simulation_test.run_full_simulation()
    sys.exit(0 if success else 1)