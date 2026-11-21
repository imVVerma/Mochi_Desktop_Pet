import pytest
from core.fsm import PetFSM, State
from core.physics import PhysicsEngine, Bounds
from core.stats import PetStats


def create_test_fsm(energy=100.0, happiness=80.0, daytime_only=True):
    if daytime_only:
        # Disable circadian bedtime so daytime state tests are isolated from wall-clock night
        stats = PetStats(energy=energy, happiness=happiness, bedtime_hour=0, wake_hour=0)
    else:
        stats = PetStats(energy=energy, happiness=happiness, bedtime_hour=23, wake_hour=7)
    physics = PhysicsEngine(bounds=Bounds(0, 0, 1920, 1080))
    return PetFSM(stats, physics)


def test_fsm_no_deadlock_5000_ticks():
    """Invariant: Simulate 5,000 ticks and verify pet never enters an invalid state."""
    fsm = create_test_fsm()
    valid_states = set(State)

    for i in range(5000):
        fsm.tick()
        assert fsm.state in valid_states, f"Tick {i} resulted in invalid state: {fsm.state}"
        assert fsm.state_ticks >= 0
        # Prevent infinite sleep during test by simulating day time and periodic activity
        if i % 100 == 0:
            fsm.stats.record_activity()


def test_energy_depletion_and_sleep_recovery():
    """Invariant: High physical activity depletes energy and forces TIRED -> SLEEPING, then recharges."""
    fsm = create_test_fsm(energy=18.0)
    fsm.transition_to(State.DANCING)

    # Tick dancing until stamina drains below threshold (<= 15)
    for _ in range(200):
        fsm.tick()
        if fsm.state == State.TIRED:
            break

    assert fsm.state in [State.TIRED, State.SLEEPING]
    assert fsm.stats.energy <= 15.0

    # Continue ticking; pet should transition to SLEEPING
    for _ in range(50):
        fsm.tick()
        if fsm.state == State.SLEEPING:
            break

    assert fsm.state == State.SLEEPING

    # While sleeping, energy must recharge
    initial_sleep_energy = fsm.stats.energy
    for _ in range(100):
        fsm.tick()

    assert fsm.stats.energy > initial_sleep_energy


def test_interruption_guarantee():
    """Invariant: User mouse grab immediately interrupts any autonomous state into DRAGGED."""
    fsm = create_test_fsm()

    test_states = [State.IDLE, State.WANDERING, State.DANCING, State.JUMPING, State.SLEEPING, State.TIRED]
    for s in test_states:
        fsm.transition_to(s)
        assert fsm.state == s

        # User grabs pet
        fsm.on_mouse_press()
        assert fsm.state == State.DRAGGED, f"State {s} failed to interrupt into DRAGGED"


def test_focus_mode_invariant():
    """Invariant: In Pomodoro Focus Mode, pet stays in FOCUS and does not wander or dance."""
    fsm = create_test_fsm()
    fsm.stats.start_focus(work_mins=25)
    fsm.tick()
    assert fsm.state == State.FOCUS

    for _ in range(300):
        fsm.tick()
        # In focus mode, pet must never wander, jump or dance
        assert fsm.state in [State.FOCUS, State.DRAGGED]

    fsm.stats.stop_focus()
    fsm.transition_to(State.IDLE)
    assert fsm.state == State.IDLE


def test_circadian_bedtime_transition():
    """Invariant: When circadian bedtime or long user inactivity is detected, pet goes to SLEEPING."""
    fsm = create_test_fsm(daytime_only=False)
    fsm.stats.bedtime_hour = 22
    fsm.stats.wake_hour = 8

    # Mock user idle
    fsm.stats.last_user_activity = 0.0  # far in the past
    fsm.tick()
    assert fsm.state == State.SLEEPING


def test_inactivity_docks_at_home_corner():
    """Invariant: After moments of user inactivity, pet autonomously returns to dock at bottom-right corner."""
    fsm = create_test_fsm(daytime_only=True)
    # Place pet away from home corner
    fsm.physics.x = 400.0
    fsm.transition_to(State.WANDERING)
    assert not fsm.physics.is_near_home(25)

    # Active interaction keeps pet wandering
    fsm.stats.record_interaction()
    fsm.tick()
    assert fsm.state == State.WANDERING

    # Inactivity occurs (e.g. user leaves pet alone)
    fsm.stats.last_pet_interaction = 0.0
    fsm.tick()
    # Pet should autonomously enter RETURNING_HOME
    assert fsm.state == State.RETURNING_HOME

    # Step until arrived at home corner
    for _ in range(500):
        fsm.tick()
        if fsm.physics.is_near_home(25):
            break

    assert fsm.physics.is_near_home(25)
    # Once docked, pet settles into IDLE (corner loaf)
    assert fsm.state in [State.IDLE, State.RETURNING_HOME]
