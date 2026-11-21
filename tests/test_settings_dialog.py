import pytest
import tkinter as tk
from ui.settings_dialog import SettingsDialog


def test_settings_dialog_end_to_end():
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

    root = tk.Tk()
    root.withdraw()

    dialog = SettingsDialog(parent=root, config_data=test_config, on_save=mock_save)

    # 1. Test Swatch Selection & Visual checkmarks without shrinking
    dialog._select_swatch("#D0BDF4")
    assert dialog.var_color.get() == "#D0BDF4"

    lavender_card = dialog.swatch_cards["#D0BDF4"]
    pink_card = dialog.swatch_cards["#FFB6C1"]
    assert lavender_card[1].cget("text") == "✓"
    assert pink_card[1].cget("text") == ""

    # 2. Test flexible hotkey selection without forced Alt
    dialog._set_hotkey("ctrl+space")
    assert dialog.var_hotkey.get() == "ctrl+space"
    assert "[Ctrl] + [Space]" in dialog.lbl_hotkey_caps.cget("text")

    dialog._set_hotkey("f8")
    assert dialog.var_hotkey.get() == "f8"
    assert "[F8]" in dialog.lbl_hotkey_caps.cget("text")

    # 3. Test modifying attributes and saving
    dialog.var_name.set("BunnyHop")
    dialog._select_swatch("#A0C4FF")
    dialog._select_accessory("👑 Royal Crown")
    dialog.var_scale.set(1.2)
    dialog._set_hotkey("ctrl+shift+b")

    # Trigger save
    dialog._save_and_apply()

    assert saved_data.get("pet_name") == "BunnyHop"
    assert saved_data.get("base_color") == "#A0C4FF"
    assert saved_data.get("accessory") == "👑 Royal Crown"
    assert saved_data.get("scale") == 1.2
    assert saved_data.get("hotkeys", {}).get("toggle_visibility") == "ctrl+shift+b"

    root.destroy()
