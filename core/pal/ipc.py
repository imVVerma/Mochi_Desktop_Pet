"""
Platform Abstraction Layer (PAL) - Single Instance & IPC Subsystem.
Cross-platform named mutex/event on Windows, and local domain socket IPC on macOS/Linux.
Prevents duplicate instances and signals running instance to toggle open/closed.
"""
import ctypes
import logging
import os
import socket
import sys
import threading
from typing import Callable, Optional

logger = logging.getLogger("DesktopPet.PAL.IPC")


class CrossPlatformInstanceLock:
    """
    Enforces a single running instance of Desktop Pet across Windows, macOS, and Linux,
    and provides IPC signaling to toggle open/closed on repeated execution.
    """

    def __init__(
        self,
        app_id: str = "DesktopPet_SingleInstance_Global",
        on_toggle_callback: Optional[Callable[[], None]] = None,
    ):
        self.app_id = app_id
        self.on_toggle_callback = on_toggle_callback
        self.already_running = False
        self._is_active = True

        # Windows handles
        self.mutex = None
        self.toggle_event = None

        # Unix socket handles
        self._server_sock: Optional[socket.socket] = None
        self._listener_thread: Optional[threading.Thread] = None
        self._sock_path = os.path.join(
            os.environ.get("TMPDIR") or os.environ.get("TEMP") or "/tmp",
            f"{self.app_id}.sock",
        )

        self._acquire_lock()

    def _acquire_lock(self) -> None:
        # 1. Windows Implementation via Named Mutex & Named Event
        if sys.platform == "win32":
            try:
                self.mutex = ctypes.windll.kernel32.CreateMutexW(None, False, self.app_id)
                ERROR_ALREADY_EXISTS = 183
                if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
                    self.already_running = True
                    # Signal existing instance to toggle
                    event_name = f"{self.app_id}_ToggleEvent"
                    h_event = ctypes.windll.kernel32.OpenEventW(0x0002, False, event_name)
                    if h_event:
                        ctypes.windll.kernel32.SetEvent(h_event)
                        ctypes.windll.kernel32.CloseHandle(h_event)
                else:
                    event_name = f"{self.app_id}_ToggleEvent"
                    self.toggle_event = ctypes.windll.kernel32.CreateEventW(None, False, False, event_name)
            except Exception as e:
                logger.debug("Win32 mutex error: %s", e)
                self.already_running = False

        # 2. macOS & Linux Implementation via Local Domain Socket
        else:
            try:
                self._server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                # If old socket file is abandoned, clean it up
                if os.path.exists(self._sock_path):
                    try:
                        # Test if an active instance is actually listening
                        test_client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        test_client.connect(self._sock_path)
                        # An active server responded -> send toggle signal and exit
                        test_client.sendall(b"toggle\n")
                        test_client.close()
                        self.already_running = True
                        return
                    except (socket.error, OSError):
                        # Stale socket file from prior crash -> remove safely
                        try:
                            os.remove(self._sock_path)
                        except OSError:
                            pass

                # Bind new server socket
                self._server_sock.bind(self._sock_path)
                self._server_sock.listen(5)
                self._server_sock.settimeout(0.5)

                # Start background listener thread
                self._listener_thread = threading.Thread(target=self._unix_listener_loop, daemon=True)
                self._listener_thread.start()
            except Exception as e:
                logger.debug("Unix socket bind failed (another instance active): %s", e)
                self.already_running = True

    def _unix_listener_loop(self) -> None:
        while self._is_active and self._server_sock:
            try:
                conn, _ = self._server_sock.accept()
                data = conn.recv(1024)
                if b"toggle" in data and self.on_toggle_callback:
                    self.on_toggle_callback()
                conn.close()
            except socket.timeout:
                continue
            except Exception:
                break

    def release(self) -> None:
        self._is_active = False

        # Windows Cleanup
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

        # Unix Cleanup
        if self._server_sock:
            try:
                self._server_sock.close()
            except Exception:
                pass
            self._server_sock = None

        if os.path.exists(self._sock_path):
            try:
                os.remove(self._sock_path)
            except Exception:
                pass
