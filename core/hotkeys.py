"""
Global Hotkey Manager for Windows.
Provides non-administrator, user-mode hotkey registration with dynamic config parsing,
proper Win32 message queue pumping, and runtime hot-reloading.
"""
import ctypes
import logging
import sys
import threading
from typing import Callable, Dict, Optional, Tuple

logger = logging.getLogger("DesktopPet.Hotkeys")

# Win32 Modifier Constants
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

# Virtual Key Mapping
VK_MAP: Dict[str, int] = {
    "tab": 0x09,
    "space": 0x20,
    "enter": 0x0D,
    "return": 0x0D,
    "esc": 0x1B,
    "escape": 0x1B,
    "backspace": 0x08,
    "tilde": 0xC0,
    "`": 0xC0,
    "~": 0xC0,
    "-": 0xBD,
    "=": 0xBB,
    "[": 0xDB,
    "]": 0xDD,
    "\\": 0xDC,
    ";": 0xBA,
    "'": 0xDE,
    ",": 0xBC,
    ".": 0xBE,
    "/": 0xBF,
    "capslock": 0x14,
    "pause": 0x13,
    "pageup": 0x21,
    "pagedown": 0x22,
    "end": 0x23,
    "home": 0x24,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "insert": 0x2D,
    "delete": 0x2E,
}

# Add standard letters a-z
for _c in range(ord('a'), ord('z') + 1):
    VK_MAP[chr(_c)] = 0x41 + (_c - ord('a'))

# Add numbers 0-9
for _c in range(ord('0'), ord('9') + 1):
    VK_MAP[chr(_c)] = 0x30 + (_c - ord('0'))

# Add function keys F1-F24
for _i in range(1, 25):
    VK_MAP[f"f{_i}"] = 0x70 + (_i - 1)

# Add Numpad 0-9
for _i in range(0, 10):
    VK_MAP[f"num{_i}"] = 0x60 + _i
    VK_MAP[f"numpad{_i}"] = 0x60 + _i


def parse_hotkey(hotkey_str: str) -> Optional[Tuple[int, int]]:
    """
    Parses a hotkey string like 'alt+q', 'ctrl+shift+b', 'ctrl+space', 'alt+~'.
    Returns (fsModifiers, vk_code) or None if parsing fails.
    """
    if not hotkey_str or not isinstance(hotkey_str, str):
        return None

    tokens = [p.strip().lower() for p in hotkey_str.replace("+", " ").split() if p.strip()]
    if not tokens:
        return None

    mods = MOD_NOREPEAT
    vk = None

    for token in tokens:
        if token in ("ctrl", "control"):
            mods |= MOD_CONTROL
        elif token == "alt":
            mods |= MOD_ALT
        elif token == "shift":
            mods |= MOD_SHIFT
        elif token in ("win", "windows", "super"):
            mods |= MOD_WIN
        else:
            if token in VK_MAP:
                vk = VK_MAP[token]
            elif len(token) == 1 and token.lower() in VK_MAP:
                vk = VK_MAP[token.lower()]

    if vk is None:
        logger.warning("Could not identify virtual key from token in: %s", hotkey_str)
        return None

    # Must have at least one modifier to avoid hijacking raw typing keys
    if (mods & (MOD_ALT | MOD_CONTROL | MOD_SHIFT | MOD_WIN)) == 0:
        logger.warning("Hotkey '%s' has no modifier key (Ctrl, Alt, Shift, or Win). Ignored for safety.", hotkey_str)
        return None

    return mods, vk


