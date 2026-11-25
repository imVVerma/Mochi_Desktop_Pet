import math
import random
import time
import tracemalloc
import pytest
from core.fsm import PetFSM, State
from core.physics import PhysicsEngine, Bounds
from core.stats import PetStats
from tests.conftest import MockCanvas
from ui.canvas_renderer import CanvasRenderer


def test_cpu_ceiling_benchmark():
    """Eval Benchmark: In headless simulation, tick calculations per frame must execute in < 2.0 ms."""
    stats = PetStats()
    physics = PhysicsEngine(bounds=Bounds(0, 0, 1920, 1080))
    fsm = PetFSM(stats, physics)

    mock_canvas = MockCanvas()
    renderer = CanvasRenderer(mock_canvas, 140, 140)

    num_frames = 2000
    start_time = time.perf_counter()

    for i in range(num_frames):
        physics.tick()
        fsm.tick()
        offset_y, stretch_x = physics.get_visual_deformations()
        renderer.draw(
            state=fsm.state,
            stats=stats,
            offset_y=offset_y,
            stretch_x=stretch_x,
            mouse_rel_x=25.0,
            mouse_rel_y=15.0,
            velocity_speed=0.0,
        )

    elapsed_seconds = time.perf_counter() - start_time
    ms_per_frame = (elapsed_seconds / num_frames) * 1000.0

    print(f"\n[Benchmark] Avg execution per frame: {ms_per_frame:.4f} ms")
    assert ms_per_frame < 2.0, f"Frame tick exceeded CPU budget: {ms_per_frame:.3f} ms >= 2.0 ms"


def test_memory_leak_50000_ticks():
    """Eval Benchmark: 50,000-tick endurance simulation. Heap memory delta must remain below 5.0 MB."""
    tracemalloc.start()

    stats = PetStats()
    physics = PhysicsEngine(bounds=Bounds(0, 0, 1920, 1080))
    fsm = PetFSM(stats, physics)

    mock_canvas = MockCanvas()
    renderer = CanvasRenderer(mock_canvas, 140, 140)

    # Warmup
    for _ in range(500):
        physics.tick()
        fsm.tick()
        offset_y, stretch_x = physics.get_visual_deformations()
        renderer.draw(fsm.state, stats, offset_y, stretch_x)

    snapshot_start = tracemalloc.take_snapshot()

    # 50,000 tick endurance run
    for i in range(50000):
        physics.tick()
        fsm.tick()
        offset_y, stretch_x = physics.get_visual_deformations()
        renderer.draw(fsm.state, stats, offset_y, stretch_x)

        if i % 1000 == 0:
            stats.record_activity()
            renderer.spawn_particle("z", "#7E57C2")

    snapshot_end = tracemalloc.take_snapshot()
    tracemalloc.stop()

    top_stats = snapshot_end.compare_to(snapshot_start, "lineno")
    total_diff_bytes = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
    total_diff_mb = total_diff_bytes / (1024 * 1024)

    print(f"\n[Benchmark] 50,000-tick heap growth: {total_diff_mb:.3f} MB")
    assert total_diff_mb < 5.0, f"Memory growth exceeded limit: {total_diff_mb:.2f} MB >= 5.0 MB"


def test_rapid_drag_chaos():
    """Stress Test: 1,000 rapid chaotic mouse drag and release flings."""
    bounds = Bounds(0, 0, 1920, 1080)
    physics = PhysicsEngine(width=140, height=140, bounds=bounds)
    stats = PetStats()
    fsm = PetFSM(stats, physics)

    for i in range(1000):
        # Pick random cursor coordinates
        cx = random.uniform(-1000, 3000)
        cy = random.uniform(-500, 2000)

        fsm.on_mouse_press()
        physics.start_drag(cx, cy)

        for _ in range(random.randint(1, 5)):
            cx += random.uniform(-50, 50)
            cy += random.uniform(-50, 50)
            physics.update_drag(cx, cy)

        vx, vy = physics.release_drag()
        fsm.on_mouse_release(vx, vy)

        for _ in range(random.randint(5, 20)):
            physics.tick()
            fsm.tick()

        # Coordinate assertions
        assert not math.isnan(physics.x)
        assert not math.isnan(physics.y)
        assert not math.isinf(physics.x)
        assert not math.isinf(physics.y)
        assert bounds.min_x <= physics.x <= bounds.max_x - physics.width + physics.corner_offset_x
        assert bounds.min_y <= physics.y <= physics.ground_y
