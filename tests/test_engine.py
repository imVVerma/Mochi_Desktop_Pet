import pytest
from main import SingleInstanceLock
from tests.conftest import MockTk, MockCanvas


def test_main_import_safety():
    """Ensure main and core modules import without any missing references or syntax errors."""
    import main
    from core.engine import PetEngine
    from core.physics import get_virtual_screen_bounds, get_primary_taskbar_height
    from core.config import resolve_config_path

    assert callable(get_virtual_screen_bounds)
    assert callable(get_primary_taskbar_height)
    assert callable(resolve_config_path)


def test_single_instance_lock():
    """Verify that multiple instances are detected to prevent infinite duplicate loops."""
    lock1 = SingleInstanceLock(name="DesktopPetTestMutex123")
    assert lock1.already_running is False

    lock2 = SingleInstanceLock(name="DesktopPetTestMutex123")
    assert lock2.already_running is True

    lock1.release()
    lock2.release()


def test_pet_engine_instantiation_headless(mock_tkinter, tmp_path):
    """Instantiate PetEngine in headless mock mode, verifying end-to-end integration."""
    config_file = tmp_path / "engine_test_config.json"
    from core.engine import PetEngine

    engine = PetEngine(config_path=str(config_file))
    assert engine.physics is not None
    assert engine.fsm is not None
    assert engine.stats is not None
    assert engine.window is not None

    # Step loops
    engine.update_loop()
    engine.wall_clock_loop()

    # User actions
    engine.handle_pet()
    assert engine.stats.happiness > 80

    engine.toggle_focus_mode()
    assert engine.stats.focus_active is True

    engine.toggle_sleep()
    assert engine.fsm.state == "SLEEPING"

    engine.exit_app()
    assert engine.is_running is False


def test_pet_engine_start_with_toggle_event(mock_tkinter, tmp_path):
    """Verify engine.start() initializes threads and mainloop without any NameError or crash."""
    config_file = tmp_path / "engine_start_test_config.json"
    from core.engine import PetEngine

    engine = PetEngine(config_path=str(config_file), toggle_event=123)
    # Mock mainloop to immediately exit so test doesn't block
    engine.window.root.mainloop = lambda: engine.exit_app()
    engine.start()
    assert engine.is_running is False
