import pytest
from core.physics import PhysicsEngine, Bounds


def test_desktop_clamping_single_monitor():
    """Verify pet coordinates stay clamped inside standard screen boundaries."""
    bounds = Bounds(0, 0, 1920, 1080)
    physics = PhysicsEngine(width=140, height=140, bounds=bounds, taskbar_height=45)

    # Attempt to place outside left/top
    physics.x = -500
    physics.y = -200
    physics.clamp_position()
    assert physics.x == 0
    assert physics.y == 0

    # Attempt to place beyond right/bottom
    physics.x = 2500
    physics.y = 1500
    physics.clamp_position()
    assert physics.x == 1920 - 140 + physics.corner_offset_x
    assert physics.y == 1080 - 45 - 140 + 12  # ground level atop taskbar


def test_desktop_clamping_multi_monitor_negative_coords():
    """Verify clamping on dual-monitor setup with secondary monitor to the left (negative coordinates)."""
    bounds = Bounds(-1920, 0, 1920, 1080)  # Dual monitor spanning -1920 to +1920
    physics = PhysicsEngine(width=140, height=140, bounds=bounds, taskbar_height=45)

    physics.x = -1500
    physics.y = 500
    physics.clamp_position()
    assert physics.x == -1500  # Valid on left monitor!

    # Out of left-most bounds
    physics.x = -3000
    physics.clamp_position()
    assert physics.x == -1920


def test_taskbar_perching_and_squash_stretch():
    """Verify downward acceleration under gravity until taskbar ground, triggering squash-and-stretch."""
    bounds = Bounds(0, 0, 1920, 1080)
    taskbar_h = 50
    pet_h = 140

    physics = PhysicsEngine(width=140, height=pet_h, bounds=bounds, taskbar_height=taskbar_h)
    expected_ground = physics.ground_y
    physics.y = 100.0
    physics.vy = 0.0
    physics.is_grounded = False

    # Simulate falling under gravity
    ticks = 0
    while not physics.is_grounded and ticks < 100:
        physics.tick()
        ticks += 1

    assert physics.y == expected_ground
    # Impact should trigger squash
    assert physics.squash_x > 0.0

    # Verify squash decay over subsequent ticks
    initial_squash = physics.squash_x
    for _ in range(15):
        physics.tick()
    assert physics.squash_x < initial_squash


def test_drop_and_fling_trajectory():
    """Verify releasing a drag with velocity computes a parabolic trajectory arc."""
    bounds = Bounds(0, 0, 1920, 1080)
    physics = PhysicsEngine(width=140, height=140, bounds=bounds)

    # Simulate drag motion
    physics.start_drag(500, 500)
    physics.update_drag(550, 480)
    physics.update_drag(600, 450)
    physics.update_drag(660, 400)

    vx, vy = physics.release_drag()
    assert vx > 0  # Thrown to the right
    assert vy < 0  # Thrown upward

    # Simulate free-flight ticks
    prev_y = physics.y
    physics.tick()
    assert not physics.is_grounded


def test_home_corner_docking():
    """Verify pet homes in on its cozy bottom-right corner when stationed."""
    bounds = Bounds(0, 0, 1920, 1080)
    physics = PhysicsEngine(width=140, height=140, bounds=bounds, home_corner="bottom_right")
    expected_home_x = 1920 - 140 + physics.corner_offset_x

    assert physics.home_x == expected_home_x
    assert physics.is_near_home() is True

    # Move pet to center of screen
    physics.x = 900.0
    assert physics.is_near_home() is False

    # Step towards home until docked
    while physics.step_towards_home(speed=10.0) != 0:
        pass

    assert physics.x == expected_home_x
    assert physics.is_near_home() is True
