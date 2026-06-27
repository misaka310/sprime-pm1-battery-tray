import sys
import os

# Add src to sys.path to ensure absolute imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sprime_pm1_battery_tray.app import main

if __name__ == "__main__":
    main()
