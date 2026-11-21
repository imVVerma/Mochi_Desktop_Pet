import ctypes
import logging
import math
import sys
import threading
import tkinter as tk
from typing import Optional
from core.config import ConfigManager
from core.fsm import PetFSM, State
from core.physics import PhysicsEngine, get_virtual_screen_bounds, get_primary_taskbar_height
from core.stats import PetStats
from ui.canvas_renderer import CanvasRenderer
from ui.settings_dialog import SettingsDialog
from ui.tray import TrayManager
from ui.window import PetWindow

logger = logging.getLogger("DesktopPet.Engine")


class PetEngine:
    """Central coordinator for Desktop Pet: links FSM, physics, stats, UI, hotkeys, and tray."""

    def __init__(self, config_path: str = "config.json", toggle_event=None):
        self.config_manager = ConfigManager(config_path)
        self.toggle_event = toggle_event

        # Initialize physical properties from config
        scale = float(self.config_manager.get("scale", 1.0))
        self.width = int(140 * scale)
        self.height = int(140 * scale)
        self.walk_speed = float(self.config_manager.get("walk_speed", 3.0))

        # Discover screen geometry and taskbar
        bounds = get_virtual_screen_bounds()
        taskbar_h = get_primary_taskbar_height(bounds.max_y)

        # Core engines
        self.physics = PhysicsEngine(
            width=self.width,
            height=self.height,
            bounds=bounds,
            taskbar_height=taskbar_h,
            home_corner=self.config_manager.get("home_corner", "bottom_right"),
        )

        circadian_cfg = self.config_manager.get("circadian", {})
        self.stats = PetStats(
            bedtime_hour=circadian_cfg.get("bedtime_hour", 23),
            wake_hour=circadian_cfg.get("wake_hour", 7),
            idle_sleep_seconds=circadian_cfg.get("idle_sleep_seconds", 180),
            idle_dock_seconds=circadian_cfg.get("idle_dock_seconds", 15),
        )

        # Wire wellness reminder messages
        wellness_cfg = self.config_manager.get("wellness_reminders", {})
        self.stats.reminders_enabled = wellness_cfg.get("enabled", True)
        self.stats.reminder_interval_seconds = wellness_cfg.get("interval_minutes", 20) * 60
        if "messages" in wellness_cfg:
            self.stats.reminder_messages = wellness_cfg["messages"]

        self.fsm = PetFSM(self.stats, self.physics)
        self.fsm.walk_speed = self.walk_speed

        # Window & Overlay
        self.window = PetWindow(
            width=self.width,
            height=self.height,
            transparent_color=self.config_manager.get("transparent_color", "#000001"),
            hotkeys_config=self.config_manager.get("hotkeys", {}),
            on_press=self.handle_press,
            on_drag=self.handle_drag,
            on_release=self.handle_release,
            on_pet=self.handle_pet,
            on_toggle_focus=self.toggle_focus_mode,
            on_toggle_sleep=self.toggle_sleep,
            on_change_color=self.change_base_color,
            on_open_preferences=lambda: self._dispatch_to_main_thread(self.open_preferences_dialog),
            on_exit=self.exit_app,
        )

        # Canvas Renderer
        self.renderer = CanvasRenderer(self.window.canvas, width=self.width, height=self.height)

        # System Tray Manager with thread-safe UI dispatch
        self.tray = TrayManager(
            on_toggle_visibility=lambda: self._dispatch_to_main_thread(self.window.toggle_visibility),
            on_toggle_focus=lambda: self._dispatch_to_main_thread(self.toggle_focus_mode),
            on_toggle_sleep=lambda: self._dispatch_to_main_thread(self.toggle_sleep),
            on_pet=lambda: self._dispatch_to_main_thread(self.handle_pet),
            on_change_color=lambda c: self._dispatch_to_main_thread(self.change_base_color, c),
            on_open_preferences=lambda: self._dispatch_to_main_thread(self.open_preferences_dialog),
            on_exit=lambda: self._dispatch_to_main_thread(self.exit_app),
        )
        self.tray.start()

        # Engine loop running state
        self.is_running = True
        self.last_pointer_pos = (0, 0)

        # Set initial placement
        self.window.set_position(self.physics.x, self.physics.y)

    def _dispatch_to_main_thread(self, callback, *args) -> None:
        """Safely executes a callback on Tkinter's main event loop."""
        if self.is_running and hasattr(self, "window") and self.window and self.window.root:
            try:
                self.window.root.after(0, callback, *args)
            except Exception as e:
                logger.debug("Failed dispatching callback to main UI thread: %s", e)

    def handle_press(self, cursor_x: float, cursor_y: float) -> None:
        self.stats.record_interaction()
        self.physics.start_drag(cursor_x, cursor_y)
        self.fsm.on_mouse_press()

    def handle_drag(self, cursor_x: float, cursor_y: float, grab_ox: float, grab_oy: float) -> None:
        self.stats.record_interaction()
        self.physics.update_drag(cursor_x, cursor_y, grab_ox, grab_oy)
        self.window.set_position(self.physics.x, self.physics.y)

    def handle_release(self) -> None:
        self.stats.record_interaction()
        vx, vy = self.physics.release_drag()
        self.fsm.on_mouse_release(vx, vy)

    def handle_pet(self) -> None:
        self.stats.record_interaction()
        self.fsm.on_petting()
        self.renderer.spawn_particle("♥", "#FF4081", size=14)
        quotes = ["I love you! ✨", "Hehe, that tickles! 🌸", "Best friends! 💖", "Yay! 🎉"]
        import random
        self.renderer.speech_bubble.show(random.choice(quotes), duration_seconds=3.0)

    def toggle_focus_mode(self) -> None:
        self.stats.record_activity()
        if self.stats.focus_active:
            self.stats.stop_focus()
            self.fsm.transition_to(State.IDLE)
            self.renderer.speech_bubble.show("Focus session paused! 😊", duration_seconds=3.0)
        else:
            focus_cfg = self.config_manager.get("focus_mode", {})
            work_mins = focus_cfg.get("work_duration_minutes", 25)
            break_mins = focus_cfg.get("break_duration_minutes", 5)
            self.stats.start_focus(work_mins=work_mins, break_mins=break_mins)
            self.fsm.transition_to(State.FOCUS)
            self.renderer.speech_bubble.show(f"Focus Mode: {work_mins}m sprint! Let's do this! 🎓", duration_seconds=4.0)

    def toggle_sleep(self) -> None:
        self.stats.record_activity()
        if self.fsm.state == State.SLEEPING:
            self.fsm.transition_to(State.EXCITED)
            self.renderer.spawn_particle("!", "#FFB74D", size=14)
            self.renderer.speech_bubble.show("Good morning! ☀️", duration_seconds=3.0)
        else:
            self.fsm.transition_to(State.SLEEPING)
            self.renderer.spawn_particle("z", "#7E57C2", size=12)
            self.renderer.speech_bubble.show("Sweet dreams... 🌙", duration_seconds=3.0)

    def change_base_color(self, color_hex: str) -> None:
        self.config_manager.set("base_color", color_hex, auto_save=True)
        self.config_manager.set("auto_color", False, auto_save=True)
        self.tray.update_icon_color(color_hex)
        self.renderer.spawn_particle("✦", color_hex, size=14)

    def open_preferences_dialog(self) -> None:
        """Opens the visual Preferences & Wardrobe dialog."""
        if hasattr(self, "window") and self.window and self.window.root:
            SettingsDialog(
                parent=self.window.root,
                config_data=self.config_manager.data,
                on_save=self.apply_preferences,
            )

    def apply_preferences(self, new_config: dict) -> None:
        """Applies newly saved preferences from the GUI dialog."""
        self.config_manager.data = new_config
        self.config_manager.save()

        # Sync dist/config.json if running as standalone or adjacent
        try:
            import json
            import os
            ws = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dist_cfg = os.path.join(ws, "dist", "config.json")
            if os.path.exists(os.path.dirname(dist_cfg)):
                with open(dist_cfg, "w", encoding="utf-8") as f:
                    json.dump(new_config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        # Apply hotkey changes
        hotkeys = new_config.get("hotkeys", {})
        if hasattr(self, "window") and self.window:
            self.window.update_hotkeys(hotkeys)

        # Apply base color
        new_color = new_config.get("base_color", "#FFB6C1")
        if hasattr(self, "tray") and self.tray:
            self.tray.update_icon_color(new_color)

        # Update stats settings
        circ = new_config.get("circadian", {})
        self.stats.bedtime_hour = circ.get("bedtime_hour", 23)
        self.stats.wake_hour = circ.get("wake_hour", 7)
        self.stats.idle_dock_seconds = circ.get("idle_dock_seconds", 15)

        wellness = new_config.get("wellness_reminders", {})
        self.stats.reminders_enabled = wellness.get("enabled", True)
        self.stats.reminder_interval_seconds = wellness.get("interval_minutes", 20) * 60

        if hasattr(self, "renderer") and self.renderer:
            self.renderer.speech_bubble.show("Preferences updated! ✨", duration_seconds=3.0)
            self.renderer.spawn_particle("✨", new_color, size=14)

    def update_loop(self) -> None:
        """Physical animation and motion tick (~20 FPS awake, throttled to 4 FPS when sleeping)."""
        if not self.is_running:
            return

        tick_interval = 50
        try:
            # If window is hidden/dismissed, throttle loop but keep brain active
            if not self.window.is_visible:
                tick_interval = 200
                return

            # Determine tick rate: throttle CPU when sleeping
            is_sleeping = (self.fsm.state == State.SLEEPING)
            tick_interval = 250 if is_sleeping else 50

            # Query mouse cursor position
            mx, my = self.window.get_pointer_position()
            if (mx, my) != self.last_pointer_pos:
                self.stats.record_activity()
                self.last_pointer_pos = (mx, my)

            # Relative vector to mouse for eye tracking & proximity
            center_x = self.physics.x + self.width / 2
            center_y = self.physics.y + self.height / 2
            rel_mx = mx - center_x
            rel_my = my - center_y
            dist = math.hypot(rel_mx, rel_my)

            if dist < 120.0:
                self.stats.record_interaction()

            self.fsm.on_mouse_proximity(dist)

            # Step physics and FSM
            self.physics.tick()
            self.fsm.tick()

            # Update window position
            self.window.set_position(self.physics.x, self.physics.y)

            # Procedural deformations
            offset_y, stretch_x = self.physics.get_visual_deformations()

            # Sleeping particle spawn
            if is_sleeping and self.fsm.state_ticks % 60 == 0:
                self.renderer.spawn_particle("z", "#7E57C2", size=10)

            # Dancing/excited sparkles
            if self.fsm.state == State.DANCING and self.fsm.state_ticks % 25 == 0:
                self.renderer.spawn_particle("♥", "#FF4081", size=12)

            # Velocity magnitude for dizzy expression
            vel_speed = math.hypot(self.physics.vx, self.physics.vy)

            # Procedural canvas rendering
            is_docked = self.physics.is_near_home(threshold=30.0)
            self.renderer.draw(
                state=self.fsm.state,
                stats=self.stats,
                offset_y=offset_y,
                stretch_x=stretch_x,
                mouse_rel_x=rel_mx,
                mouse_rel_y=rel_my,
                velocity_speed=vel_speed,
                auto_color=self.config_manager.get("auto_color", True),
                base_color=self.config_manager.get("base_color", "#FFB6C1"),
                is_docked=is_docked,
            )
        except Exception as e:
            logger.error("Error during update_loop (throttling): %s", e)
            tick_interval = 500
        finally:
            if self.is_running and hasattr(self, "window") and self.window and self.window.root:
                try:
                    self.window.root.after(tick_interval, self.update_loop)
                except Exception:
                    pass

    def wall_clock_loop(self) -> None:
        """Runs once per second: checks hot-reloading, advances Pomodoro & wellness reminders."""
        if not self.is_running:
            return

        try:
            # Check for config changes on disk
            if self.config_manager.check_hot_reload():
                if hasattr(self, "window") and self.window:
                    self.window.update_hotkeys(self.config_manager.get("hotkeys", {}))

            # Step timers
            reminder_or_focus_msg = self.stats.tick_second()
            if reminder_or_focus_msg and self.window.is_visible:
                self.renderer.speech_bubble.show(reminder_or_focus_msg, duration_seconds=6.0)

            self.stats.natural_decay()
        except Exception as e:
            logger.error("Error in wall_clock_loop: %s", e)
        finally:
            if self.is_running and hasattr(self, "window") and self.window and self.window.root:
                try:
                    self.window.root.after(1000, self.wall_clock_loop)
                except Exception:
                    pass

    def start(self) -> None:
        """Starts main event loop and toggle event listener."""
        if self.toggle_event and sys.platform == "win32":
            def toggle_listener():
                kernel32 = ctypes.windll.kernel32
                while self.is_running and self.toggle_event:
                    res = kernel32.WaitForSingleObject(self.toggle_event, 200)
                    if res == 0:  # WAIT_OBJECT_0
                        self._dispatch_to_main_thread(self.window.toggle_visibility)

            self._toggle_thread = threading.Thread(target=toggle_listener, daemon=True)
            self._toggle_thread.start()

        self.update_loop()
        self.wall_clock_loop()
        self.window.root.mainloop()

    def exit_app(self) -> None:
        """Clean shutdown handler."""
        if not self.is_running:
            return
        self.is_running = False
        if hasattr(self, "tray") and self.tray:
            try:
                self.tray.stop()
            except Exception:
                pass
        if hasattr(self, "window") and self.window:
            try:
                self.window.close()
            except Exception:
                pass
