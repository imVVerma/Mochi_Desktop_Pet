"""
Preferences & Wardrobe GUI Dialog for Desktop Pet.
Features modern pastel styling, live interactive avatar preview,
instant keyboard hotkey recorder, and automatic Windows Search indexing.
"""
import copy
import logging
import sys
import tkinter as tk
from tkinter import colorchooser, ttk
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("DesktopPet.SettingsDialog")

PRESET_COLORS = [
    ("Blossom Pink", "#FFB6C1"),
    ("Mint Sage", "#B5EAD7"),
    ("Sky Blue", "#A0C4FF"),
    ("Lavender", "#D0BDF4"),
    ("Buttercup", "#FFEAA7"),
    ("Peach Sorbet", "#FFDAC1"),
    ("Cotton White", "#FFFFFF"),
    ("Midnight Berry", "#957DAD"),
]


class SettingsDialog:
    """Delightful, modern modal Preferences & Wardrobe dialog with live preview."""

    _instance: Optional["SettingsDialog"] = None

    def __init__(
        self,
        parent: tk.Tk,
        config_data: Dict[str, Any],
        on_save: Callable[[Dict[str, Any]], None],
    ):
        if SettingsDialog._instance and SettingsDialog._instance.window.winfo_exists():
            SettingsDialog._instance.window.lift()
            SettingsDialog._instance.window.focus_force()
            return

        SettingsDialog._instance = self
        self.parent = parent
        self.config_data = copy.deepcopy(config_data)
        self.old_pet_name = self.config_data.get("pet_name", "Mochi")
        self.on_save = on_save
        self.is_recording_hotkey = False

        # Config variables
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

        # Window setup
        self.window = tk.Toplevel(parent)
        self.window.title(f"{self.var_name.get()} — Preferences & Wardrobe 🌸")
        self.window.geometry("540x630")
        self.window.resizable(False, False)
        self.window.attributes("-topmost", True)
        self.window.config(bg="#F6F7FB")

        self._center_window(540, 630)
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
        # Header Card with Live Mochi Avatar
        header_card = tk.Frame(self.window, bg="#FFFFFF", relief=tk.FLAT, bd=0)
        header_card.pack(fill=tk.X, padx=16, pady=(16, 10))

        # Live avatar preview canvas
        self.preview_canvas = tk.Canvas(header_card, width=88, height=88, bg="#FFFFFF", highlightthickness=0)
        self.preview_canvas.pack(side=tk.LEFT, padx=(12, 16), pady=10)
        self._redraw_avatar_preview()

        # Header Titles
        info_frame = tk.Frame(header_card, bg="#FFFFFF")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=12)

        self.lbl_header_name = tk.Label(
            info_frame,
            text=f"🐾 {self.var_name.get()}",
            font=("Segoe UI", 16, "bold"),
            bg="#FFFFFF",
            fg="#2C3E50",
        )
        self.lbl_header_name.pack(anchor="w")

        lbl_header_sub = tk.Label(
            info_frame,
            text="Virtual Desk Companion & Wellness Buddy",
            font=("Segoe UI", 9),
            bg="#FFFFFF",
            fg="#7F8C8D",
        )
        lbl_header_sub.pack(anchor="w", pady=(2, 0))

        # Styled Notebook for Tabs
        style = ttk.Style(self.window)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TNotebook", background="#F6F7FB")
        style.configure("TNotebook.Tab", padding=[16, 8], font=("Segoe UI", 9, "bold"))
        style.configure("TFrame", background="#F6F7FB")

        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        # Tab 1: Wardrobe & Look
        tab_wardrobe = ttk.Frame(notebook)
        notebook.add(tab_wardrobe, text="🎨 Wardrobe")
        self._build_wardrobe_tab(tab_wardrobe)

        # Tab 2: Hotkeys & Shortcuts
        tab_hotkeys = ttk.Frame(notebook)
        notebook.add(tab_hotkeys, text="⌨️ Hotkeys & Search")
        self._build_hotkeys_tab(tab_hotkeys)

        # Tab 3: Habits & Rhythm
        tab_wellness = ttk.Frame(notebook)
        notebook.add(tab_wellness, text="⏳ Habits & Focus")
        self._build_wellness_tab(tab_wellness)

        # Bottom Action Bar
        bottom_bar = tk.Frame(self.window, bg="#ECEEF4", height=54)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)

        btn_cancel = tk.Button(
            bottom_bar,
            text="Cancel",
            font=("Segoe UI", 9),
            bg="#FFFFFF",
            fg="#555566",
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._on_close,
        )
        btn_cancel.pack(side=tk.RIGHT, padx=16, pady=10)

        btn_save = tk.Button(
            bottom_bar,
            text="Save & Apply ✨",
            font=("Segoe UI", 9, "bold"),
            bg="#FFB6C1",
            activebackground="#FFA2B1",
            fg="#222228",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            cursor="hand2",
            command=self._save_and_apply,
        )
        btn_save.pack(side=tk.RIGHT, padx=(0, 6), pady=10)

    def _redraw_avatar_preview(self) -> None:
        c = self.preview_canvas
        c.delete("all")
        color = self.var_color.get()

        # Floppy Ears
        c.create_polygon([20, 42, 16, 14, 28, 8, 34, 18, 32, 42], fill=color, outline="#222228", width=2)
        c.create_polygon([68, 42, 66, 18, 72, 8, 84, 14, 80, 42], fill=color, outline="#222228", width=2)
        c.create_polygon([20, 36, 18, 16, 26, 12, 30, 20], fill="#FFD1DC")
        c.create_polygon([70, 20, 74, 12, 82, 16, 80, 36], fill="#FFD1DC")

        # Chubby Bunny Body
        c.create_oval([14, 28, 86, 84], fill=color, outline="#222228", width=2)
        # Soft Cream Belly
        c.create_oval([28, 48, 72, 80], fill="#FFF9F2", outline="")

        # Sparkle Eyes
        c.create_oval([30, 44, 38, 54], fill="#18181D")
        c.create_oval([32, 46, 35, 49], fill="#FFFFFF")
        c.create_oval([62, 44, 70, 54], fill="#18181D")
        c.create_oval([64, 46, 67, 49], fill="#FFFFFF")

        # Nose & Smile
        c.create_polygon([48, 54, 52, 54, 50, 57], fill="#FF7597")
        c.create_arc([44, 56, 50, 62], start=0, extent=180, style=tk.ARC, outline="#222228", width=2)
        c.create_arc([50, 56, 56, 62], start=0, extent=180, style=tk.ARC, outline="#222228", width=2)

        # Cheerful Blush
        c.create_oval([24, 54, 32, 60], fill="#FFCCD5", outline="")
        c.create_oval([68, 54, 76, 60], fill="#FFCCD5", outline="")

    def _build_wardrobe_tab(self, parent: ttk.Frame) -> None:
        card = tk.Frame(parent, bg="#FFFFFF", padx=16, pady=16)
        card.pack(fill=tk.BOTH, expand=True, padx=4, pady=8)

        # Name Input
        lbl_name = tk.Label(card, text="Companion Name:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_name.pack(anchor="w", pady=(0, 4))

        name_box = tk.Frame(card, bg="#F5F6FA", relief=tk.SOLID, bd=1, padx=8, pady=4)
        name_box.pack(fill=tk.X, pady=(0, 14))

        ent_name = tk.Entry(
            name_box,
            textvariable=self.var_name,
            font=("Segoe UI", 11),
            bg="#F5F6FA",
            relief=tk.FLAT,
            bd=0,
        )
        ent_name.pack(fill=tk.X, expand=True)
        ent_name.bind("<KeyRelease>", lambda e: self.lbl_header_name.config(text=f"🐾 {self.var_name.get() or 'Mochi'}"))

        # Skin Palette
        lbl_colors = tk.Label(card, text="Skin Palette & Wardrobe Color:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_colors.pack(anchor="w", pady=(0, 6))

        palette_row = tk.Frame(card, bg="#FFFFFF")
        palette_row.pack(fill=tk.X, pady=(0, 14))

        for name, hex_code in PRESET_COLORS:
            btn_color = tk.Button(
                palette_row,
                bg=hex_code,
                activebackground=hex_code,
                width=3,
                height=1,
                relief=tk.SOLID,
                bd=1,
                cursor="hand2",
                command=lambda c=hex_code: self._apply_color(c),
            )
            btn_color.pack(side=tk.LEFT, padx=3)

        btn_custom = tk.Button(
            palette_row,
            text="Pick Custom 🎨",
            font=("Segoe UI", 9),
            bg="#F5F6FA",
            relief=tk.SOLID,
            bd=1,
            cursor="hand2",
            padx=8,
            command=self._pick_custom_color,
        )
        btn_custom.pack(side=tk.LEFT, padx=(8, 0))

        # Size Scale Slider
        lbl_scale = tk.Label(card, text="Mochi Scale Size:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_scale.pack(anchor="w", pady=(0, 4))

        scale_row = tk.Frame(card, bg="#FFFFFF")
        scale_row.pack(fill=tk.X, pady=(0, 12))

        lbl_scale_val = tk.Label(scale_row, text=f"{int(self.var_scale.get()*100)}%", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", width=6)
        lbl_scale_val.pack(side=tk.RIGHT)

        slider_scale = ttk.Scale(
            scale_row,
            from_=0.7,
            to=1.5,
            variable=self.var_scale,
            command=lambda v: lbl_scale_val.config(text=f"{int(float(v)*100)}%"),
        )
        slider_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Auto-adapt checkbox
        chk_auto = tk.Checkbutton(
            card,
            text="Auto-adapt color based on emotional states and bedtime",
            variable=self.var_auto_color,
            bg="#FFFFFF",
            font=("Segoe UI", 9),
            activebackground="#FFFFFF",
        )
        chk_auto.pack(anchor="w", pady=(4, 0))

    def _build_hotkeys_tab(self, parent: ttk.Frame) -> None:
        card = tk.Frame(parent, bg="#FFFFFF", padx=16, pady=16)
        card.pack(fill=tk.BOTH, expand=True, padx=4, pady=8)

        lbl_hk_title = tk.Label(card, text="Toggle Pet (Summon / Dismiss Hotkey):", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_hk_title.pack(anchor="w", pady=(0, 6))

        # Keycap visual pill
        pill_frame = tk.Frame(card, bg="#F5F6FA", relief=tk.SOLID, bd=1, padx=14, pady=10)
        pill_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_hotkey_caps = tk.Label(
            pill_frame,
            text=self._format_keycap_display(self.var_hotkey.get()),
            font=("Segoe UI", 12, "bold"),
            bg="#F5F6FA",
            fg="#2C3E50",
        )
        self.lbl_hotkey_caps.pack(side=tk.LEFT)

        self.btn_record = tk.Button(
            pill_frame,
            text="Record New Hotkey ⏺️",
            font=("Segoe UI", 9, "bold"),
            bg="#FFB6C1",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._start_recording_hotkey,
        )
        self.btn_record.pack(side=tk.RIGHT)

        btn_reset = tk.Button(
            card,
            text="Reset to Recommended Default (Alt + Q)",
            font=("Segoe UI", 9),
            bg="#FFFFFF",
            fg="#7F8C8D",
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self._set_hotkey("alt+q"),
        )
        btn_reset.pack(anchor="w", pady=(0, 14))

        # Windows Search Integration Callout
        search_card = tk.Frame(card, bg="#EEF5FF", relief=tk.FLAT, bd=0, padx=12, pady=10)
        search_card.pack(fill=tk.X, pady=(0, 8))

        lbl_search_info = tk.Label(
            search_card,
            text=(
                "🔍 Windows Search Bar Integration:\n"
                f"• When you rename your pet above, Mochi automatically updates your\n"
                f"  Windows Start Menu shortcut so typing your pet's name finds it immediately!\n"
                f"• Clicking the shortcut or pressing the hotkey toggles open/closed."
            ),
            font=("Segoe UI", 9),
            bg="#EEF5FF",
            fg="#1A365D",
            justify=tk.LEFT,
        )
        lbl_search_info.pack(anchor="w")

    def _build_wellness_tab(self, parent: ttk.Frame) -> None:
        card = tk.Frame(parent, bg="#FFFFFF", padx=16, pady=16)
        card.pack(fill=tk.BOTH, expand=True, padx=4, pady=8)

        # Inactivity Corner Docking
        lbl_dock = tk.Label(card, text="Taskbar Corner Docking (Inactivity Delay):", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_dock.pack(anchor="w", pady=(0, 4))

        dock_row = tk.Frame(card, bg="#FFFFFF")
        dock_row.pack(fill=tk.X, pady=(0, 12))

        lbl_dock_val = tk.Label(dock_row, text=f"{self.var_dock_delay.get()}s", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", width=6)
        lbl_dock_val.pack(side=tk.RIGHT)

        slider_dock = ttk.Scale(
            dock_row,
            from_=5,
            to=60,
            variable=self.var_dock_delay,
            command=lambda v: lbl_dock_val.config(text=f"{int(float(v))}s"),
        )
        slider_dock.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Pomodoro Sprint
        lbl_pomo = tk.Label(card, text="Pomodoro Focus Sprint Duration:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_pomo.pack(anchor="w", pady=(0, 4))

        pomo_row = tk.Frame(card, bg="#FFFFFF")
        pomo_row.pack(fill=tk.X, pady=(0, 12))

        lbl_pomo_val = tk.Label(pomo_row, text=f"{self.var_focus_work.get()} min", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", width=6)
        lbl_pomo_val.pack(side=tk.RIGHT)

        slider_pomo = ttk.Scale(
            pomo_row,
            from_=15,
            to=60,
            variable=self.var_focus_work,
            command=lambda v: lbl_pomo_val.config(text=f"{int(float(v))} min"),
        )
        slider_pomo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Bedtime & Wake Clock
        lbl_sleep = tk.Label(card, text="Circadian Sleep Schedule:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_sleep.pack(anchor="w", pady=(0, 4))

        sleep_row = tk.Frame(card, bg="#FFFFFF")
        sleep_row.pack(fill=tk.X, pady=(0, 12))

        tk.Label(sleep_row, text="Bedtime:", font=("Segoe UI", 9), bg="#FFFFFF").pack(side=tk.LEFT, padx=(0, 4))
        tk.Spinbox(sleep_row, from_=0, to=23, width=4, textvariable=self.var_bedtime, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(sleep_row, text="Wake Time:", font=("Segoe UI", 9), bg="#FFFFFF").pack(side=tk.LEFT, padx=(0, 4))
        tk.Spinbox(sleep_row, from_=0, to=23, width=4, textvariable=self.var_wake, font=("Segoe UI", 9)).pack(side=tk.LEFT)

        # Wellness Reminders
        chk_wellness = tk.Checkbutton(
            card,
            text="Enable gentle wellness speech bubbles (water, eye breaks, posture)",
            variable=self.var_wellness_enabled,
            bg="#FFFFFF",
            font=("Segoe UI", 9),
            activebackground="#FFFFFF",
        )
        chk_wellness.pack(anchor="w", pady=(4, 0))

    def _format_keycap_display(self, hk_str: str) -> str:
        parts = [p.capitalize() for p in hk_str.replace("+", " ").split() if p.strip()]
        return " + ".join(f"[{p}]" for p in parts) if parts else "[None]"

    def _apply_color(self, hex_code: str) -> None:
        self.var_color.set(hex_code)
        self._redraw_avatar_preview()

    def _pick_custom_color(self) -> None:
        color = colorchooser.askcolor(initialcolor=self.var_color.get(), title="Select Skin Color", parent=self.window)
        if color and color[1]:
            self._apply_color(color[1])

    def _start_recording_hotkey(self) -> None:
        self.is_recording_hotkey = True
        self.btn_record.config(text="Press any key combo... (Esc)", bg="#FFD1DC")
        self.lbl_hotkey_caps.config(text="[ ⏺️ Listening... ]", fg="#E74C3C")
        self.window.bind("<Key>", self._on_key_press)
        self.window.focus_set()

    def _on_key_press(self, event) -> None:
        if not self.is_recording_hotkey:
            return

        key_sym = event.keysym.lower()
        if key_sym == "escape":
            self._stop_recording_hotkey()
            self.lbl_hotkey_caps.config(text=self._format_keycap_display(self.var_hotkey.get()), fg="#2C3E50")
            return

        state = event.state
        has_ctrl = (state & 0x0004) != 0 or key_sym in ("control_l", "control_r")
        has_shift = (state & 0x0001) != 0 or key_sym in ("shift_l", "shift_r")
        has_alt = (state & 0x20000) != 0 or (state & 0x0008) != 0 or key_sym in ("alt_l", "alt_r")

        if key_sym in ("control_l", "control_r", "shift_l", "shift_r", "alt_l", "alt_r", "caps_lock"):
            return

        key_name = key_sym
        if key_sym == "space":
            key_name = "space"
        elif key_sym in ("grave", "asciitilde"):
            key_name = "~"

        parts = []
        if has_ctrl:
            parts.append("ctrl")
        if has_alt:
            parts.append("alt")
        if has_shift:
            parts.append("shift")

        if not parts:
            parts.append("alt")

        parts.append(key_name)
        new_hk = "+".join(parts)
        self._set_hotkey(new_hk)
        self._stop_recording_hotkey()

    def _set_hotkey(self, hk_str: str) -> None:
        self.var_hotkey.set(hk_str.lower())
        self.lbl_hotkey_caps.config(text=self._format_keycap_display(hk_str), fg="#2C3E50")

    def _stop_recording_hotkey(self) -> None:
        self.is_recording_hotkey = False
        self.btn_record.config(text="Record New Hotkey ⏺️", bg="#FFB6C1")
        try:
            self.window.unbind("<Key>")
        except Exception:
            pass

    def _save_and_apply(self) -> None:
        updated = copy.deepcopy(self.config_data)

        new_name = self.var_name.get().strip() or "Mochi"
        updated["pet_name"] = new_name
        updated["base_color"] = self.var_color.get()
        updated["auto_color"] = self.var_auto_color.get()
        updated["scale"] = round(float(self.var_scale.get()), 2)

        if "hotkeys" not in updated:
            updated["hotkeys"] = {}
        new_hotkey = self.var_hotkey.get().lower()
        updated["hotkeys"]["toggle_visibility"] = new_hotkey

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

        # Update Windows Search Bar shortcut if pet was renamed
        if sys.platform == "win32":
            try:
                from build.install_shortcut import install_shortcuts
                install_shortcuts(pet_name=new_name, old_pet_name=self.old_pet_name, custom_hotkey=new_hotkey)
            except Exception as e:
                logger.debug("Shortcut update notice: %s", e)

        try:
            self.on_save(updated)
            logger.info("Preferences successfully applied for %s.", new_name)
        except Exception as e:
            logger.error("Failed to apply preferences: %s", e)

        self._on_close()

    def _on_close(self) -> None:
        SettingsDialog._instance = None
        try:
            self.window.destroy()
        except Exception:
            pass
