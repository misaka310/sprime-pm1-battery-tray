import hid
import time

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


def scan_devices():
    devices = hid.enumerate(VID, PID)
    return devices


def _decode_path(device):
    path = device.get('path', b'')
    if isinstance(path, bytes):
        return path.decode('ascii', errors='ignore')
    return path or ''


def _query_feature_report(device_path):
    h = hid.device()
    try:
        h.open_path(device_path)
        h.set_nonblocking(0)

        buf = bytearray(REPORT_LENGTH)
        buf[0] = FEATURE_REPORT_ID
        buf[1] = QUERY_COMMAND
        buf[4] = QUERY_FLAG

        h.send_feature_report(buf)
        time.sleep(0.05)
        return h.get_feature_report(FEATURE_REPORT_ID, REPORT_LENGTH)
    finally:
        try:
            h.close()
        except Exception:
            pass


def parse_battery_report(ret):
    if not ret or len(ret) < MIN_RESPONSE_LENGTH:
        return {"status": "read_failed", "error": "Invalid response length"}

    battery = ret[9]
    charging = bool(ret[10])
    full = bool(ret[11])
    online = bool(ret[12])

    if not online:
        return {"status": "disconnected", "battery": battery, "charging": charging, "full": full}
    return {"status": "connected", "battery": battery, "charging": charging, "full": full}


def select_sprime_device(devices):
    # The device that responds to feature report 5 is usually the one with a specific MI or Col.
    # Prefer Col04, then verify other matching HID endpoints by probing the feature report.
    for d in devices:
        if "Col04" in _decode_path(d):
            return d

    for d in devices:
        device_path = d.get('path')
        if not device_path:
            continue
        try:
            ret = _query_feature_report(device_path)
            if ret and len(ret) >= MIN_RESPONSE_LENGTH:
                return d
        except Exception:
            continue
    return None


def read_battery(device_path):
    try:
        ret = _query_feature_report(device_path)
    except Exception as e:
        error_text = str(e)
        lowered = error_text.lower()
        status = "permission_or_access_error" if "open" in lowered or "access" in lowered or "permission" in lowered else "read_failed"
        return {"status": status, "error": error_text}

    return parse_battery_report(ret)


def get_battery_info():
    devices = scan_devices()
    if not devices:
        return {"status": "device_not_found"}

    dev = select_sprime_device(devices)
    if not dev:
        return {"status": "protocol_unknown", "error": "Could not find compatible SPRIME endpoint"}

    return read_battery(dev['path'])
