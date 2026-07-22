import os
import sys

# Add src to sys.path to ensure absolute imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sprime_pm1_battery_tray.app import main
from sprime_pm1_battery_tray.single_instance import acquire_single_instance

if __name__ == "__main__" and acquire_single_instance():
    main()
