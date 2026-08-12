from pathlib import Path

from sprime_pm1_battery_tray import startup


def test_startup_shortcut_toggle(monkeypatch, tmp_path):
    monkeypatch.setenv("APPDATA", str(tmp_path))

    legacy_cleanup_calls = []

    def fake_create_shortcut(shortcut_path, target_path, arguments=""):
        path = Path(shortcut_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    monkeypatch.setattr(startup, "_create_shortcut", fake_create_shortcut)
    monkeypatch.setattr(startup, "_remove_legacy_run_entry", lambda: legacy_cleanup_calls.append(True))

    assert not startup.is_startup_enabled()

    startup.set_startup(True)
    assert startup.is_startup_enabled()

    startup.set_startup(False)
    assert not startup.is_startup_enabled()
    assert len(legacy_cleanup_calls) == 2


def test_powershell_quote_escapes_single_quotes():
    assert startup._powershell_quote("C:\\Users\\O'Brien") == "'C:\\Users\\O''Brien'"
