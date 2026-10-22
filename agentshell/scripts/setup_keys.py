# agentshell/scripts/setup_keys.py
import sys
from pathlib import Path
from keys import run_setup_keys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # agentshell/

if __name__ == "__main__":
    run_setup_keys()

