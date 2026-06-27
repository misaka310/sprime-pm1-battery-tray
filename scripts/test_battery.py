import hid
import time

def scan_devices():
    return hid.enumerate()

def test_battery():
    devices = hid.enumerate()
    candidates = []
    for d in devices:
        manufacturer = (d.get('manufacturer_string') or "").lower()
        product = (d.get('product_string') or "").lower()
        if "sprime" in manufacturer or "sprime" in product:
            candidates.append(d)
            
    if not candidates:
        print("No SPRIME candidates found")
        return
        
    for c in candidates:
        path = c['path']
        print(f"Trying device: {c['product_string']} (Path: {path})")
        try:
            h = hid.device()
            h.open_path(path)
            h.set_nonblocking(0)
            
            # Prepare feature report
            # Report ID 5 + 31 bytes
            buf = bytearray(32)
            buf[0] = 0x05
            buf[1] = 21 # a[0] = 21 in JS, which means data[0] is buf[1]
            buf[4] = 1  # a[3] = 1 in JS, which means data[3] is buf[4]
            
            # WebHID sendFeatureReport sends report ID 5 and data 'a'
            h.send_feature_report(buf)
            time.sleep(0.1)
            
            # WebHID receiveFeatureReport 
            ret = h.get_feature_report(0x05, 32)
            if ret:
                print(f"Response ({len(ret)} bytes): {[hex(x) for x in ret]}")
                if len(ret) >= 14:
                    battery = ret[10]
                    charging = ret[11]
                    fullCharge = ret[12]
                    online = ret[13]
                    print(f"Battery: {battery}%, Charging: {charging}, Full: {fullCharge}, Online: {online}")
            else:
                print("No response")
            h.close()
            print("---")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    test_battery()