class GlobalHotkeyManager:
    """
    Manages non-admin global hotkeys using Windows RegisterHotKey with a dedicated
    message pump thread and thread-safe callbacks.
    """

    def __init__(
        self,
        on_toggle_visibility: Optional[Callable[[], None]] = None,
        on_toggle_focus: Optional[Callable[[], None]] = None,
        on_pet: Optional[Callable[[], None]] = None,
    ):
        self.on_toggle_visibility = on_toggle_visibility
        self.on_toggle_focus = on_toggle_focus
        self.on_pet = on_pet

        self._thread: Optional[threading.Thread] = None
        self._thread_id: Optional[int] = None
        self._stop_event = threading.Event()
        self._registered_ids: Dict[int, str] = {}
        self._current_hotkeys: Dict[str, str] = {}

    def start(self, hotkeys_config: Optional[Dict[str, str]] = None) -> None:
        """Starts the background hotkey listener thread."""
        if sys.platform != "win32":
            return

        self._current_hotkeys = hotkeys_config or {}
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="DesktopPetHotkeys")
        self._thread.start()

    def update_hotkeys(self, hotkeys_config: Dict[str, str]) -> None:
        """Dynamically re-registers hotkeys if configuration changed."""
        if self._current_hotkeys == hotkeys_config:
            return
        self.stop()
        self.start(hotkeys_config)

    def stop(self) -> None:
        """Signals the hotkey listener thread to stop and waits for exit."""
        if sys.platform != "win32" or not self._thread or not self._thread.is_alive():
            return

        self._stop_event.set()
        if self._thread_id:
            try:
                ctypes.windll.user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            except Exception:
                pass
        self._thread.join(timeout=1.0)
        self._thread = None
        self._thread_id = None

    def _worker_loop(self) -> None:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        self._thread_id = kernel32.GetCurrentThreadId()

        # Set 64-bit ctypes function signatures
        class MSG(ctypes.Structure):
            _fields_ = [
                ("hwnd", ctypes.c_void_p),
                ("message", ctypes.c_uint),
                ("wParam", ctypes.c_void_p),
                ("lParam", ctypes.c_void_p),
                ("time", ctypes.c_ulong),
                ("pt_x", ctypes.c_long),
                ("pt_y", ctypes.c_long),
                ("lPrivate", ctypes.c_ulong),
            ]

        user32.RegisterHotKey.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint, ctypes.c_uint]
        user32.RegisterHotKey.restype = ctypes.c_bool
        user32.UnregisterHotKey.argtypes = [ctypes.c_void_p, ctypes.c_int]
        user32.UnregisterHotKey.restype = ctypes.c_bool

        user32.PeekMessageW.argtypes = [ctypes.POINTER(MSG), ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
        user32.PeekMessageW.restype = ctypes.c_bool
        user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
        user32.GetMessageW.restype = ctypes.c_int

        # Crucial: Force Windows to initialize the thread's message queue before registering hotkeys
        init_msg = MSG()
        user32.PeekMessageW(ctypes.byref(init_msg), None, 0, 0, 0)

        # Register configured hotkeys
        # Hotkey IDs
        ID_TOGGLE_CONFIG = 201
        ID_TOGGLE_FALLBACK = 202
        ID_FOCUS = 203
        ID_PET = 204

        registered = {}

        # 1. Configured toggle hotkey (e.g. 'alt+q', 'ctrl+space', or user choice)
        toggle_str = self._current_hotkeys.get("toggle_visibility", "alt+q")
        parsed = parse_hotkey(toggle_str)
        if parsed:
            mods, vk = parsed
            ok = user32.RegisterHotKey(None, ID_TOGGLE_CONFIG, mods, vk)
            if ok:
                registered[ID_TOGGLE_CONFIG] = "toggle"
                logger.info("Registered hotkey '%s' for toggle_visibility.", toggle_str)
            else:
                logger.warning("Failed to register hotkey '%s' (Error: %d).", toggle_str, kernel32.GetLastError())

        # 2. Always register fallback 'ctrl+shift+b' if different from toggle_str
        if toggle_str.lower() != "ctrl+shift+b":
            parsed_fb = parse_hotkey("ctrl+shift+b")
            if parsed_fb:
                mods, vk = parsed_fb
                if user32.RegisterHotKey(None, ID_TOGGLE_FALLBACK, mods, vk):
                    registered[ID_TOGGLE_FALLBACK] = "toggle"

        # 3. Focus mode hotkey
        focus_str = self._current_hotkeys.get("toggle_focus", "ctrl+shift+f")
        parsed_focus = parse_hotkey(focus_str)
        if parsed_focus:
            mods, vk = parsed_focus
            if user32.RegisterHotKey(None, ID_FOCUS, mods, vk):
                registered[ID_FOCUS] = "focus"

        # 4. Pet cheer-up hotkey
        pet_str = self._current_hotkeys.get("pet", "ctrl+shift+p")
        parsed_pet = parse_hotkey(pet_str)
        if parsed_pet:
            mods, vk = parsed_pet
            if user32.RegisterHotKey(None, ID_PET, mods, vk):
                registered[ID_PET] = "pet"

        self._registered_ids = registered

        # Main blocking Win32 message pump
        msg = MSG()
        try:
            while not self._stop_event.is_set():
                res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if res == 0 or res == -1:  # WM_QUIT or error
                    break

                if msg.message == WM_HOTKEY:
                    action = registered.get(msg.wParam)
                    if action == "toggle" and self.on_toggle_visibility:
                        self.on_toggle_visibility()
                    elif action == "focus" and self.on_toggle_focus:
                        self.on_toggle_focus()
                    elif action == "pet" and self.on_pet:
                        self.on_pet()

                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            for hk_id in list(registered.keys()):
                user32.UnregisterHotKey(None, hk_id)
            registered.clear()
            self._registered_ids.clear()
