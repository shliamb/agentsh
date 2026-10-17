# agentshell/scripts/setup_keys.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # agentshell/

from keys import run_setup_keys

if __name__ == "__main__":
    run_setup_keys()

