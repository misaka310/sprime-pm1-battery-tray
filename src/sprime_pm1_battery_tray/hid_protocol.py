from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any

import hid

# Vendor ID and Product ID for SPRIME PM1
VID = 0x1915
PID = 0xAC1C

FEATURE_REPORT_ID = 0x05
QUERY_COMMAND = 0x15
QUERY_FLAG = 0x01
REPORT_LENGTH = 32
MIN_RESPONSE_LENGTH = 14


class SprimeDeviceError(Exception):
    pass


def scan_devices() -> list[dict[str, Any]]:
    return list(hid.enumerate(VID, PID))


def _decode_path(device: dict[str, Any]) -> str:
    path = device.get("path", b"")
    if isinstance(path, bytes):
        return path.decode("ascii", errors="ignore")
    return str(path or "")


def _query_feature_report(device_path: Any) -> Sequence[int]:
    handle = hid.device()
    try:
        handle.open_path(device_path)
        handle.set_nonblocking(0)

        buf = bytearray(REPORT_LENGTH)
        buf[0] = FEATURE_REPORT_ID
        buf[1] = QUERY_COMMAND
        buf[4] = QUERY_FLAG

        sent = handle.send_feature_report(buf)
        if not isinstance(sent, int) or sent <= 0:
            raise SprimeDeviceError("HID feature report command was not accepted")
        time.sleep(0.05)
        response = handle.get_feature_report(FEATURE_REPORT_ID, REPORT_LENGTH)
        if response is None:
            raise SprimeDeviceError("HID feature report returned no response")
        return response
    finally:
        try:
            handle.close()
        except Exception:
            pass


def parse_battery_report(ret: Sequence[int] | None) -> dict[str, Any]:
    if not ret or len(ret) < MIN_RESPONSE_LENGTH:
        return {"status": "read_failed", "error": "Invalid response length"}

    try:
        battery = int(ret[9])
        charging_raw = int(ret[10])
        full_raw = int(ret[11])
        online_raw = int(ret[12])
    except (IndexError, TypeError, ValueError) as exc:
        return {"status": "invalid_report", "error": f"Invalid report values: {exc}"}

    if not 0 <= battery <= 100:
        return {"status": "invalid_report", "error": f"Battery value out of range: {battery}"}
    invalid_flags = {
        "charging": charging_raw,
        "full": full_raw,
        "online": online_raw,
    }
    invalid_flags = {name: value for name, value in invalid_flags.items() if value not in (0, 1)}
    if invalid_flags:
        detail = ", ".join(f"{name}={value}" for name, value in invalid_flags.items())
        return {"status": "invalid_report", "error": f"Invalid boolean flag values: {detail}"}

    charging = bool(charging_raw)
    full = bool(full_raw)
    online = bool(online_raw)

    if not online:
        return {"status": "disconnected", "battery": battery, "charging": charging, "full": full}
    return {"status": "connected", "battery": battery, "charging": charging, "full": full}


def select_sprime_device(devices: Sequence[dict[str, Any]]) -> dict[str, Any] | None:
    # The device that responds to feature report 5 is usually the one with a specific MI or Col.
    # Prefer Col04, then verify other matching HID endpoints by probing the feature report.
    for device in devices:
        if "col04" in _decode_path(device).lower():
            return device

    for device in devices:
        device_path = device.get("path")
        if not device_path:
            continue
        try:
            ret = _query_feature_report(device_path)
            if ret and len(ret) >= MIN_RESPONSE_LENGTH:
                return device
        except Exception:
            continue
    return None


def read_battery(device_path: Any) -> dict[str, Any]:
    try:
        ret = _query_feature_report(device_path)
    except Exception as exc:
        error_text = str(exc)
        lowered = error_text.lower()
        status = (
            "permission_or_access_error"
            if "open" in lowered or "access" in lowered or "permission" in lowered
            else "read_failed"
        )
        return {"status": status, "error": error_text or exc.__class__.__name__}

    return parse_battery_report(ret)


def get_battery_info() -> dict[str, Any]:
    try:
        devices = scan_devices()
    except Exception as exc:
        return {"status": "enumeration_failed", "error": str(exc) or exc.__class__.__name__}

    if not devices:
        return {"status": "device_not_found"}

    dev = select_sprime_device(devices)
    if not dev:
        return {"status": "protocol_unknown", "error": "Could not find compatible SPRIME endpoint"}
    device_path = dev.get("path")
    if not device_path:
        return {"status": "protocol_unknown", "error": "Compatible SPRIME endpoint has no HID path"}
    return read_battery(device_path)
