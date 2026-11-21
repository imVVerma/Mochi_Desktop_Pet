import json
import os
import time
import pytest
from core.config import ConfigManager, DEFAULT_CONFIG


def test_default_config_creation(tmp_path):
    config_file = tmp_path / "test_config.json"
    manager = ConfigManager(str(config_file))

    assert os.path.exists(str(config_file))
    assert manager.get("pet_name") == "Mochi"
    assert manager.get("scale") == 1.0


def test_corrupt_config_recovery(tmp_path):
    """Graceful Config Recovery: Corrupt config.json with invalid syntax and verify recovery."""
    config_file = tmp_path / "corrupt_config.json"
    with open(str(config_file), "w", encoding="utf-8") as f:
        f.write("{ invalid_json: True, syntax_error: [")

    manager = ConfigManager(str(config_file))
    # Must recover with default settings
    assert manager.get("pet_name") == "Mochi"
    assert manager.get("walk_speed") == 3.0
    assert "focus_mode" in manager.data


def test_deep_merge_partial_config(tmp_path):
    """User provides partial config; remaining keys must merge with defaults."""
    config_file = tmp_path / "partial_config.json"
    with open(str(config_file), "w", encoding="utf-8") as f:
        json.dump({"pet_name": "Koko", "scale": 1.5}, f)

    manager = ConfigManager(str(config_file))
    assert manager.get("pet_name") == "Koko"
    assert manager.get("scale") == 1.5
    # Nested defaults should be preserved
    assert manager.get("focus_mode")["work_duration_minutes"] == 25


def test_hot_reloading(tmp_path):
    """Verifies that modifications to config on disk are automatically detected."""
    config_file = tmp_path / "hot_config.json"
    manager = ConfigManager(str(config_file))
    assert manager.get("pet_name") == "Mochi"

    time.sleep(0.05)
    with open(str(config_file), "w", encoding="utf-8") as f:
        json.dump({"pet_name": "Bubbles", "scale": 2.0}, f)

    reloaded = manager.check_hot_reload()
    assert reloaded is True
    assert manager.get("pet_name") == "Bubbles"
