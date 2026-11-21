import pytest
from core.hotkeys import parse_hotkey, MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_NOREPEAT, GlobalHotkeyManager


def test_parse_hotkey_valid():
    # 2-key combos
    m1, v1 = parse_hotkey("alt+q")
    assert (m1 & MOD_ALT) != 0
    assert (m1 & MOD_NOREPEAT) != 0
    assert v1 == ord("Q")

    m2, v2 = parse_hotkey("ctrl+space")
    assert (m2 & MOD_CONTROL) != 0
    assert v2 == 0x20

    m3, v3 = parse_hotkey("alt+~")
    assert (m3 & MOD_ALT) != 0
    assert v3 == 0xC0

    # 3-key combo
    m4, v4 = parse_hotkey("ctrl+shift+b")
    assert (m4 & MOD_CONTROL) != 0
    assert (m4 & MOD_SHIFT) != 0
    assert v4 == ord("B")


def test_parse_hotkey_invalid_or_safety():
    # No modifier key (should be rejected for safety so normal typing is not hijacked)
    assert parse_hotkey("a") is None
    assert parse_hotkey("space") is None
    # Invalid key token
    assert parse_hotkey("ctrl+nonexistentkey") is None
    # Empty or non-string
    assert parse_hotkey("") is None
    assert parse_hotkey(None) is None


def test_global_hotkey_manager_lifecycle():
    received = []
    manager = GlobalHotkeyManager(
        on_toggle_visibility=lambda: received.append("toggle"),
        on_toggle_focus=lambda: received.append("focus"),
        on_pet=lambda: received.append("pet"),
    )

    # Start manager with test hotkeys
    manager.start({"toggle_visibility": "alt+q", "toggle_focus": "ctrl+shift+f"})
    assert manager._thread is not None
    assert manager._thread.is_alive()

    # Dynamic update
    manager.update_hotkeys({"toggle_visibility": "alt+z"})
    assert manager._current_hotkeys["toggle_visibility"] == "alt+z"

    # Stop cleanly
    manager.stop()
    assert manager._thread is None
