import os
import sys
import winreg

APP_NAME = "SPRIME PM1 Battery Tray"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def is_startup_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
        return True
    except OSError:
        return False


def set_startup(enable):
    if not enable:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except OSError:
                    pass
        except OSError:
            pass
        return

    if getattr(sys, "frozen", False):
        exe_path = sys.executable
        cmd = f'"{exe_path}"'
    else:
        script_path = os.path.abspath(sys.argv[0])
        python_path = sys.executable
        cmd = f'"{python_path}" "{script_path}"'

    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
