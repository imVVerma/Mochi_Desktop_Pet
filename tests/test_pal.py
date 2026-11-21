import sys
import pytest
from core.pal.display import DisplayMetrics
from core.pal.ipc import CrossPlatformInstanceLock
from core.pal.window import apply_dpi_awareness, configure_transparent_window


def test_display_metrics():
    min_x, min_y, max_x, max_y, pr, pb = DisplayMetrics.get_screen_bounds()
    assert max_x > min_x
    assert max_y > min_y
    assert pr is not None
    assert pb is not None

    taskbar_h = DisplayMetrics.get_dock_or_taskbar_height(1080)
    assert 20 <= taskbar_h <= 120


def test_cross_platform_instance_lock():
    lock1 = CrossPlatformInstanceLock(app_id="TestAppLock_PAL_123")
    assert lock1.already_running is False

    lock2 = CrossPlatformInstanceLock(app_id="TestAppLock_PAL_123")
    assert lock2.already_running is True

    lock1.release()
    lock2.release()


def test_window_pal_helpers():
    # Verify DPI and window configuration functions execute safely
    apply_dpi_awareness()
