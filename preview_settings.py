#!/usr/bin/env python3
"""
Interactive & Headless Preview Launcher for Redesigned Mochi Preferences & Wardrobe.
Renders the contemporary warm & cozy aesthetic and captures a high-resolution preview screenshot.
"""
import os
import sys
import time
import tkinter as tk
from PIL import ImageGrab

from core.pal.window import apply_dpi_awareness
from ui.settings_dialog import SettingsDialog

apply_dpi_awareness()

def main():
    root = tk.Tk()
    root.withdraw()

    test_config = {
        "pet_name": "Mochi",
        "species": "bunny",
        "home_corner": "bottom_right",
        "scale": 1.0,
        "base_color": "#FFF4D2",
        "auto_color": True,
        "eye_color": "#2C3E50",
        "walk_speed": 3.0,
        "taskbar_height": 45,
        "transparent_color": "#000001",
        "sound_enabled": False,
        "accessory": "🧣 Cozy Scarf",
        "focus_mode": {
            "work_duration_minutes": 25,
            "break_duration_minutes": 5,
            "auto_break": True
        },
        "wellness_reminders": {
            "enabled": True,
            "interval_minutes": 20,
            "messages": [
                "Time to drink some water! 💧",
                "Look 20 feet away for 20 seconds! 👁️",
                "Posture check! Sit up comfortably. 🪑"
            ]
        },
        "circadian": {
            "bedtime_hour": 23,
            "wake_hour": 7,
            "idle_sleep_seconds": 180,
            "idle_dock_seconds": 5
        },
        "hotkeys": {
            "toggle_visibility": "alt+q",
            "toggle_focus": "ctrl+shift+f",
            "pet": "ctrl+shift+p"
        }
    }

    def on_save(cfg):
        print(f"[Preview] Saved config: {cfg}")

    dialog = SettingsDialog(parent=root, config_data=test_config, on_save=on_save)
    dialog.notebook.select(2)  # Habits & Focus tab
    dialog.window.update_idletasks()
    dialog.window.update()

    # Capture preview screenshot after rendering
    time.sleep(0.3)
    dialog.window.update()

    try:
        x = dialog.window.winfo_rootx()
        y = dialog.window.winfo_rooty()
        w = dialog.window.winfo_width()
        h = dialog.window.winfo_height()

        screenshot_path = os.path.join(os.path.dirname(__file__), "dist", "mochi_settings_redesign_preview.png")
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save(screenshot_path)
        print(f"[Preview] Screenshot successfully saved to {screenshot_path}")
    except Exception as e:
        print(f"[Preview] Screenshot capture note: {e}")

    # If run with --capture-only, close immediately, otherwise run event loop
    if "--capture-only" in sys.argv:
        dialog.window.destroy()
        root.destroy()
    else:
        root.mainloop()

if __name__ == "__main__":
    main()
