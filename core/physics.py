import logging
import math
import sys
from typing import Tuple, Optional, List
from core.pal.display import DisplayMetrics

logger = logging.getLogger("DesktopPet.Physics")

# Windows API Constants for Virtual Screen & Taskbar Metrics
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
SPI_GETWORKAREA = 48


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


class Bounds:
    """Represents a virtual screen or monitor bounding rectangle."""

    def __init__(
        self,
        min_x: int = 0,
        min_y: int = 0,
        max_x: int = 1920,
        max_y: int = 1080,
        primary_right: Optional[int] = None,
        primary_bottom: Optional[int] = None,
    ):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.primary_right = primary_right if primary_right is not None else max_x
        self.primary_bottom = primary_bottom if primary_bottom is not None else max_y

    @property
    def width(self) -> int:
        return self.max_x - self.min_x

    @property
    def height(self) -> int:
        return self.max_y - self.min_y

    def contains(self, x: float, y: float) -> bool:
        return self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y


def get_virtual_screen_bounds() -> Bounds:
    """Discovers the complete virtual screen bounding rectangle across all monitors (supports negative coords)."""
    min_x, min_y, max_x, max_y, pr, pb = DisplayMetrics.get_screen_bounds()
    return Bounds(min_x, min_y, max_x, max_y, pr, pb)


def get_primary_taskbar_height(screen_h: int) -> int:
    """Estimates the taskbar or dock height on the primary display."""
    return DisplayMetrics.get_dock_or_taskbar_height(screen_h)


