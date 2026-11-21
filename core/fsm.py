import enum
import random
from typing import Optional
from core.stats import PetStats
from core.physics import PhysicsEngine


class State(str, enum.Enum):
    IDLE = "IDLE"
    WANDERING = "WANDERING"
    JUMPING = "JUMPING"
    DANCING = "DANCING"
    EXCITED = "EXCITED"
    TIRED = "TIRED"
    SLEEPING = "SLEEPING"
    DRAGGED = "DRAGGED"
    FALLING = "FALLING"
    FOCUS = "FOCUS"
    RETURNING_HOME = "RETURNING_HOME"


class PetFSM:
    """Finite State Machine controlling autonomous decision making, invariants, and transitions."""

    def __init__(self, stats: PetStats, physics: PhysicsEngine):
        self.stats = stats
        self.physics = physics
        self.state: State = State.IDLE
        self.direction: int = 1  # 1 for right, -1 for left
        self.walk_speed: float = 3.0

        # State timers and durations
        self.state_ticks: int = 0
        self.state_duration_ticks: int = 80  # ~4 seconds default
        self.jump_phase: int = 0

    def transition_to(self, new_state: State) -> None:
        """Enforces clean state transitions and resets state-specific counters."""
        if self.state == new_state and new_state not in [State.WANDERING, State.JUMPING]:
            return

        self.state = new_state
        self.state_ticks = 0

        if new_state == State.WANDERING:
            self.direction = random.choice([1, -1])
            self.state_duration_ticks = random.randint(60, 140)  # 3-7 seconds
        elif new_state == State.IDLE:
            self.state_duration_ticks = random.randint(50, 100)
        elif new_state == State.DANCING:
            self.state_duration_ticks = random.randint(60, 100)
        elif new_state == State.EXCITED:
            self.state_duration_ticks = random.randint(40, 80)
        elif new_state == State.JUMPING:
            self.state_duration_ticks = 30
            self.jump_phase = 0
            if self.physics.is_grounded:
                self.physics.apply_impulse(self.direction * 3.0, -11.0)
        elif new_state == State.TIRED:
            self.state_duration_ticks = 40
        elif new_state == State.SLEEPING:
            self.state_duration_ticks = 200  # Will sleep until recharged or woken
        elif new_state == State.RETURNING_HOME:
            self.state_duration_ticks = 800  # Generous duration to cross multi-monitor screens
            self.direction = 1 if self.physics.home_x > self.physics.x else -1

    def on_mouse_press(self) -> None:
        """Immediate interruption guarantee: user grab overrides any autonomous state."""
        self.stats.record_interaction()
        self.transition_to(State.DRAGGED)

    def on_mouse_release(self, vx: float, vy: float) -> None:
        """Handles releasing the pet with fling trajectory."""
        self.stats.record_interaction()
        if abs(vx) > 2.0 or vy < -2.0 or not self.physics.is_grounded:
            self.transition_to(State.FALLING)
        else:
            if self.stats.focus_active:
                self.transition_to(State.FOCUS if self.physics.is_near_home(30) else State.RETURNING_HOME)
            elif not self.physics.is_near_home(60):
                self.transition_to(State.RETURNING_HOME)
            else:
                self.transition_to(State.EXCITED if self.stats.happiness > 60 else State.IDLE)

    def on_petting(self) -> None:
        """Right-click or petting interaction."""
        self.stats.record_interaction()
        self.stats.pet_interaction()
        if self.state == State.SLEEPING:
            # Waking up
            self.transition_to(State.EXCITED)
        elif not self.stats.focus_active:
            self.transition_to(State.DANCING if self.stats.happiness > 70 else State.EXCITED)

    def on_mouse_proximity(self, dist: float) -> None:
        """Reacts when the mouse cursor enters close vicinity."""
        if dist < 120.0:
            self.stats.record_interaction()
        else:
            self.stats.record_activity()
        if self.state in [State.IDLE, State.WANDERING] and dist < 85.0:
            self.stats.curiosity = min(100.0, self.stats.curiosity + 10.0)
            self.transition_to(State.EXCITED)

    def tick(self) -> None:
        """Updates FSM logic, drains/recharges energy, and triggers state transitions."""
        self.state_ticks += 1

        # 1. Update Energy based on current physical exertion
        if self.state == State.DANCING:
            self.stats.drain_energy(0.15)
        elif self.state == State.JUMPING:
            self.stats.drain_energy(0.25)
        elif self.state == State.EXCITED:
            self.stats.drain_energy(0.10)
        elif self.state == State.WANDERING:
            self.stats.drain_energy(0.04)
        elif self.state == State.SLEEPING:
            self.stats.recover_energy(0.35)
        elif self.state == State.IDLE or self.state == State.FOCUS:
            self.stats.recover_energy(0.02)

        # 2. State-specific invariant enforcement
        if self.state == State.DRAGGED:
            # Held by user, no autonomous expiration
            return

        if self.state == State.FALLING:
            # Wait until landed
            if self.physics.is_grounded:
                if self.stats.focus_active:
                    self.transition_to(State.FOCUS if self.physics.is_near_home(30) else State.RETURNING_HOME)
                elif self.stats.energy <= 15:
                    self.transition_to(State.TIRED)
                elif not self.physics.is_near_home(80):
                    self.transition_to(State.RETURNING_HOME)
                else:
                    self.transition_to(State.EXCITED)
            return

        # Returning Home Motion
        if self.state == State.RETURNING_HOME:
            self.stats.drain_energy(0.02)
            step_dir = self.physics.step_towards_home(self.walk_speed * 1.25)
            if step_dir != 0:
                self.direction = step_dir
            if self.physics.is_near_home(threshold=20.0) or step_dir == 0:
                self.physics.x = self.physics.home_x
                if self.stats.focus_active:
                    self.transition_to(State.FOCUS)
                elif self.stats.is_circadian_bedtime() or self.stats.is_user_idle():
                    self.transition_to(State.SLEEPING)
                else:
                    self.transition_to(State.IDLE)
            return

        # Focus Mode invariant
        if self.stats.focus_active and self.state != State.FOCUS:
            self.transition_to(State.FOCUS)
            return

        # Exhaustion Invariant: Low energy forces tiredness -> sleep
        if self.stats.energy <= 15 and self.state not in [State.TIRED, State.SLEEPING]:
            self.transition_to(State.TIRED)
            return

        if self.state == State.TIRED and self.state_ticks >= self.state_duration_ticks:
            self.transition_to(State.SLEEPING)
            return

        # Inactivity & Bedtime Corner Docking Invariant:
        # After moments of inactivity or at bedtime, Mochi returns home to dock in the bottom-right corner
        if self.state not in [State.SLEEPING, State.TIRED, State.FOCUS, State.RETURNING_HOME]:
            if not self.physics.is_near_home(threshold=20.0):
                if self.stats.is_inactive_for_docking() or self.stats.is_circadian_bedtime() or self.stats.is_user_idle():
                    self.transition_to(State.RETURNING_HOME)
                    return

        # Circadian / Idle Bedtime Invariant (once stationed at home corner)
        if self.state not in [State.SLEEPING, State.TIRED, State.FOCUS]:
            if self.stats.is_circadian_bedtime() or self.stats.is_user_idle():
                self.transition_to(State.SLEEPING)
                return

        # Sleeping State Recovery Check
        if self.state == State.SLEEPING:
            # Stay asleep if exhausted or nighttime or user idle
            if self.stats.energy >= 85 and not self.stats.is_circadian_bedtime() and not self.stats.is_user_idle():
                self.transition_to(State.IDLE)
            return

        # Focus state stays in focus
        if self.state == State.FOCUS:
            return

        # Active Motion Handling
        if self.state == State.WANDERING:
            self.physics.x += self.walk_speed * self.direction
            # Flip direction upon hitting screen bounds
            min_x = self.physics.bounds.min_x + 10
            max_x = self.physics.bounds.max_x - self.physics.width - 10
            if self.physics.x <= min_x:
                self.direction = 1
            elif self.physics.x >= max_x:
                self.direction = -1

        # Periodic Autonomous Decision
        if self.state_ticks >= self.state_duration_ticks:
            self._decide_next_autonomous_state()

    def _decide_next_autonomous_state(self) -> None:
        """Selects the next behavior based on personality, happiness, and curiosity."""
        # If user is inactive, prefer to return home or remain docked in cozy corner loaf
        if self.stats.is_inactive_for_docking():
            if not self.physics.is_near_home(threshold=20.0):
                self.transition_to(State.RETURNING_HOME)
            else:
                self.physics.x = self.physics.home_x
                if self.stats.is_circadian_bedtime() or self.stats.is_user_idle():
                    self.transition_to(State.SLEEPING)
                else:
                    self.transition_to(State.IDLE)
            return

        # When stationed at its home corner, stay stationed in the corner!
        # Mochi plays, dances, wiggles ears, and loafs right in its corner perch without wandering away.
        if self.physics.home_corner != "none" and self.physics.is_near_home(threshold=35.0):
            self.physics.x = self.physics.home_x
            if self.stats.is_circadian_bedtime() or self.stats.is_user_idle():
                self.transition_to(State.SLEEPING)
                return

            corner_choices = [State.IDLE]
            corner_weights = [5]
            if self.stats.happiness > 60:
                corner_choices.extend([State.DANCING, State.JUMPING, State.EXCITED])
                corner_weights.extend([2, 2, 2])
            next_choice = random.choices(corner_choices, weights=corner_weights, k=1)[0]
            self.transition_to(next_choice)
            return

        choices = [State.IDLE, State.WANDERING]
        weights = [4, 5]

        if self.stats.happiness > 70 and self.stats.energy > 40:
            choices.extend([State.DANCING, State.JUMPING])
            weights.extend([3, 2])

        if self.stats.curiosity > 70:
            choices.append(State.EXCITED)
            weights.append(3)

        # If pet has wandered far from its cozy home corner, prioritize heading back
        if not self.physics.is_near_home(75):
            choices.append(State.RETURNING_HOME)
            weights.append(5)

        next_choice = random.choices(choices, weights=weights, k=1)[0]
        self.transition_to(next_choice)
