#!/usr/bin/env python3
"""
Desktop Pet: An autonomous, charming, and productive desktop companion.
Zero-install, pure Python & Tkinter with vector procedural graphics.
"""
import argparse
import ctypes
import logging
import os
import sys

# Ensure desktop_pet root is on PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# PyInstaller --noconsole safety: redirect None streams to devnull to avoid write errors
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")


class SingleInstanceLock:
    """Ensures only one instance of Desktop Pet runs at a time using a named Windows Mutex,
    and signals the running instance to toggle visibility (open/close) when triggered again."""

    def __init__(
        self,
        name: str = "DesktopPet_SingleInstance_Mutex_Global",
        event_name: str = "DesktopPet_ToggleEvent_Global",
    ):
        self.name = name
        self.event_name = event_name
        self.mutex = None
        self.toggle_event = None
        self.already_running = False

        if sys.platform == "win32":
            try:
                self.mutex = ctypes.windll.kernel32.CreateMutexW(None, False, self.name)
                # ERROR_ALREADY_EXISTS = 183
                if ctypes.windll.kernel32.GetLastError() == 183:
                    self.already_running = True
                    # Signal existing instance to toggle open/close
                    EVENT_MODIFY_STATE = 0x0002
                    h_event = ctypes.windll.kernel32.OpenEventW(EVENT_MODIFY_STATE, False, self.event_name)
                    if h_event:
                        ctypes.windll.kernel32.SetEvent(h_event)
                        ctypes.windll.kernel32.CloseHandle(h_event)
                else:
                    self.toggle_event = ctypes.windll.kernel32.CreateEventW(None, False, False, self.event_name)
            except Exception:
                self.already_running = False

    def release(self):
        if self.toggle_event and sys.platform == "win32":
            try:
                ctypes.windll.kernel32.CloseHandle(self.toggle_event)
            except Exception:
                pass
            self.toggle_event = None
        if self.mutex and sys.platform == "win32":
            try:
                ctypes.windll.kernel32.CloseHandle(self.mutex)
            except Exception:
                pass
            self.mutex = None


def setup_logging():
    # Setup file logging in user's AppData/Temp as well as console
    log_dir = os.environ.get("APPDATA") or os.environ.get("TEMP") or "."
    log_file = os.path.join(log_dir, "DesktopPet", "desktop_pet.log")
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers = [
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8", mode="a")
        ]
    except Exception:
        handlers = [logging.StreamHandler(sys.stdout)]

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers
    )

    # Global unhandled exception hook to log fatal errors without crash popup loops
    def handle_fatal_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.getLogger("DesktopPet").critical(
            "Unhandled fatal exception: %s: %s", exc_type.__name__, exc_value,
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_fatal_exception


def main():
    setup_logging()
    logger = logging.getLogger("DesktopPet")

    # Check single-instance lock to prevent infinite execution / error loops
    lock = SingleInstanceLock()
    if lock.already_running:
        logger.info("Another instance of Desktop Pet is already running. Signaled existing instance to toggle open/close. Exiting cleanly.")
        sys.exit(0)

    from core.physics import enable_high_dpi_awareness
    enable_high_dpi_awareness()

    from core.engine import PetEngine

    parser = argparse.ArgumentParser(description="Desktop Pet - Virtual Desk Companion")
    parser.add_argument("--config", default="config.json", help="Path to config.json")
    args = parser.parse_args()

    logger.info("Initializing Desktop Pet...")

    try:
        engine = PetEngine(config_path=args.config, toggle_event=lock.toggle_event)
        logger.info("Desktop Pet running. Press Ctrl+C, Ctrl+Shift+B, or right-click to exit.")
        engine.start()
    except KeyboardInterrupt:
        logger.info("Shutdown requested via KeyboardInterrupt.")
    except Exception as e:
        logger.exception("Fatal engine error: %s", e)
    finally:
        lock.release()


if __name__ == "__main__":
    main()