class PhysicsEngine:
    """Kinematics, gravity, collision, taskbar perching, squash-and-stretch, and multi-monitor physics."""

    def __init__(
        self,
        width: int = 140,
        height: int = 140,
        bounds: Optional[Bounds] = None,
        taskbar_height: int = 45,
        gravity: float = 0.85,
        air_resistance: float = 0.98,
        ground_friction: float = 0.85,
        bounce_damping: float = 0.40,
        home_corner: str = "bottom_right",
        corner_offset_x: int = 24,
    ):
        self.width = width
        self.height = height
        self.bounds = bounds or Bounds(0, 0, 1920, 1080)
        self.taskbar_height = taskbar_height
        self.gravity = gravity
        self.air_resistance = air_resistance
        self.ground_friction = ground_friction
        self.bounce_damping = bounce_damping
        self.home_corner = home_corner
        self.corner_offset_x = corner_offset_x

        # Position and motion - start directly docked at home corner
        self.x: float = float(self.home_x if home_corner != "none" else self.bounds.max_x - 220)
        self.y: float = float(self.ground_y)
        self.vx: float = 0.0
        self.vy: float = 0.0

        # State flags
        self.is_grounded: bool = True
        self.is_held: bool = False

        # Squash and stretch kinematics
        self.squash_x: float = 0.0
        self.squash_decay: float = 0.72

        # Drag tracking buffer for throw physics
        self.drag_history: List[Tuple[float, float]] = []

    @property
    def ground_y(self) -> float:
        """Effective ground level atop taskbar."""
        if hasattr(self.bounds, "primary_bottom") and self.bounds.primary_bottom < self.bounds.max_y:
            return float(self.bounds.primary_bottom - self.height + 12)
        return float(self.bounds.max_y - self.taskbar_height - self.height + 12)

    @property
    def home_x(self) -> float:
        """Calculates anchor coordinate for the home corner."""
        if self.home_corner == "bottom_right":
            target_right = getattr(self.bounds, "primary_right", self.bounds.max_x)
            # Snug alignment in absolute bottom-right corner above system clock
            return float(target_right - self.width + self.corner_offset_x)
        elif self.home_corner == "bottom_left":
            return float(self.bounds.min_x - self.corner_offset_x)
        return self.x

    def is_near_home(self, threshold: float = 25.0) -> bool:
        """Returns True if the pet is resting in or near its home corner."""
        if self.home_corner == "none":
            return False
        return abs(self.x - self.home_x) <= threshold and self.is_grounded

    def step_towards_home(self, speed: float = 2.5) -> int:
        """Steps horizontally towards home corner with arched hopping animation. Returns direction (1=right, -1=left, 0=arrived)."""
        if self.home_corner == "none" or self.is_held:
            return 0
        diff = self.home_x - self.x
        if abs(diff) <= speed:
            self.x = self.home_x
            self.squash_x = 0.0
            return 0
        direction = 1 if diff > 0 else -1
        self.x += direction * speed
        # Add arched hop squash/stretch rhythm during homing
        self.hop_phase = (getattr(self, "hop_phase", 0.0) + 0.42) % (2 * math.pi)
        hop_arc = math.sin(self.hop_phase)
        if hop_arc > 0:
            self.squash_x = -hop_arc * 2.8  # stretch vertically while leaping
        else:
            self.squash_x = -hop_arc * 2.0  # squash slightly on landing
        self.clamp_position()
        return direction

    def set_bounds(self, bounds: Bounds, taskbar_height: Optional[int] = None) -> None:
        self.bounds = bounds
        if taskbar_height is not None:
            self.taskbar_height = taskbar_height
        self.clamp_position()

    def clamp_position(self) -> None:
        """Clamps the pet inside screen bounds, accounting for multi-monitor / negative coordinates."""
        min_allowed_x = float(self.bounds.min_x)
        # Allow the transparent padding to reach the absolute corner
        max_allowed_x = float(self.bounds.max_x - self.width + self.corner_offset_x)
        min_allowed_y = float(self.bounds.min_y)
        max_allowed_y = float(self.ground_y)

        if max_allowed_x < min_allowed_x:
            max_allowed_x = min_allowed_x
        if max_allowed_y < min_allowed_y:
            max_allowed_y = min_allowed_y

        self.x = max(min_allowed_x, min(self.x, max_allowed_x))
        self.y = max(min_allowed_y, min(self.y, max_allowed_y))

        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.is_grounded = True
        else:
            self.is_grounded = False

    def start_drag(self, cursor_x: float, cursor_y: float) -> None:
        self.is_held = True
        self.is_grounded = False
        self.vx = 0.0
        self.vy = 0.0
        self.drag_history = [(cursor_x, cursor_y)]

    def update_drag(self, cursor_x: float, cursor_y: float, grab_offset_x: float = 70, grab_offset_y: float = 70) -> None:
        """Follow cursor during drag and record trajectory history."""
        self.x = cursor_x - grab_offset_x
        self.y = cursor_y - grab_offset_y
        self.clamp_position()

        self.drag_history.append((cursor_x, cursor_y))
        if len(self.drag_history) > 5:
            self.drag_history.pop(0)

    def release_drag(self) -> Tuple[float, float]:
        """Calculates release velocity vector for realistic toss/throw physics."""
        self.is_held = False
        if len(self.drag_history) >= 2:
            dx = self.drag_history[-1][0] - self.drag_history[0][0]
            dy = self.drag_history[-1][1] - self.drag_history[0][1]
            dt = max(1, len(self.drag_history) - 1)
            # Clamp fling velocity to sane boundaries
            self.vx = max(-30.0, min(dx / dt * 0.9, 30.0))
            self.vy = max(-30.0, min(dy / dt * 0.9, 30.0))
        else:
            self.vx = 0.0
            self.vy = 0.0

        self.drag_history.clear()
        self.is_grounded = (self.y >= self.ground_y)
        return self.vx, self.vy

    def apply_impulse(self, impulse_x: float, impulse_y: float) -> None:
        """Applies an immediate velocity boost (e.g., jump)."""
        self.vx += impulse_x
        self.vy += impulse_y
        if impulse_y < 0:
            self.is_grounded = False

    def tick(self) -> None:
        """Advances physics simulation by one frame (~50ms tick)."""
        if self.is_held:
            # Held by user, physics paused
            return

        # Decay squash from previous impact
        self.squash_x *= self.squash_decay
        if abs(self.squash_x) < 0.1:
            self.squash_x = 0.0

        # Apply gravity if airborne
        if not self.is_grounded:
            self.vy += self.gravity
            self.vx *= self.air_resistance
            self.vy *= self.air_resistance
        else:
            self.vx *= self.ground_friction
            if abs(self.vx) < 0.05:
                self.vx = 0.0

        # Move
        self.x += self.vx
        self.y += self.vy

        # Horizontal screen wall collision & bounce
        min_allowed_x = float(self.bounds.min_x)
        max_allowed_x = float(self.bounds.max_x - self.width)
        if self.x <= min_allowed_x:
            self.x = min_allowed_x
            self.vx = -self.vx * self.bounce_damping
        elif self.x >= max_allowed_x:
            self.x = max_allowed_x
            self.vx = -self.vx * self.bounce_damping

        # Ceiling collision
        min_allowed_y = float(self.bounds.min_y)
        if self.y < min_allowed_y:
            self.y = min_allowed_y
            self.vy = 0.0

        # Ground / Taskbar perching collision
        if self.y >= self.ground_y:
            impact_speed = self.vy
            self.y = self.ground_y

            if impact_speed > 3.0:
                # Trigger procedural squash & stretch
                self.squash_x = min(22.0, impact_speed * 1.6)
                # Bounce
                self.vy = -impact_speed * self.bounce_damping
                if abs(self.vy) < 1.2:
                    self.vy = 0.0
                    self.is_grounded = True
                else:
                    self.is_grounded = False
            else:
                self.vy = 0.0
                self.is_grounded = True
        else:
            self.is_grounded = False

    def get_visual_deformations(self) -> Tuple[float, float]:
        """
        Returns (offset_y, stretch_x) for procedural canvas drawing.
        Squash expands horizontally (stretch_x > 0) and compresses vertically.
        Airborne stretch compresses horizontally (stretch_x < 0) and elongates vertically.
        """
        if self.is_held:
            # Slight dangling stretch when held
            return (0.0, -3.0)

        if not self.is_grounded:
            # Dynamic airborne velocity deformation
            air_stretch = max(-12.0, min(14.0, -self.vy * 0.7))
            return (-air_stretch * 0.4, air_stretch)

        # Grounded squash decay
        if self.squash_x > 0:
            return (self.squash_x * 0.3, self.squash_x)

        return (0.0, 0.0)
