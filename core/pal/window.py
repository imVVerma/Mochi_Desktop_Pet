"""
Platform Abstraction Layer (PAL) - Windowing & Transparency Subsystem.
Configures frameless topmost windowing, high-DPI scaling, and transparency across platforms.
"""
import ctypes
import logging
import sys
import tkinter as tk

logger = logging.getLogger("DesktopPet.PAL.Window")


def apply_dpi_awareness() -> None:
    """Enables high-DPI awareness on Windows to prevent coordinate scaling mismatch."""
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass


def configure_transparent_window(root: tk.Tk, transparent_color: str = "#000001") -> None:
    """
    Applies frameless topmost transparent styling across OS platforms.
    Windows: Uses hardware color-keying via -transparentcolor.
    macOS / Linux: Uses alpha composite transparency or systemTransparent fallback.
    """
    apply_dpi_awareness()

    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.config(bg=transparent_color)

    if sys.platform == "win32":
        try:
            root.wm_attributes("-transparentcolor", transparent_color)
        except Exception as e:
            logger.debug("Win32 transparentcolor notice: %s", e)

    elif sys.platform == "darwin":
        # macOS Cocoa
        try:
            root.wm_attributes("-alpha", 0.99)
            root.configure(bg="systemTransparent")
        except Exception:
            pass

    elif sys.platform.startswith("linux"):
        # Linux X11 / Wayland
        try:
            root.wm_attributes("-type", "splash")
        except Exception:
            pass
