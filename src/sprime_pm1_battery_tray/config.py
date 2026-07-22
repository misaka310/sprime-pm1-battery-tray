import json
import os


def _get_application_data_root():
    base = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.abspath(os.path.join(base, "SprimePM1BatteryTray"))


CONFIG_DIR = _get_application_data_root()
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "config_version": 3,
    "refresh_interval_sec": 300,
    "low_battery_threshold": 20,
    "notify_low_battery": True,
    "start_on_boot": False,
}


def get_log_dir():
    return os.path.join(CONFIG_DIR, "logs")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)

            merged = DEFAULT_CONFIG.copy()
            merged.update(cfg)
            return merged
    except (OSError, ValueError, TypeError):
        return DEFAULT_CONFIG.copy()


def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
