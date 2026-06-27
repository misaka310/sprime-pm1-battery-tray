from sprime_pm1_battery_tray.hid_protocol import parse_battery_report, select_sprime_device


def test_parse_connected_battery_report():
    report = [0] * 32
    report[9] = 96
    report[10] = 0
    report[11] = 0
    report[12] = 1

    res = parse_battery_report(report)

    assert res == {
        "status": "connected",
        "battery": 96,
        "charging": False,
        "full": False,
    }


def test_parse_charging_full_battery_report():
    report = [0] * 32
    report[9] = 100
    report[10] = 1
    report[11] = 1
    report[12] = 1

    res = parse_battery_report(report)

    assert res["status"] == "connected"
    assert res["battery"] == 100
    assert res["charging"] is True
    assert res["full"] is True


def test_parse_disconnected_battery_report():
    report = [0] * 32
    report[9] = 55
    report[12] = 0

    res = parse_battery_report(report)

    assert res["status"] == "disconnected"
    assert res["battery"] == 55


def test_parse_invalid_response_length():
    res = parse_battery_report([0] * 8)

    assert res["status"] == "read_failed"
    assert "Invalid response length" in res["error"]


def test_select_sprime_device_prefers_col04():
    devices = [
        {"path": b"\\\\?\\hid#vid_1915&pid_ac1c&mi_01&col02"},
        {"path": b"\\\\?\\hid#vid_1915&pid_ac1c&mi_01&Col04"},
    ]

    selected = select_sprime_device(devices)

    assert selected is devices[1]
