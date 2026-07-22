import importlib
import os
from pathlib import Path


def test_log_directory_is_stable_across_working_directories(monkeypatch, tmp_path):
    appdata = tmp_path / "appdata"
    first_cwd = tmp_path / "first"
    second_cwd = tmp_path / "second"
    first_cwd.mkdir()
    second_cwd.mkdir()

    monkeypatch.setenv("APPDATA", str(appdata))
    monkeypatch.delenv("LOCALAPPDATA", raising=False)

    from sprime_pm1_battery_tray import config

    config = importlib.reload(config)
    expected = (appdata / "SprimePM1BatteryTray" / "logs").resolve()

    original_cwd = Path.cwd()
    try:
        os.chdir(first_cwd)
        first = Path(config.get_log_dir()).resolve()
        os.chdir(second_cwd)
        second = Path(config.get_log_dir()).resolve()
    finally:
        os.chdir(original_cwd)

    assert first == expected
    assert second == expected
    assert first.is_absolute()
