"""
Platform Abstraction Layer (PAL) - Display Subsystem.
Cross-platform virtual screen bounds discovery, taskbar/dock detection,
and multi-monitor geometry for Windows, macOS, and Linux.
"""
import ctypes
import logging
import os
import subprocess
import sys
from typing import Optional

logger = logging.getLogger("DesktopPet.PAL.Display")


class DisplayMetrics:
    """Discovers screen geometry, multi-monitor bounds, and taskbar/dock heights across OS platforms."""

    @staticmethod
    def get_screen_bounds(fallback_w: int = 1920, fallback_h: int = 1080):
        """
        Returns (min_x, min_y, max_x, max_y, primary_right, primary_bottom).
        Supports multi-monitor setups with secondary displays placed left or top.
        """
        # 1. Windows Provider
        if sys.platform == "win32":
            try:
                min_x = ctypes.windll.user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
                min_y = ctypes.windll.user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
                width = ctypes.windll.user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
                height = ctypes.windll.user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN

                class RECT(ctypes.Structure):
                    _fields_ = [
                        ("left", ctypes.c_long),
                        ("top", ctypes.c_long),
                        ("right", ctypes.c_long),
                        ("bottom", ctypes.c_long),
                    ]

                rect = RECT()
                primary_right = None
                primary_bottom = None
                # SPI_GETWORKAREA = 48
                if ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0):
                    primary_right = int(rect.right)
                    primary_bottom = int(rect.bottom)

                if width > 0 and height > 0:
                    return min_x, min_y, min_x + width, min_y + height, primary_right, primary_bottom
            except Exception as e:
                logger.debug("Win32 display metric error: %s", e)

        # 2. macOS Provider (Darwin)
        elif sys.platform == "darwin":
            try:
                # Query display dimensions via system_profiler or osascript if PyObjC not installed
                cmd = ["osascript", "-e", 'tell application "Finder" to get bounds of window of desktop']
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=1.0)
                if res.returncode == 0 and res.stdout.strip():
                    parts = [int(p.strip()) for p in res.stdout.strip().split(",")]
                    if len(parts) == 4:
                        # parts = [left, top, right, bottom]
                        return parts[0], parts[1], parts[2], parts[3], parts[2], parts[3]
            except Exception as e:
                logger.debug("macOS display metric error: %s", e)

        # 3. Linux Provider (X11 / Wayland)
        elif sys.platform.startswith("linux"):
            try:
                # Query X11 screen size via xrandr
                res = subprocess.run(["xrandr"], capture_output=True, text=True, timeout=1.0)
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        if "current" in line:
                            # e.g., 'Screen 0: minimum 320 x 200, current 1920 x 1080...'
                            idx = line.find("current")
                            tokens = line[idx:].split()
                            if len(tokens) >= 4:
                                w = int(tokens[1])
                                h = int(tokens[3].rstrip(","))
                                return 0, 0, w, h, w, h
            except Exception as e:
                logger.debug("Linux display metric error: %s", e)

        # Default fallback
        return 0, 0, fallback_w, fallback_h, fallback_w, fallback_h

    @staticmethod
    def get_dock_or_taskbar_height(screen_h: int) -> int:
        """
        Returns estimated taskbar/dock height at the bottom of the primary display.
        Windows: Taskbar height (typically 40-48px).
        macOS: Dock height (typically 60-80px if placed at bottom).
        Linux: GNOME Dash / KDE Panel (typically 36-48px).
        """
        # Windows
        if sys.platform == "win32":
            try:
                class RECT(ctypes.Structure):
                    _fields_ = [
                        ("left", ctypes.c_long),
                        ("top", ctypes.c_long),
                        ("right", ctypes.c_long),
                        ("bottom", ctypes.c_long),
                    ]

                rect = RECT()
                if ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0):
                    work_bottom = int(rect.bottom)
                    if screen_h > work_bottom > 0:
                        # Work-area and screen metrics can use different DPI-scaled
                        # coordinate spaces. Keep taskbar estimates within a plausible range.
                        return max(20, min(screen_h - work_bottom, 120))
            except Exception:
                pass
            return 45

        # macOS: Dock at bottom typically occupies ~65px
        elif sys.platform == "darwin":
            return 65

        # Linux: GNOME / KDE panel typically occupies ~40px
        elif sys.platform.startswith("linux"):
            return 40

        return 45
