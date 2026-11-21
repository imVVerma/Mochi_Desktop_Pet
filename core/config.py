import json
import logging
import os
import sys
from typing import Any, Dict

logger = logging.getLogger("DesktopPet.Config")


def resolve_config_path(preferred_path: str = "config.json") -> str:
    """Safely resolves the path to config.json across standalone EXE and script environments."""
    if os.path.isabs(preferred_path):
        return preferred_path

    # 1. If running as compiled PyInstaller executable, check next to the EXE
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        candidate = os.path.join(exe_dir, preferred_path)
        if os.path.exists(candidate):
            return candidate
        # Verify if directory is writable
        try:
            test_file = os.path.join(exe_dir, ".pet_write_test")
            with open(test_file, "w") as f:
                f.write("1")
            os.remove(test_file)
            return candidate
        except Exception:
            pass

    # 2. Check current working directory or relative to root
    if os.path.exists(preferred_path):
        return os.path.abspath(preferred_path)

    # 3. Test if current directory is writable
    try:
        test_file = ".pet_write_test"
        with open(test_file, "w") as f:
            f.write("1")
        os.remove(test_file)
        return os.path.abspath(preferred_path)
    except Exception:
        # Fallback to user AppData / home directory if directory is write-protected
        appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
        safe_dir = os.path.join(appdata, "DesktopPet")
        try:
            os.makedirs(safe_dir, exist_ok=True)
            return os.path.join(safe_dir, preferred_path)
        except Exception:
            return os.path.abspath(preferred_path)


DEFAULT_CONFIG: Dict[str, Any] = {
    "pet_name": "Mochi",
    "species": "bunny",
    "home_corner": "bottom_right",
    "scale": 1.0,
    "base_color": "#FFB6C1",
    "auto_color": True,
    "eye_color": "#2C3E50",
    "walk_speed": 3.0,
    "taskbar_height": 45,
    "transparent_color": "#000001",
    "sound_enabled": False,
    "focus_mode": {
        "work_duration_minutes": 25,
        "break_duration_minutes": 5,
        "auto_break": True
    },
    "wellness_reminders": {
        "enabled": True,
        "interval_minutes": 20,
        "messages": [
            "Time to drink some water! 💧",
            "Look 20 feet away for 20 seconds! 👁️",
            "Roll your shoulders and stretch! 🧘",
            "Take a slow deep breath in... and out. 🌸",
            "Posture check! Sit up comfortably. 🪑"
        ]
    },
    "circadian": {
        "bedtime_hour": 23,
        "wake_hour": 7,
        "idle_sleep_seconds": 180
    },
    "hotkeys": {
        "toggle_visibility": "ctrl+shift+b",
        "toggle_focus": "ctrl+shift+f",
        "pet": "ctrl+shift+p"
    }
}


class ConfigManager:
    """Manages application configuration, persistence, fallback resilience, and live hot-reloading."""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = resolve_config_path(config_path)
        self.data: Dict[str, Any] = json.loads(json.dumps(DEFAULT_CONFIG))
        self.last_mtime: float = 0.0
        self.load()

    def load(self) -> bool:
        """Loads configuration from disk with graceful corruption recovery."""
        if not os.path.exists(self.config_path):
            logger.info("Config file '%s' not found. Creating default configuration.", self.config_path)
            self.save()
            return True

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    logger.warning("Config file '%s' is empty. Using defaults.", self.config_path)
                    self.data = json.loads(json.dumps(DEFAULT_CONFIG))
                    return False
                loaded = json.loads(content)
                if isinstance(loaded, dict):
                    # Merge with defaults to ensure missing keys are present
                    merged = json.loads(json.dumps(DEFAULT_CONFIG))
                    self._deep_update(merged, loaded)
                    self.data = merged
                    self.last_mtime = os.path.getmtime(self.config_path)
                    return True
                else:
                    logger.warning("Config root is not a dictionary. Falling back to defaults.")
                    self.data = json.loads(json.dumps(DEFAULT_CONFIG))
                    return False
        except Exception as e:
            logger.warning("Failed to parse config file '%s': %s. Recovering with default settings.", self.config_path, e)
            self.data = json.loads(json.dumps(DEFAULT_CONFIG))
            return False

    def check_hot_reload(self) -> bool:
        """Checks if config file on disk has changed and reloads it if modified."""
        if not os.path.exists(self.config_path):
            return False
        try:
            mtime = os.path.getmtime(self.config_path)
            if mtime > self.last_mtime:
                logger.info("Config file modified on disk. Hot-reloading...")
                return self.load()
        except OSError:
            pass
        return False

    def save(self) -> bool:
        """Persists current configuration to disk."""
        try:
            temp_path = self.config_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, self.config_path)
            self.last_mtime = os.path.getmtime(self.config_path)
            return True
        except Exception as e:
            logger.error("Failed to save config to '%s': %s", self.config_path, e)
            return False

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any, auto_save: bool = False) -> None:
        self.data[key] = value
        if auto_save:
            self.save()

    def _deep_update(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        for k, v in update.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._deep_update(base[k], v)
            else:
                base[k] = v
