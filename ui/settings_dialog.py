"""
Preferences & Wardrobe GUI Dialog for Mochi Desktop Pet.
Provides zero-code visual personalization: appearance, palette picker,
interactive hotkey recording, wellness timers, and live hot-reloading.
"""
import copy
import logging
import tkinter as tk
from tkinter import colorchooser, ttk
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("DesktopPet.SettingsDialog")

PRESET_COLORS = [
    ("Blossom Pink", "#FFB6C1"),
    ("Mint Sage", "#B5EAD7"),
    ("Sky Blue", "#A0C4FF"),
    ("Lavender", "#D0BDF4"),
    ("Buttercup Yellow", "#FFEAA7"),
    ("Peach Sorbet", "#FFDAC1"),
    ("Pure White", "#FFFFFF"),
]


class SettingsDialog:
    """Modal Preferences & Wardrobe dialog for configuring Mochi without editing JSON."""

    _instance: Optional["SettingsDialog"] = None

    def __init__(
        self,
        parent: tk.Tk,
        config_data: Dict[str, Any],
        on_save: Callable[[Dict[str, Any]], None],
    ):
        # Enforce single dialog instance
        if SettingsDialog._instance and SettingsDialog._instance.window.winfo_exists():
            SettingsDialog._instance.window.lift()
            SettingsDialog._instance.window.focus_force()
            return

        SettingsDialog._instance = self
        self.parent = parent
        self.config_data = copy.deepcopy(config_data)
        self.on_save = on_save
        self.is_recording_hotkey = False

        # Working variables
        self.var_name = tk.StringVar(value=self.config_data.get("pet_name", "Mochi"))
        self.var_color = tk.StringVar(value=self.config_data.get("base_color", "#FFB6C1"))
        self.var_auto_color = tk.BooleanVar(value=self.config_data.get("auto_color", True))
        self.var_scale = tk.DoubleVar(value=self.config_data.get("scale", 1.0))

        hotkeys = self.config_data.get("hotkeys", {})
        self.var_hotkey = tk.StringVar(value=hotkeys.get("toggle_visibility", "alt+q").lower())

        circadian = self.config_data.get("circadian", {})
        self.var_bedtime = tk.IntVar(value=circadian.get("bedtime_hour", 23))
        self.var_wake = tk.IntVar(value=circadian.get("wake_hour", 7))
        self.var_dock_delay = tk.IntVar(value=circadian.get("idle_dock_seconds", 15))

        focus = self.config_data.get("focus_mode", {})
        self.var_focus_work = tk.IntVar(value=focus.get("work_duration_minutes", 25))
        self.var_focus_break = tk.IntVar(value=focus.get("break_duration_minutes", 5))

        wellness = self.config_data.get("wellness_reminders", {})
        self.var_wellness_enabled = tk.BooleanVar(value=wellness.get("enabled", True))
        self.var_wellness_interval = tk.IntVar(value=wellness.get("interval_minutes", 20))

        # Create Dialog Window
        self.window = tk.Toplevel(parent)
        self.window.title("Mochi Preferences & Wardrobe 🌸")
        self.window.geometry("500x560")
        self.window.resizable(False, False)
        self.window.attributes("-topmost", True)
        self.window.config(bg="#F9F9FB")

        # Center on screen
        self._center_window(500, 560)

        self._build_ui()
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center_window(self, width: int, height: int) -> None:
        try:
            sw = self.window.winfo_screenwidth()
            sh = self.window.winfo_screenheight()
            x = max(0, (sw - width) // 2)
            y = max(0, (sh - height) // 2)
            self.window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

    def _build_ui(self) -> None:
        style = ttk.Style(self.window)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Configure tab styles
        style.configure("TNotebook", background="#F9F9FB")
        style.configure("TNotebook.Tab", padding=[16, 8], font=("Segoe UI", 10, "bold"))
        style.configure("TFrame", background="#F9F9FB")
        style.configure("TLabel", background="#F9F9FB", font=("Segoe UI", 10))

        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=(16, 8))

        # Tab 1: Appearance & Wardrobe
        tab_wardrobe = ttk.Frame(notebook)
        notebook.add(tab_wardrobe, text="🎨 Appearance & Wardrobe")
        self._build_wardrobe_tab(tab_wardrobe)

        # Tab 2: Hotkeys & Shortcuts
        tab_hotkeys = ttk.Frame(notebook)
        notebook.add(tab_hotkeys, text="⌨️ Hotkeys")
        self._build_hotkeys_tab(tab_hotkeys)

        # Tab 3: Rhythm & Wellness
        tab_wellness = ttk.Frame(notebook)
        notebook.add(tab_wellness, text="⏳ Timers & Rhythm")
        self._build_wellness_tab(tab_wellness)

        # Bottom Action Bar
        action_bar = tk.Frame(self.window, bg="#F0EFF4", height=50)
        action_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)

        btn_cancel = tk.Button(
            action_bar,
            text="Cancel",
            font=("Segoe UI", 10),
            bg="#E2E1E8",
            fg="#222228",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._on_close,
        )
        btn_cancel.pack(side=tk.RIGHT, padx=16, pady=10)

        btn_save = tk.Button(
            action_bar,
            text="Save & Apply ✨",
            font=("Segoe UI", 10, "bold"),
            bg="#FFB6C1",
            activebackground="#FFA2B1",
            fg="#222228",
            relief=tk.FLAT,
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._save_and_apply,
        )
        btn_save.pack(side=tk.RIGHT, padx=(0, 8), pady=10)

    def _build_wardrobe_tab(self, parent: ttk.Frame) -> None:
        container = tk.Frame(parent, bg="#F9F9FB")
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Pet Name
        lbl_name = tk.Label(container, text="Pet Name:", font=("Segoe UI", 10, "bold"), bg="#F9F9FB")
        lbl_name.grid(row=0, column=0, sticky="w", pady=(0, 4))
        ent_name = tk.Entry(container, textvariable=self.var_name, font=("Segoe UI", 10), width=24, relief=tk.SOLID, bd=1)
        ent_name.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 16))

        # Color Palette Swatches
        lbl_colors = tk.Label(container, text="Wardrobe Skin Color:", font=("Segoe UI", 10, "bold"), bg="#F9F9FB")
        lbl_colors.grid(row=2, column=0, sticky="w", pady=(0, 6))

        palette_frame = tk.Frame(container, bg="#F9F9FB")
        palette_frame.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.color_preview = tk.Label(palette_frame, text="  🐰  ", bg=self.var_color.get(), font=("Segoe UI", 14), relief=tk.SOLID, bd=1)
        self.color_preview.pack(side=tk.LEFT, padx=(0, 12))

        for name, hex_code in PRESET_COLORS:
            btn_swatch = tk.Button(
                palette_frame,
                bg=hex_code,
                activebackground=hex_code,
                width=3,
                height=1,
                relief=tk.SOLID,
                bd=1,
                cursor="hand2",
                command=lambda c=hex_code: self._pick_preset_color(c),
            )
            btn_swatch.pack(side=tk.LEFT, padx=3)

        btn_custom = tk.Button(
            palette_frame,
            text="Custom...",
            font=("Segoe UI", 9),
            bg="#FFFFFF",
            relief=tk.SOLID,
            bd=1,
            cursor="hand2",
            command=self._pick_custom_color,
        )
        btn_custom.pack(side=tk.LEFT, padx=(8, 0))

        # Auto-color checkbox
        chk_auto = tk.Checkbutton(
            container,
            text="Auto-adapt color based on mood and circadian lighting",
            variable=self.var_auto_color,
            bg="#F9F9FB",
            font=("Segoe UI", 9),
            activebackground="#F9F9FB",
        )
        chk_auto.grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 16))

        # Size Scale Slider
        lbl_scale = tk.Label(container, text="Mochi Size Scale:", font=("Segoe UI", 10, "bold"), bg="#F9F9FB")
        lbl_scale.grid(row=5, column=0, sticky="w", pady=(0, 4))

        scale_frame = tk.Frame(container, bg="#F9F9FB")
        scale_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        lbl_scale_val = tk.Label(scale_frame, text=f"{int(self.var_scale.get()*100)}%", font=("Segoe UI", 9, "bold"), bg="#F9F9FB", width=6)
        lbl_scale_val.pack(side=tk.RIGHT)

        slider_scale = ttk.Scale(
            scale_frame,
            from_=0.7,
            to=1.5,
            variable=self.var_scale,
            command=lambda v: lbl_scale_val.config(text=f"{int(float(v)*100)}%"),
        )
        slider_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _build_hotkeys_tab(self, parent: ttk.Frame) -> None:
        container = tk.Frame(parent, bg="#F9F9FB")
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        lbl_title = tk.Label(container, text="Toggle Visibility (Summon / Dismiss):", font=("Segoe UI", 10, "bold"), bg="#F9F9FB")
        lbl_title.pack(anchor="w", pady=(0, 6))

        box_frame = tk.Frame(container, bg="#FFFFFF", relief=tk.SOLID, bd=1, padx=12, pady=10)
        box_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_hotkey_display = tk.Label(
            box_frame,
            text=self.var_hotkey.get().upper(),
            font=("Segoe UI", 12, "bold"),
            bg="#FFFFFF",
            fg="#2C3E50",
        )
        self.lbl_hotkey_display.pack(side=tk.LEFT)

        self.btn_record = tk.Button(
            box_frame,
            text="Click to Record New Hotkey ⏺️",
            font=("Segoe UI", 9),
            bg="#EAE8F0",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._start_recording_hotkey,
        )
        self.btn_record.pack(side=tk.RIGHT)

        btn_reset_hk = tk.Button(
            container,
            text="Reset to Default (Alt + Q)",
            font=("Segoe UI", 9),
            bg="#F9F9FB",
            relief=tk.FLAT,
            fg="#555566",
            cursor="hand2",
            command=lambda: self._set_hotkey("alt+q"),
        )
        btn_reset_hk.pack(anchor="w", pady=(0, 16))

        info_box = tk.Label(
            container,
            text=(
                "💡 How Hotkeys Work:\n"
                "• Pressing your hotkey acts as a toggle: summons Mochi when dismissed,\n"
                "  and tucks Mochi into the system tray when visible on screen.\n"
                "• Recommended: Fast 2-key combinations like Alt+Q, Ctrl+Space, or Alt+Z.\n"
                "• Permanent fallback: Ctrl+Shift+B remains active as a backup hotkey."
            ),
            font=("Segoe UI", 9),
            bg="#F0EFF4",
            fg="#333344",
            relief=tk.FLAT,
            padx=12,
            pady=10,
            justify=tk.LEFT,
        )
        info_box.pack(fill=tk.X, pady=(0, 8))

    def _build_wellness_tab(self, parent: ttk.Frame) -> None:
        container = tk.Frame(parent, bg="#F9F9FB")
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Inactivity Corner Docking
        lbl_dock = tk.Label(container, text="Corner Roosting Inactivity Delay:", font=("Segoe UI", 10, "bold"), bg="#F9F9FB")
        lbl_dock.pack(anchor="w", pady=(0, 4))

        dock_frame = tk.Frame(container, bg="#F9F9FB")
        dock_frame.pack(fill=tk.X, pady=(0, 14))

        lbl_dock_val = tk.Label(dock_frame, text=f"{self.var_dock_delay.get()} sec", font=("Segoe UI", 9, "bold"), bg="#F9F9FB", width=8)
        lbl_dock_val.pack(side=tk.RIGHT)

        slider_dock = ttk.Scale(
            dock_frame,
            from_=5,
            to=60,
            variable=self.var_dock_delay,
            command=lambda v: lbl_dock_val.config(text=f"{int(float(v))} sec"),
        )
        slider_dock.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Pomodoro Focus Sprints
        lbl_pomo = tk.Label(container, text="Pomodoro Sprint Duration:", font=("Segoe UI", 10, "bold"), bg="#F9F9FB")
        lbl_pomo.pack(anchor="w", pady=(0, 4))

        pomo_frame = tk.Frame(container, bg="#F9F9FB")
        pomo_frame.pack(fill=tk.X, pady=(0, 14))

        lbl_pomo_val = tk.Label(pomo_frame, text=f"{self.var_focus_work.get()} min", font=("Segoe UI", 9, "bold"), bg="#F9F9FB", width=8)
        lbl_pomo_val.pack(side=tk.RIGHT)

        slider_pomo = ttk.Scale(
            pomo_frame,
            from_=15,
            to=60,
            variable=self.var_focus_work,
            command=lambda v: lbl_pomo_val.config(text=f"{int(float(v))} min"),
        )
        slider_pomo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Circadian Rhythm Bedtime & Wake
        lbl_circadian = tk.Label(container, text="Circadian Rhythm (Sleep Schedule):", font=("Segoe UI", 10, "bold"), bg="#F9F9FB")
        lbl_circadian.pack(anchor="w", pady=(0, 4))

        circ_frame = tk.Frame(container, bg="#F9F9FB")
        circ_frame.pack(fill=tk.X, pady=(0, 14))

        tk.Label(circ_frame, text="Bedtime:", font=("Segoe UI", 9), bg="#F9F9FB").pack(side=tk.LEFT, padx=(0, 4))
        sp_bed = tk.Spinbox(circ_frame, from_=0, to=23, width=4, textvariable=self.var_bedtime, font=("Segoe UI", 9))
        sp_bed.pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(circ_frame, text="Wake Hour:", font=("Segoe UI", 9), bg="#F9F9FB").pack(side=tk.LEFT, padx=(0, 4))
        sp_wake = tk.Spinbox(circ_frame, from_=0, to=23, width=4, textvariable=self.var_wake, font=("Segoe UI", 9))
        sp_wake.pack(side=tk.LEFT)

        # Wellness Reminders Checkbox
        chk_well = tk.Checkbutton(
            container,
            text="Enable gentle wellness speech bubbles (hydration, eye breaks, posture)",
            variable=self.var_wellness_enabled,
            bg="#F9F9FB",
            font=("Segoe UI", 9),
            activebackground="#F9F9FB",
        )
        chk_well.pack(anchor="w", pady=(0, 4))

    def _pick_preset_color(self, hex_code: str) -> None:
        self.var_color.set(hex_code)
        self.color_preview.config(bg=hex_code)

    def _pick_custom_color(self) -> None:
        color = colorchooser.askcolor(initialcolor=self.var_color.get(), title="Select Mochi Skin Color", parent=self.window)
        if color and color[1]:
            self._pick_preset_color(color[1])

    def _start_recording_hotkey(self) -> None:
        self.is_recording_hotkey = True
        self.btn_record.config(text="Press your keys now... (Esc to cancel)", bg="#FFD1DC")
        self.lbl_hotkey_display.config(text="...", fg="#888888")
        self.window.bind("<Key>", self._on_key_press)
        self.window.focus_set()

    def _on_key_press(self, event) -> None:
        if not self.is_recording_hotkey:
            return

        key_sym = event.keysym.lower()
        if key_sym == "escape":
            self._stop_recording_hotkey()
            self.lbl_hotkey_display.config(text=self.var_hotkey.get().upper(), fg="#2C3E50")
            return

        # Check modifier mask
        # 0x0001: Shift, 0x0004: Control, 0x20000: Alt (Windows state)
        state = event.state
        has_ctrl = (state & 0x0004) != 0 or key_sym in ("control_l", "control_r")
        has_shift = (state & 0x0001) != 0 or key_sym in ("shift_l", "shift_r")
        has_alt = (state & 0x20000) != 0 or (state & 0x0008) != 0 or key_sym in ("alt_l", "alt_r")

        # Ignore bare modifier presses without letter/key
        if key_sym in ("control_l", "control_r", "shift_l", "shift_r", "alt_l", "alt_r", "caps_lock"):
            return

        # Map special keysyms
        if key_sym == "space":
            key_name = "space"
        elif key_sym == "grave":
            key_name = "`"
        elif key_sym == "asciitilde":
            key_name = "~"
        else:
            key_name = key_sym

        # Build combination
        parts = []
        if has_ctrl:
            parts.append("ctrl")
        if has_alt:
            parts.append("alt")
        if has_shift:
            parts.append("shift")

        if not parts:
            # Enforce at least one modifier key for global safety
            parts.append("alt")

        parts.append(key_name)
        new_hotkey = "+".join(parts)
        self._set_hotkey(new_hotkey)
        self._stop_recording_hotkey()

    def _set_hotkey(self, hk_str: str) -> None:
        self.var_hotkey.set(hk_str.lower())
        self.lbl_hotkey_display.config(text=hk_str.upper(), fg="#2C3E50")

    def _stop_recording_hotkey(self) -> None:
        self.is_recording_hotkey = False
        self.btn_record.config(text="Click to Record New Hotkey ⏺️", bg="#EAE8F0")
        try:
            self.window.unbind("<Key>")
        except Exception:
            pass

    def _save_and_apply(self) -> None:
        updated = copy.deepcopy(self.config_data)

        updated["pet_name"] = self.var_name.get().strip() or "Mochi"
        updated["base_color"] = self.var_color.get()
        updated["auto_color"] = self.var_auto_color.get()
        updated["scale"] = round(float(self.var_scale.get()), 2)

        if "hotkeys" not in updated:
            updated["hotkeys"] = {}
        updated["hotkeys"]["toggle_visibility"] = self.var_hotkey.get().lower()

        if "circadian" not in updated:
            updated["circadian"] = {}
        updated["circadian"]["bedtime_hour"] = int(self.var_bedtime.get())
        updated["circadian"]["wake_hour"] = int(self.var_wake.get())
        updated["circadian"]["idle_dock_seconds"] = int(self.var_dock_delay.get())

        if "focus_mode" not in updated:
            updated["focus_mode"] = {}
        updated["focus_mode"]["work_duration_minutes"] = int(self.var_focus_work.get())
        updated["focus_mode"]["break_duration_minutes"] = int(self.var_focus_break.get())

        if "wellness_reminders" not in updated:
            updated["wellness_reminders"] = {}
        updated["wellness_reminders"]["enabled"] = self.var_wellness_enabled.get()
        updated["wellness_reminders"]["interval_minutes"] = int(self.var_wellness_interval.get())

        try:
            self.on_save(updated)
            logger.info("Preferences successfully saved and applied.")
        except Exception as e:
            logger.error("Failed to apply saved preferences: %s", e)

        self._on_close()

    def _on_close(self) -> None:
        SettingsDialog._instance = None
        try:
            self.window.destroy()
        except Exception:
            pass
