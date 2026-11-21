import logging
import sys
import threading
import tkinter as tk
from typing import Callable, Dict, Optional, Tuple
from core.hotkeys import GlobalHotkeyManager
from core.pal.window import apply_dpi_awareness, configure_transparent_window
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
        hotkeys_config: Optional[Dict[str, str]] = None,
        on_press: Optional[Callable[[float, float], None]] = None,
        on_drag: Optional[Callable[[float, float, float, float], None]] = None,
        on_release: Optional[Callable[[], None]] = None,
        on_pet: Optional[Callable[[], None]] = None,
        on_toggle_focus: Optional[Callable[[], None]] = None,
        on_toggle_sleep: Optional[Callable[[], None]] = None,
        on_change_color: Optional[Callable[[str], None]] = None,
        on_change_accessory: Optional[Callable[[str], None]] = None,
        on_open_preferences: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
    ):
        enable_high_dpi_awareness()

        self.width = width
        self.height = height
        self.transparent_color = transparent_color
        self.hotkeys_config = hotkeys_config or {}

        self.on_press = on_press
        self.on_drag = on_drag
        self.on_release = on_release
        self.on_pet = on_pet
        self.on_toggle_focus = on_toggle_focus
        self.on_toggle_sleep = on_toggle_sleep
        self.on_change_color = on_change_color
        self.on_change_accessory = on_change_accessory
        self.on_open_preferences = on_open_preferences
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

        configure_transparent_window(self.root, self.transparent_color)

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

        # Global Hotkeys Manager setup
        self.hotkey_manager = GlobalHotkeyManager(
            on_toggle_visibility=lambda: self.root.after(0, self.toggle_visibility),
            on_toggle_focus=lambda: self.on_toggle_focus and self.root.after(0, self.on_toggle_focus),
            on_pet=lambda: self.on_pet and self.root.after(0, self.on_pet),
        )
        self.hotkey_manager.start(self.hotkeys_config)

    def _build_context_menu(self) -> None:
        self.menu = tk.Menu(self.root, tearoff=0, bg="#FFFFFF", fg="#2C3E50", activebackground="#FFD1DC", activeforeground="#18181D")
        
        # Header title
        self.menu.add_command(label="🐾 Mochi — Desk Companion", state=tk.DISABLED, font=("Segoe UI", 9, "bold"))
        self.menu.add_separator()

        # Quick interactions
        self.menu.add_command(label="✨ Cheer Up / Pet", command=lambda: self.on_pet and self.on_pet())
        self.menu.add_command(label="🎓 Focus Sprint (Pomodoro)", command=lambda: self.on_toggle_focus and self.on_toggle_focus())
        self.menu.add_command(label="💤 Sleep / Wake", command=lambda: self.on_toggle_sleep and self.on_toggle_sleep())
        self.menu.add_separator()

        # Wardrobe Submenu
        color_menu = tk.Menu(self.menu, tearoff=0, bg="#FFFFFF", fg="#2C3E50", activebackground="#FFD1DC", activeforeground="#18181D")
        colors = [
            ("🌸 Blossom Pink", "#FFB6C1"),
            ("🌿 Mint Sage", "#B5EAD7"),
            ("☁️ Sky Blue", "#A0C4FF"),
            ("🔮 Lavender", "#D0BDF4"),
            ("🌼 Buttercup", "#FFEAA7"),
            ("🍑 Peach Sorbet", "#FFDAC1"),
            ("🤍 Cotton White", "#FFFFFF"),
        ]
        for name, code in colors:
            color_menu.add_command(label=name, command=lambda c=code: self.on_change_color and self.on_change_color(c))
        self.menu.add_cascade(label="🎨 Quick Wardrobe Colors", menu=color_menu)

        # Outfits & Accessories Submenu
        outfit_menu = tk.Menu(self.menu, tearoff=0, bg="#FFFFFF", fg="#2C3E50", activebackground="#FFD1DC", activeforeground="#18181D")
        outfits = [
            ("🎀 Silk Ribbon Bow", "🎀 Silk Ribbon"),
            ("👑 Royal Golden Crown", "👑 Royal Crown"),
            ("🌸 Sakura Flower Pin", "🌸 Sakura Flower"),
            ("👓 Smart Glasses", "👓 Smart Glasses"),
            ("🎩 Gentleman Top Hat", "🎩 Gentleman Top Hat"),
            ("🧣 Cozy Knit Scarf", "🧣 Cozy Scarf"),
            ("🐾 Natural Bunny (None)", "None"),
        ]
        for name, acc_code in outfits:
            outfit_menu.add_command(label=name, command=lambda a=acc_code: self.on_change_accessory and self.on_change_accessory(a))
        self.menu.add_cascade(label="👗 Outfits & Accessories", menu=outfit_menu)

        self.menu.add_command(label="⚙️ Preferences & Wardrobe...", font=("Segoe UI", 9, "bold"), command=lambda: self.on_open_preferences and self.on_open_preferences())

        self.menu.add_separator()
        toggle_hk = self.hotkeys_config.get("toggle_visibility", "Alt+Q").upper()
        self.menu.add_command(label=f"👁️ Dismiss / Summon ({toggle_hk})", command=self.toggle_visibility)
        self.menu.add_command(label="🚪 Quit Mochi", command=self.close)

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

    def update_hotkeys(self, new_hotkeys_config: Dict[str, str]) -> None:
        """Dynamically re-registers global hotkeys and updates context menu label."""
        self.hotkeys_config = new_hotkeys_config or {}
        if hasattr(self, "hotkey_manager") and self.hotkey_manager:
            self.hotkey_manager.update_hotkeys(self.hotkeys_config)

    def get_pointer_position(self) -> Tuple[int, int]:
        try:
            return self.root.winfo_pointerx(), self.root.winfo_pointery()
        except Exception:
            return 0, 0

    def close(self) -> None:
        if hasattr(self, "hotkey_manager") and self.hotkey_manager:
            self.hotkey_manager.stop()
        # Prevent re-entrant recursion
        callback = self.on_exit
        self.on_exit = None
        if callback:
            callback()
        try:
            self.root.destroy()
        except Exception:
            pass
