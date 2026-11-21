"""
Platform Abstraction Layer (PAL) for Desktop Pet.
Encapsulates platform-specific APIs (Windows, macOS, Linux) for display geometry,
taskbar/dock metrics, single-instance IPC, and transparent window overlays.
"""
from core.pal.display import DisplayMetrics
from core.pal.ipc import CrossPlatformInstanceLock
from core.pal.window import apply_dpi_awareness, configure_transparent_window

__all__ = [
    "DisplayMetrics",
    "CrossPlatformInstanceLock",
    "apply_dpi_awareness",
    "configure_transparent_window",
]
