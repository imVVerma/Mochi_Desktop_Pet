import sys
from unittest.mock import MagicMock
import pytest


class MockCanvas:
    """Headless mock for tkinter.Canvas."""

    def __init__(self, master=None, *args, **kwargs):
        self.master = master
        self._items = {}
        self._item_counter = 0

    def pack(self, *args, **kwargs):
        pass

    def bind(self, *args, **kwargs):
        pass

    def create_oval(self, *args, **kwargs):
        self._item_counter += 1
        return self._item_counter

    def create_line(self, *args, **kwargs):
        self._item_counter += 1
        return self._item_counter

    def create_arc(self, *args, **kwargs):
        self._item_counter += 1
        return self._item_counter

    def create_polygon(self, *args, **kwargs):
        self._item_counter += 1
        return self._item_counter

    def create_text(self, *args, **kwargs):
        self._item_counter += 1
        return self._item_counter

    def delete(self, *args, **kwargs):
        pass


class MockTk:
    """Headless mock for tkinter.Tk."""

    def __init__(self, *args, **kwargs):
        self._scheduled_callbacks = []
        self.report_callback_exception = None

    def overrideredirect(self, *args, **kwargs):
        pass

    def attributes(self, *args, **kwargs):
        pass

    def wm_attributes(self, *args, **kwargs):
        pass

    def config(self, *args, **kwargs):
        pass

    def geometry(self, *args, **kwargs):
        pass

    def withdraw(self):
        pass

    def deiconify(self):
        pass

    def destroy(self):
        pass

    def mainloop(self):
        pass

    def after(self, delay, callback=None, *args):
        if callback:
            self._scheduled_callbacks.append((delay, callback, args))
        return len(self._scheduled_callbacks)

    def winfo_screenwidth(self):
        return 1920

    def winfo_screenheight(self):
        return 1080

    def winfo_pointerx(self):
        return 500

    def winfo_pointery(self):
        return 500


class MockMenu:
    """Headless mock for tkinter.Menu."""
    def __init__(self, master=None, *args, **kwargs):
        self.master = master

    def add_command(self, *args, **kwargs):
        pass

    def add_separator(self, *args, **kwargs):
        pass

    def add_cascade(self, *args, **kwargs):
        pass

    def tk_popup(self, *args, **kwargs):
        pass

    def grab_release(self, *args, **kwargs):
        pass


@pytest.fixture
def mock_tkinter(monkeypatch):
    """Provides a headless mocked Tkinter environment for automated evals."""
    import tkinter as tk
    monkeypatch.setattr(tk, "Tk", MockTk)
    monkeypatch.setattr(tk, "Canvas", MockCanvas)
    monkeypatch.setattr(tk, "Menu", MockMenu)
    return MockTk, MockCanvas, MockMenu
