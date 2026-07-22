import time
import threading
import datetime
import pystray
from pystray import MenuItem as item
from PIL import Image
import queue
import os
import sys
import argparse
import customtkinter as ctk
import tkinter as tk

from .config import get_log_dir, load_config, save_config
from .hid_protocol import get_battery_info
from .icon_renderer import create_battery_icon
from .settings_window import SettingsWindow
from .startup import is_startup_enabled, set_startup


class BatteryTrayApp:
    def __init__(self):
        self.config = load_config()

        if getattr(sys, "frozen", False):
            set_startup(self.config.get("start_on_boot", False))

        self.current_status = {
            "device": "SPRIME PM1",
            "battery": "--",
            "status": "Initializing...",
            "last_update": "--",
            "last_error": "None",
            "charging": False,
            "full": False,
        }

        self.queue = queue.Queue()
        self.poll_lock = threading.Lock()

        self.root = ctk.CTk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0)
        ctk.set_appearance_mode("dark")

        self.settings_window = SettingsWindow(
            self.root,
            self.on_config_changed,
            lambda: self.queue.put(("manual_refresh", None)),
        )

        self.icon = pystray.Icon("sprime_pm1_battery")
        self.update_tray_icon()
        self.icon.menu = pystray.Menu(
            item("Refresh now", lambda: self.queue.put(("manual_refresh", None))),
            item("Show settings", lambda: self.queue.put(("show_settings", None))),
            item("Start on boot", self.toggle_start_on_boot, checked=lambda item: is_startup_enabled()),
            item("Open logs", lambda: self.queue.put(("open_logs", None))),
            item("Quit", lambda: self.queue.put(("quit", None))),
        )

        self.running = True
        self.last_poll_time = 0
        self.notified_low_battery = False

        self.process_queue()
        self.poll_thread = threading.Thread(target=self.poll_worker, daemon=True)
        self.poll_thread.start()

    def process_queue(self):
        """Processes events from the queue in the main thread."""
        try:
            while True:
                msg, data = self.queue.get_nowait()
                if msg == "update_status":
                    self.handle_update_status(data)
                elif msg == "show_settings":
                    self.settings_window.show(self.current_status)
                elif msg == "manual_refresh":
                    self.trigger_refresh()
                elif msg == "open_logs":
                    self.open_logs_folder()
                elif msg == "quit":
                    self.quit()
                    return
                self.queue.task_done()
        except queue.Empty:
            pass

        if self.running:
            self.root.after(100, self.process_queue)

    def trigger_refresh(self):
        """Force a poll immediately."""
        threading.Thread(target=self.poll_worker, args=(True,), daemon=True).start()

    def poll_once(self):
        """Read HID battery state once, unless another read is already active."""
        if not self.poll_lock.acquire(blocking=False):
            return None
        try:
            return get_battery_info()
        finally:
            self.poll_lock.release()

    def poll_worker(self, immediate=False):
        """Background thread for HID polling."""
        if not immediate:
            time.sleep(1)

        while self.running:
            res = self.poll_once()
            if res is not None:
                self.queue.put(("update_status", res))

            interval = self.config.get("refresh_interval_sec", 300)
            if immediate:
                return

            for _ in range(interval * 2):
                if not self.running:
                    break
                time.sleep(0.5)

    def handle_update_status(self, res):
        """Updates internal status and refreshes UI components."""
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        self.current_status["last_update"] = now_str

        if "error" in res:
            self.current_status["last_error"] = res["error"]
        else:
            self.current_status["last_error"] = "None"

        self.current_status["status"] = res.get("status", "unknown")

        if res.get("status") in ["connected", "disconnected"]:
            self.current_status["battery"] = res.get("battery", "--")
            self.current_status["charging"] = res.get("charging", False)
            self.current_status["full"] = res.get("full", False)

            if res.get("status") == "connected" and isinstance(self.current_status["battery"], int):
                thresh = self.config.get("low_battery_threshold", 20)
                if self.current_status["battery"] <= thresh and not self.current_status["charging"]:
                    if self.config.get("notify_low_battery", True) and not self.notified_low_battery:
                        self.icon.notify(f"Battery is low: {self.current_status['battery']}%", "SPRIME PM1")
                        self.notified_low_battery = True
                else:
                    self.notified_low_battery = False

        self.update_tray_icon()
        if self.settings_window.root:
            self.settings_window.update_status(self.current_status)

    def update_tray_icon(self):
        batt = self.current_status["battery"]
        perc = batt if isinstance(batt, int) else None
        status = self.current_status["status"]
        is_charging = self.current_status.get("charging", False)

        img = create_battery_icon(
            perc,
            status,
            is_charging,
            low_battery_threshold=self.config.get("low_battery_threshold", 20),
        )
        self.icon.icon = img

        if status == "connected" and perc is not None:
            self.icon.title = f"SPRIME PM1: {perc}%"
        elif status == "disconnected":
            self.icon.title = "SPRIME PM1: Disconnected"
        elif status == "device_not_found":
            self.icon.title = "SPRIME PM1: Device Not Found"
        else:
            self.icon.title = f"SPRIME PM1: {status}"

    def toggle_start_on_boot(self):
        enabled = not is_startup_enabled()
        set_startup(enabled)
        self.config["start_on_boot"] = enabled
        save_config(self.config)

    def open_logs_folder(self):
        log_dir = get_log_dir()
        os.makedirs(log_dir, exist_ok=True)
        os.startfile(log_dir)

    def on_config_changed(self, new_config):
        self.config = new_config
        self.update_tray_icon()

    def quit(self):
        self.running = False
        self.icon.stop()
        self.root.quit()
        self.root.destroy()

    def run(self):
        icon_thread = threading.Thread(target=self.icon.run)
        icon_thread.daemon = True
        icon_thread.start()
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="SPRIME PM1 Battery Tray")
    parser.add_argument("--smoke-test", action="store_true", help="Run a smoke test and exit")
    args = parser.parse_args()

    if args.smoke_test:
        print("Running smoke test...")
        try:
            import customtkinter as ctk
            import pystray

            print("Checking config...")
            load_config()

            print("Checking icon generation...")
            img = create_battery_icon(50, "connected", False)
            if img is None:
                print("Error: Icon generation failed")
                sys.exit(1)

            print("Checking HID reading...")
            res = get_battery_info()
            print(f"HID Result: {res}")

            print("Checking UI initialization...")
            root = ctk.CTk()
            SettingsWindow(root, lambda x: None, lambda: None)
            root.destroy()

            print("Smoke test passed!")
            sys.exit(0)

        except Exception as e:
            print(f"Smoke test failed with error: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)

    app = BatteryTrayApp()
    app.run()


if __name__ == "__main__":
    main()
