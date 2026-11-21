import datetime
import random
import time
from typing import Callable, List, Optional


class PetStats:
    """Tracks living attributes: Energy, Happiness, Curiosity, Focus Mode, and Wellness timers."""

    def __init__(
        self,
        energy: float = 100.0,
        happiness: float = 85.0,
        curiosity: float = 50.0,
        bedtime_hour: int = 23,
        wake_hour: int = 7,
        idle_sleep_seconds: int = 180,
    ):
        self.energy: float = max(0.0, min(100.0, energy))
        self.happiness: float = max(0.0, min(100.0, happiness))
        self.curiosity: float = max(0.0, min(100.0, curiosity))

        self.bedtime_hour = bedtime_hour
        self.wake_hour = wake_hour
        self.idle_sleep_seconds = idle_sleep_seconds

        # User activity tracking
        self.last_user_activity: float = time.time()

        # Pomodoro / Focus Mode
        self.focus_active: bool = False
        self.focus_phase: str = "WORK"  # "WORK" or "BREAK"
        self.focus_seconds_remaining: int = 25 * 60
        self.work_duration_seconds: int = 25 * 60
        self.break_duration_seconds: int = 5 * 60
        self.on_focus_phase_change: Optional[Callable[[str], None]] = None

        # Wellness Reminders
        self.reminders_enabled: bool = True
        self.reminder_interval_seconds: int = 20 * 60
        self.last_reminder_time: float = time.time()
        self.reminder_messages: List[str] = [
            "Time to drink some water! 💧",
            "Look 20 feet away for 20 seconds! 👁️",
            "Roll your shoulders and stretch! 🧘",
            "Take a slow deep breath in... and out. 🌸",
            "Posture check! Sit up comfortably. 🪑"
        ]
        self.on_reminder: Optional[Callable[[str], None]] = None

    def record_activity(self) -> None:
        """Called whenever the user moves the mouse, clicks, or types."""
        self.last_user_activity = time.time()

    def is_user_idle(self) -> bool:
        return (time.time() - self.last_user_activity) >= self.idle_sleep_seconds

    def is_circadian_bedtime(self, current_dt: Optional[datetime.datetime] = None) -> bool:
        """Determines if the local time matches the pet's natural bedtime."""
        if self.bedtime_hour == self.wake_hour:
            return False
        dt = current_dt or datetime.datetime.now()
        hour = dt.hour
        if self.bedtime_hour > self.wake_hour:
            # e.g. 23:00 to 07:00
            return hour >= self.bedtime_hour or hour < self.wake_hour
        else:
            # Daytime sleep span
            return self.bedtime_hour <= hour < self.wake_hour

    def pet_interaction(self) -> None:
        """Boosts happiness and curiosity on direct petting."""
        self.happiness = min(100.0, self.happiness + 15.0)
        self.curiosity = min(100.0, self.curiosity + 20.0)
        self.record_activity()

    def start_focus(self, work_mins: int = 25, break_mins: int = 5) -> None:
        self.work_duration_seconds = work_mins * 60
        self.break_duration_seconds = break_mins * 60
        self.focus_active = True
        self.focus_phase = "WORK"
        self.focus_seconds_remaining = self.work_duration_seconds
        self.record_activity()

    def stop_focus(self) -> None:
        self.focus_active = False
        self.focus_phase = "WORK"
        self.focus_seconds_remaining = 0

    def tick_second(self) -> Optional[str]:
        """Ticked once per wall-clock second to advance timers."""
        # 1. Advance Pomodoro Focus Mode
        if self.focus_active:
            self.focus_seconds_remaining -= 1
            if self.focus_seconds_remaining <= 0:
                if self.focus_phase == "WORK":
                    self.focus_phase = "BREAK"
                    self.focus_seconds_remaining = self.break_duration_seconds
                    msg = "Focus block complete! Great job! Time for a 5-minute break! ☕"
                else:
                    self.focus_phase = "WORK"
                    self.focus_seconds_remaining = self.work_duration_seconds
                    msg = "Break is over! Ready for another focus session? 🎯"

                if self.on_focus_phase_change:
                    self.on_focus_phase_change(self.focus_phase)
                return msg

        # 2. Advance Wellness Reminder
        now = time.time()
        if self.reminders_enabled and (now - self.last_reminder_time) >= self.reminder_interval_seconds:
            self.last_reminder_time = now
            msg = random.choice(self.reminder_messages)
            if self.on_reminder:
                self.on_reminder(msg)
            return msg

        return None

    def drain_energy(self, amount: float) -> None:
        self.energy = max(0.0, self.energy - amount)

    def recover_energy(self, amount: float) -> None:
        self.energy = min(100.0, self.energy + amount)

    def natural_decay(self) -> None:
        """Gentle continuous stat decay."""
        self.happiness = max(20.0, self.happiness - 0.005)
        self.curiosity = max(10.0, self.curiosity - 0.01)
