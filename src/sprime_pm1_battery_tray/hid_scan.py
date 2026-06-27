import hid
import json
import os

def scan_devices():
    devices = hid.enumerate()
    return devices

def get_sprime_candidates(devices):
    # Known SPRIME VIDs (Need to verify, but common ones are 0x3785, 0x3642, etc.)
    # I will search for SPRIME in the manufacturer_string or product_string
    candidates = []
    for d in devices:
        manufacturer = (d.get('manufacturer_string') or "").lower()
        product = (d.get('product_string') or "").lower()
        if "sprime" in manufacturer or "sprime" in product:
            candidates.append(d)
    return candidates

def dump_devices(devices, log_path_json, log_path_txt):
    os.makedirs(os.path.dirname(log_path_json), exist_ok=True)
    
    # Prepare for JSON
    serializable_devices = []
    for d in devices:
        sd = d.copy()
        if isinstance(sd.get('path'), bytes):
            sd['path'] = sd['path'].decode('ascii', errors='ignore')
        serializable_devices.append(sd)

    # JSON dump
    with open(log_path_json, 'w', encoding='utf-8') as f:
        json.dump(serializable_devices, f, indent=4, ensure_ascii=False)
    
    # TXT dump for easier reading
    with open(log_path_txt, 'w', encoding='utf-8') as f:
        for d in devices:
            line = f"VID: 0x{d['vendor_id']:04x}, PID: 0x{d['product_id']:04x}, " \
                   f"Mfr: {d['manufacturer_string']}, Prod: {d['product_string']}, " \
                   f"Ser: {d['serial_number']}, UsagePage: 0x{d['usage_page']:04x}, Usage: 0x{d['usage']:04x}, " \
                   f"Path: {d['path'].decode('ascii', errors='ignore') if isinstance(d['path'], bytes) else d['path']}\n"
            f.write(line)

if __name__ == "__main__":
    devs = scan_devices()
    dump_devices(devs, "logs/hid-devices.json", "logs/hid-devices.txt")
    candidates = get_sprime_candidates(devs)
    print(f"Found {len(devs)} HID devices.")
    print(f"Found {len(candidates)} SPRIME candidates.")
    for c in candidates:
        print(f"- VID: 0x{c['vendor_id']:04x}, PID: 0x{c['product_id']:04x}, Prod: {c['product_string']}")
