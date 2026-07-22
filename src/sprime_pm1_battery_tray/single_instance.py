from __future__ import annotations

import ctypes
import os

_MUTEX_NAME = "Local\\SPRIME_PM1_Battery_Tray_SingleInstance"
_ERROR_ALREADY_EXISTS = 183
_mutex_handle: int | None = None


def acquire_single_instance() -> bool:
    """Keep one application instance per logged-in Windows session."""
    global _mutex_handle

    if os.name != "nt":
        return True

    kernel32 = ctypes.windll.kernel32
    create_mutex = kernel32.CreateMutexW
    create_mutex.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
    create_mutex.restype = ctypes.c_void_p

    handle = create_mutex(None, False, _MUTEX_NAME)
    if not handle:
        raise ctypes.WinError()

    if kernel32.GetLastError() == _ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(ctypes.c_void_p(handle))
        return False

    _mutex_handle = int(handle)
    return True
