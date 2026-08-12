import os
import subprocess
import sys
import winreg

APP_NAME = "SPRIME PM1 Battery Tray"
SHORTCUT_NAME = f"{APP_NAME}.lnk"
LEGACY_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _startup_dir():
    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")


def _startup_shortcut_path():
    return os.path.join(_startup_dir(), SHORTCUT_NAME)


def _powershell_quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def _launch_target():
    if getattr(sys, "frozen", False):
        return os.path.abspath(sys.executable), ""

    script_path = os.path.abspath(sys.argv[0])
    return os.path.abspath(sys.executable), f'"{script_path}"'


def _create_shortcut(shortcut_path, target_path, arguments=""):
    working_dir = os.path.dirname(target_path)
    ps = (
        "$shell = New-Object -ComObject WScript.Shell; "
        f"$shortcut = $shell.CreateShortcut({_powershell_quote(shortcut_path)}); "
        f"$shortcut.TargetPath = {_powershell_quote(target_path)}; "
        f"$shortcut.WorkingDirectory = {_powershell_quote(working_dir)}; "
        f"$shortcut.IconLocation = {_powershell_quote(target_path + ',0')}; "
        f"$shortcut.Description = {_powershell_quote('SPRIME PM1 battery monitor')}; "
        f"$shortcut.Arguments = {_powershell_quote(arguments)}; "
        "$shortcut.Save()"
    )
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps],
        check=True,
        creationflags=creationflags,
    )


def _remove_legacy_run_entry():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, LEGACY_RUN_KEY, 0, winreg.KEY_SET_VALUE)
    except OSError:
        return

    try:
        winreg.DeleteValue(key, APP_NAME)
    except OSError:
        pass
    finally:
        winreg.CloseKey(key)


def is_startup_enabled():
    return os.path.isfile(_startup_shortcut_path())


def set_startup(enable):
    shortcut_path = _startup_shortcut_path()

    if enable:
        os.makedirs(_startup_dir(), exist_ok=True)
        target_path, arguments = _launch_target()
        _create_shortcut(shortcut_path, target_path, arguments)
    else:
        try:
            os.remove(shortcut_path)
        except FileNotFoundError:
            pass

    # Migrate away from the older HKCU\...\Run registration so there is only
    # one auto-start mechanism and Windows Startup remains easy to inspect.
    _remove_legacy_run_entry()
