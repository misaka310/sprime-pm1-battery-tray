import pytest
import winreg
from sprime_pm1_battery_tray.startup import is_startup_enabled, set_startup

def test_startup_dryrun(monkeypatch):
    # Mock winreg to avoid actually writing to registry during test
    store = {}
    
    class MockKey:
        pass
        
    def mock_open_key(*args):
        return MockKey()
        
    def mock_query_value_ex(key, name):
        if name in store:
            return store[name], 1
        raise WindowsError("File not found")
        
    def mock_set_value_ex(key, name, reserved, type, value):
        store[name] = value
        
    def mock_delete_value(key, name):
        if name in store:
            del store[name]
        else:
            raise WindowsError("File not found")
            
    def mock_close_key(key):
        pass

    monkeypatch.setattr(winreg, "OpenKey", mock_open_key)
    monkeypatch.setattr(winreg, "QueryValueEx", mock_query_value_ex)
    monkeypatch.setattr(winreg, "SetValueEx", mock_set_value_ex)
    monkeypatch.setattr(winreg, "DeleteValue", mock_delete_value)
    monkeypatch.setattr(winreg, "CloseKey", mock_close_key)

    # Initial state should be false
    assert not is_startup_enabled()

    # Set to true
    set_startup(True)
    assert is_startup_enabled()

    # Set to false
    set_startup(False)
    assert not is_startup_enabled()
