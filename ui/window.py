import ctypes
import logging
import sys
import threading
import tkinter as tk
from typing import Callable, Optional, Tuple
from core.physics import Bounds, get_virtual_screen_bounds, get_primary_taskbar_height

logger = logging.getLogger("DesktopPet.Window")

# Windows API Constants for DPI and Multi-Monitor Metrics
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
VK_TAB = 0x09
VK_B = 0x42
VK_F = 0x46
VK_P = 0x50
WM_HOTKEY = 0x0312


def enable_high_dpi_awareness() -> None:
    """Enables Windows Per-Monitor DPI awareness to eliminate scaling blurriness and coordinate mismatch."""
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware v2
        except Exception:
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per-monitor DPI aware v1
            except Exception:
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass


class PetWindow:
    """Transparent, frameless, topmost overlay window with non-admin hotkeys and multi-monitor support."""

    def __init__(
        self,
        width: int = 140,
        height: int = 140,
        transparent_color: str = "#000001",
        on_press: Optional[Callable[[float, float], None]] = None,
        on_drag: Optional[Callable[[float, float, float, float], None]] = None,
        on_release: Optional[Callable[[], None]] = None,
        on_pet: Optional[Callable[[], None]] = None,
        on_toggle_focus: Optional[Callable[[], None]] = None,
        on_toggle_sleep: Optional[Callable[[], None]] = None,
        on_change_color: Optional[Callable[[str], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
    ):
        enable_high_dpi_awareness()

        self.width = width
        self.height = height
        self.transparent_color = transparent_color

        self.on_press = on_press
        self.on_drag = on_drag
        self.on_release = on_release
        self.on_pet = on_pet
        self.on_toggle_focus = on_toggle_focus
        self.on_toggle_sleep = on_toggle_sleep
        self.on_change_color = on_change_color
        self.on_exit = on_exit

        self.is_visible: bool = True
        self.grab_offset_x: float = width / 2
        self.grab_offset_y: float = height / 2

        # Create Tkinter Window
        self.root = tk.Tk()

        # Suppress automatic Tkinter error popup dialogs on unhandled callback exceptions
        def _suppress_tk_exception(exc, val, tb):
            logger.error("Suppressed unhandled Tkinter callback error: %s: %s", exc, val)

        self.root.report_callback_exception = _suppress_tk_exception

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg=self.transparent_color)

        if sys.platform == "win32":
            self.root.wm_attributes("-transparentcolor", self.transparent_color)

        # Vector Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=self.transparent_color,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Context Menu
        self._build_context_menu()

        # Bindings
        self.canvas.bind("<Button-1>", self._handle_mouse_press)
        self.canvas.bind("<B1-Motion>", self._handle_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._handle_mouse_release)
        self.canvas.bind("<Button-3>", self._show_context_menu)
        self.canvas.bind("<Double-Button-1>", self._handle_double_click)

        # Non-admin Global Hotkeys setup
        self._stop_hotkeys = threading.Event()
        self._hotkey_thread: Optional[threading.Thread] = None
        self._setup_global_hotkeys()

    def _build_context_menu(self) -> None:
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Pet Mochi (Cheer Up) ✨", command=lambda: self.on_pet and self.on_pet())
        self.menu.add_command(label="Toggle Focus Mode (Pomodoro) 🎓", command=lambda: self.on_toggle_focus and self.on_toggle_focus())
        self.menu.add_command(label="Toggle Sleep / Wake 💤", command=lambda: self.on_toggle_sleep and self.on_toggle_sleep())
        self.menu.add_separator()

        color_menu = tk.Menu(self.menu, tearoff=0)
        colors = [
            ("Blossom Pink", "#FFB6C1"),
            ("Mint Sage", "#B5EAD7"),
            ("Sky Blue", "#A0C4FF"),
            ("Lavender", "#D0BDF4"),
            ("Buttercup Yellow", "#FFEAA7"),
        ]
        for name, code in colors:
            color_menu.add_command(label=name, command=lambda c=code: self.on_change_color and self.on_change_color(c))
        self.menu.add_cascade(label="Change Skin Color 🎨", menu=color_menu)

        self.menu.add_separator()
        self.menu.add_command(label="Dismiss / Hide (Ctrl+Shift+B)", command=self.toggle_visibility)
        self.menu.add_command(label="Exit Desktop Pet", command=self.close)

    def _show_context_menu(self, event) -> None:
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _handle_mouse_press(self, event) -> None:
        self.grab_offset_x = float(event.x)
        self.grab_offset_y = float(event.y)
        if self.on_press:
            self.on_press(float(event.x_root), float(event.y_root))

    def _handle_mouse_drag(self, event) -> None:
        if self.on_drag:
            self.on_drag(float(event.x_root), float(event.y_root), self.grab_offset_x, self.grab_offset_y)

    def _handle_mouse_release(self, event) -> None:
        if self.on_release:
            self.on_release()

    def _handle_double_click(self, event) -> None:
        if self.on_pet:
            self.on_pet()

    def set_position(self, x: float, y: float) -> None:
        """Positions overlay window."""
        self.root.geometry(f"{self.width}x{self.height}+{int(x)}+{int(y)}")

    def toggle_visibility(self) -> None:
        if self.is_visible:
            self.root.withdraw()
            self.is_visible = False
            logger.info("Pet dismissed to tray / background.")
        else:
            self.root.deiconify()
            self.root.attributes("-topmost", True)
            self.is_visible = True
            logger.info("Pet summoned back to desktop.")

    def _setup_global_hotkeys(self) -> None:
        """Sets up non-admin global hotkeys via Windows RegisterHotKey."""
        if sys.platform != "win32":
            return

        def hotkey_worker():
            user32 = ctypes.windll.user32
            # Hotkey IDs
            ID_TOGGLE = 101
            ID_FOCUS = 102
            ID_PET = 103
            ID_TOGGLE_SHIFT_TAB = 104

            # RegisterHotKey does NOT require Administrator rights!
            r1 = user32.RegisterHotKey(None, ID_TOGGLE, MOD_CONTROL | MOD_SHIFT, VK_B)
            r2 = user32.RegisterHotKey(None, ID_FOCUS, MOD_CONTROL | MOD_SHIFT, VK_F)
            r3 = user32.RegisterHotKey(None, ID_PET, MOD_CONTROL | MOD_SHIFT, VK_P)
            r4 = user32.RegisterHotKey(None, ID_TOGGLE_SHIFT_TAB, MOD_SHIFT, VK_TAB)

            if not (r1 or r2 or r3 or r4):
                logger.debug("Win32 RegisterHotKey returned False for one or more keys.")

            class MSG(ctypes.Structure):
                _fields_ = [
                    ("hwnd", ctypes.c_void_p),
                    ("message", ctypes.c_uint),
                    ("wParam", ctypes.c_void_p),
                    ("lParam", ctypes.c_void_p),
                    ("time", ctypes.c_ulong),
                    ("pt_x", ctypes.c_long),
                    ("pt_y", ctypes.c_long),
                ]

            msg = MSG()
            while not self._stop_hotkeys.is_set():
                # PeekMessage with PM_REMOVE allows non-blocking loop check
                if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                    if msg.message == WM_HOTKEY:
                        hk_id = msg.wParam
                        if hk_id in (ID_TOGGLE, ID_TOGGLE_SHIFT_TAB):
                            self.root.after(0, self.toggle_visibility)
                        elif hk_id == ID_FOCUS and self.on_toggle_focus:
                            self.root.after(0, self.on_toggle_focus)
                        elif hk_id == ID_PET and self.on_pet:
                            self.root.after(0, self.on_pet)
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
                else:
                    self._stop_hotkeys.wait(0.05)

            user32.UnregisterHotKey(None, ID_TOGGLE)
            user32.UnregisterHotKey(None, ID_FOCUS)
            user32.UnregisterHotKey(None, ID_PET)
            user32.UnregisterHotKey(None, ID_TOGGLE_SHIFT_TAB)

        self._hotkey_thread = threading.Thread(target=hotkey_worker, daemon=True)
        self._hotkey_thread.start()

    def get_pointer_position(self) -> Tuple[int, int]:
        try:
            return self.root.winfo_pointerx(), self.root.winfo_pointery()
        except Exception:
            return 0, 0

    def close(self) -> None:
        self._stop_hotkeys.set()
        # Prevent re-entrant recursion
        callback = self.on_exit
        self.on_exit = None
        if callback:
            callback()
        try:
            self.root.destroy()
        except Exception:
            pass
