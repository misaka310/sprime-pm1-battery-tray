import winreg
import os
import sys

APP_NAME = "SPRIME PM1 Battery Tray"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def is_startup_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except OSError:
        return False


def set_startup(enable):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE)
    except FileNotFoundError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY)

    if enable:
        if getattr(sys, "frozen", False):
            # Running as PyInstaller executable
            exe_path = sys.executable
            cmd = f'"{exe_path}"'
        else:
            # Running as python script
            script_path = os.path.abspath(sys.argv[0])
            python_path = sys.executable
            cmd = f'"{python_path}" "{script_path}"'
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
    else:
        try:
            winreg.DeleteValue(key, APP_NAME)
        except OSError:
            pass
    winreg.CloseKey(key)
