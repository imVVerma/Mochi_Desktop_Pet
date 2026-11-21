import pytest
from ui.settings_dialog import SettingsDialog


def test_settings_dialog_save():
    saved_data = {}

    def mock_save(data):
        nonlocal saved_data
        saved_data = data

    test_config = {
        "pet_name": "Mochi",
        "base_color": "#FFB6C1",
        "scale": 1.0,
        "auto_color": True,
        "hotkeys": {"toggle_visibility": "alt+q"},
        "circadian": {"bedtime_hour": 23, "wake_hour": 7, "idle_dock_seconds": 15},
        "focus_mode": {"work_duration_minutes": 25, "break_duration_minutes": 5},
        "wellness_reminders": {"enabled": True, "interval_minutes": 20},
    }

    import tkinter as tk
    root = tk.Tk()
    root.withdraw()

    dialog = SettingsDialog(parent=root, config_data=test_config, on_save=mock_save)

    # Modify some fields in dialog
    dialog.var_name.set("BunnyHop")
    dialog.var_color.set("#A0C4FF")
    dialog.var_scale.set(1.2)
    dialog.var_hotkey.set("alt+z")

    # Trigger save
    dialog._save_and_apply()

    assert saved_data.get("pet_name") == "BunnyHop"
    assert saved_data.get("base_color") == "#A0C4FF"
    assert saved_data.get("scale") == 1.2
    assert saved_data.get("hotkeys", {}).get("toggle_visibility") == "alt+z"

    root.destroy()
