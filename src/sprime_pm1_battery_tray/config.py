import json
import os

CONFIG_DIR = os.path.join(os.environ.get('APPDATA', ''), 'SprimePM1BatteryTray')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

DEFAULT_CONFIG = {
    "config_version": 3,
    "refresh_interval_sec": 300,
    "low_battery_threshold": 20,
    "notify_low_battery": True,
    "start_on_boot": False
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            
            # Merge with defaults
            merged = DEFAULT_CONFIG.copy()
            merged.update(cfg)
            return merged
    except:
        return DEFAULT_CONFIG.copy()


def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
