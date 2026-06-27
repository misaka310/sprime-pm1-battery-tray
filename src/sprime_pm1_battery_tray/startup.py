import winreg
import os
import sys

APP_NAME = "SPRIME PM1 Battery Tray"

def is_startup_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except WindowsError:
        return False

def set_startup(enable):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    if enable:
        if getattr(sys, 'frozen', False):
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
        except WindowsError:
            pass
    winreg.CloseKey(key)
