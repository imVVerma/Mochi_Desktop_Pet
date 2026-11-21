import logging
import threading
from typing import Callable, Optional

logger = logging.getLogger("DesktopPet.Tray")

try:
    from PIL import Image, ImageDraw
    import pystray
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


def create_default_tray_image(color: str = "#FF9AA2") -> "Image.Image":
    """Generates a procedural 64x64 Floppy Bunny icon for the system tray."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Bunny Ears
    draw.polygon([(16, 28), (14, 8), (22, 4), (26, 12), (24, 28)], fill=color, outline="#222228", width=2)
    draw.polygon([(40, 28), (38, 12), (42, 4), (50, 8), (48, 28)], fill=color, outline="#222228", width=2)
    draw.polygon([(16, 22), (16, 10), (20, 6), (22, 12)], fill="#FFD1DC")
    draw.polygon([(42, 22), (42, 12), (44, 6), (48, 10)], fill="#FFD1DC")

    # Chubby body
    draw.ellipse([8, 18, 56, 60], fill=color, outline="#222228", width=3)
    # Belly
    draw.ellipse([18, 34, 46, 56], fill="#FFF9F2")
    # Eyes with glints
    draw.ellipse([20, 28, 26, 35], fill="#18181D")
    draw.ellipse([21, 29, 23, 31], fill="#FFFFFF")
    draw.ellipse([38, 28, 44, 35], fill="#18181D")
    draw.ellipse([39, 29, 41, 31], fill="#FFFFFF")
    # Cute nose and smile
    draw.polygon([(30, 36), (34, 36), (32, 38)], fill="#FF7597")
    draw.arc([27, 36, 32, 42], start=0, end=180, fill="#222228", width=2)
    draw.arc([32, 36, 37, 42], start=0, end=180, fill="#222228", width=2)
    return img


class TrayManager:
    """Manages system tray icon and context menu with pystray, with fallback handling."""

    def __init__(
        self,
        on_toggle_visibility: Callable[[], None],
        on_toggle_focus: Callable[[], None],
        on_toggle_sleep: Callable[[], None],
        on_pet: Callable[[], None],
        on_change_color: Callable[[str], None],
        on_exit: Callable[[], None],
    ):
        self.on_toggle_visibility = on_toggle_visibility
        self.on_toggle_focus = on_toggle_focus
        self.on_toggle_sleep = on_toggle_sleep
        self.on_pet = on_pet
        self.on_change_color = on_change_color
        self.on_exit = on_exit

        self.icon: Optional["pystray.Icon"] = None
        self.tray_thread: Optional[threading.Thread] = None

    def start(self) -> bool:
        if not TRAY_AVAILABLE:
            logger.info("pystray or Pillow not available; system tray disabled (using window context menu fallback).")
            return False

        try:
            image = create_default_tray_image()
            menu = pystray.Menu(
                pystray.MenuItem("Summon / Dismiss", lambda icon, item: self.on_toggle_visibility(), default=True),
                pystray.MenuItem("Pet Mochi (Cheer Up)", lambda icon, item: self.on_pet()),
                pystray.MenuItem("Toggle Focus Mode (Pomodoro)", lambda icon, item: self.on_toggle_focus()),
                pystray.MenuItem("Toggle Sleep / Wake", lambda icon, item: self.on_toggle_sleep()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    "Colors",
                    pystray.Menu(
                        pystray.MenuItem("Rose Pink", lambda icon, item: self.on_change_color("#FFB6C1")),
                        pystray.MenuItem("Mint Sage", lambda icon, item: self.on_change_color("#B5EAD7")),
                        pystray.MenuItem("Sky Blue", lambda icon, item: self.on_change_color("#A0C4FF")),
                        pystray.MenuItem("Lavender", lambda icon, item: self.on_change_color("#D0BDF4")),
                        pystray.MenuItem("Buttercup", lambda icon, item: self.on_change_color("#FFEAA7")),
                    )
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", lambda icon, item: self._handle_exit()),
            )

            self.icon = pystray.Icon("desktop_pet", image, "Desktop Pet (Mochi)", menu)
            self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
            self.tray_thread.start()
            logger.info("System tray initialized successfully.")
            return True
        except Exception as e:
            logger.warning("Failed to start system tray icon: %s", e)
            return False

    def update_icon_color(self, color: str) -> None:
        if self.icon and TRAY_AVAILABLE:
            try:
                self.icon.icon = create_default_tray_image(color)
            except Exception:
                pass

    def _handle_exit(self) -> None:
        self.stop()
        self.on_exit()

    def stop(self) -> None:
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
            self.icon = None
