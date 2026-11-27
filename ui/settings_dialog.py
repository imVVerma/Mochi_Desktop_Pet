"""
Preferences & Wardrobe GUI Dialog for Desktop Pet.
Features contemporary warm & cozy aesthetic, live interactive avatar preview with accessories,
instant keyboard hotkey recorder, flexible custom shortcuts,
and automatic Windows Search indexing.
"""
import copy
import logging
import math
import sys
import tkinter as tk
from tkinter import colorchooser, ttk
from typing import Any, Callable, Dict, List, Optional, Tuple

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

ACCESSORY_OPTIONS = [
    ("🎀 Silk Ribbon", "🎀 Silk Ribbon"),
    ("👑 Royal Crown", "👑 Royal Crown"),
    ("🌸 Sakura Flower", "🌸 Sakura Flower"),
    ("👓 Smart Glasses", "👓 Smart Glasses"),
    ("🎩 Top Hat", "🎩 Gentleman Top Hat"),
    ("🧣 Cozy Scarf", "🧣 Cozy Scarf"),
    ("🐾 Natural", "None"),
]


class SettingsDialog:
    """Delightful, modern modal Preferences & Wardrobe dialog with warm & cozy aesthetic."""

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
        self.swatch_cards: Dict[str, Tuple[tk.Frame, tk.Label, tk.Canvas]] = {}
        self.accessory_cards: Dict[str, Tuple[tk.Frame, tk.Label]] = {}
        self.dock_chips: Dict[int, tk.Button] = {}
        self.pomo_chips: Dict[int, tk.Button] = {}

        # Config variables
        self.var_name = tk.StringVar(value=self.config_data.get("pet_name", "Mochi"))
        self.var_color = tk.StringVar(value=self.config_data.get("base_color", "#FFF4D2"))
        self.var_accessory = tk.StringVar(value=self.config_data.get("accessory", "🧣 Cozy Scarf"))
        self.var_auto_color = tk.BooleanVar(value=self.config_data.get("auto_color", True))
        self.var_scale = tk.DoubleVar(value=self.config_data.get("scale", 1.0))

        hotkeys = self.config_data.get("hotkeys", {})
        self.var_hotkey = tk.StringVar(value=hotkeys.get("toggle_visibility", "alt+q").lower())

        circadian = self.config_data.get("circadian", {})
        self.var_bedtime = tk.IntVar(value=circadian.get("bedtime_hour", 23))
        self.var_wake = tk.IntVar(value=circadian.get("wake_hour", 7))
        self.var_dock_delay = tk.IntVar(value=circadian.get("idle_dock_seconds", 5))

        focus = self.config_mode = self.config_data.get("focus_mode", {})
        self.var_focus_work = tk.IntVar(value=focus.get("work_duration_minutes", 25))
        self.var_focus_break = tk.IntVar(value=focus.get("break_duration_minutes", 5))

        wellness = self.config_data.get("wellness_reminders", {})
        self.var_wellness_enabled = tk.BooleanVar(value=wellness.get("enabled", True))
        self.var_wellness_interval = tk.IntVar(value=wellness.get("interval_minutes", 20))

        # Window setup
        self.window = tk.Toplevel(parent)
        self.window.title(f"{self.var_name.get()} — Wardrobe & Preferences ✨")
        self.window.geometry("590x710")
        self.window.resizable(False, False)
        self.window.attributes("-topmost", True)
        self.window.config(bg="#FAF7F2")

        self._center_window(590, 710)
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
        # 1. Header Card with Live Mochi Avatar Preview
        header_card = tk.Frame(
            self.window,
            bg="#FFFDF9",
            highlightbackground="#EFE5D8",
            highlightthickness=1,
            bd=0,
        )
        header_card.pack(fill=tk.X, padx=16, pady=(16, 12))

        # Live avatar preview canvas
        preview_container = tk.Frame(header_card, bg="#FFF5EB", highlightbackground="#F2DECA", highlightthickness=1, bd=0)
        preview_container.pack(side=tk.LEFT, padx=(12, 16), pady=12)

        self.preview_canvas = tk.Canvas(preview_container, width=96, height=96, bg="#FFF5EB", highlightthickness=0)
        self.preview_canvas.pack(padx=2, pady=2)
        self._redraw_avatar_preview()

        # Header Titles & Tags
        info_frame = tk.Frame(header_card, bg="#FFFDF9")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=12)

        title_row = tk.Frame(info_frame, bg="#FFFDF9")
        title_row.pack(anchor="w", fill=tk.X)

        self.lbl_header_name = tk.Label(
            title_row,
            text=f"🐾 {self.var_name.get()}",
            font=("Segoe UI", 17, "bold"),
            bg="#FFFDF9",
            fg="#1B2A4A",
        )
        self.lbl_header_name.pack(side=tk.LEFT)

        tag_badge = tk.Label(
            title_row,
            text="Cozy Companion",
            font=("Segoe UI", 8, "bold"),
            bg="#FFF0E0",
            fg="#D97706",
            padx=7,
            pady=1,
        )
        tag_badge.pack(side=tk.LEFT, padx=(8, 0))

        self.lbl_header_sub = tk.Label(
            info_frame,
            text="PREVIEW • Save & Apply updates Mochi",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFDF9",
            fg="#7C3AED",
        )
        self.lbl_header_sub.pack(anchor="w", pady=(3, 1))

        self.lbl_header_desc = tk.Label(
            info_frame,
            text="Floppy Bunny • Cream Yellow with Cozy Scarf",
            font=("Segoe UI", 8),
            bg="#FFFDF9",
            fg="#786C5E",
        )
        self.lbl_header_desc.pack(anchor="w")

        # 2. Styled Notebook for Contemporary Tabs
        style = ttk.Style(self.window)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TNotebook", background="#FAF7F2", borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background="#EFE8DE",
            foreground="#6B5E51",
            padding=[18, 9],
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#DE9B61")],
            foreground=[("selected", "#FFFFFF")],
        )
        style.configure("TFrame", background="#FAF7F2")

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        # Tab 1: Wardrobe & Outfits
        tab_wardrobe = ttk.Frame(self.notebook)
        self.notebook.add(tab_wardrobe, text="🎨 Wardrobe & Outfits")
        self._build_wardrobe_tab(tab_wardrobe)

        # Tab 2: Hotkeys & Search
        tab_hotkeys = ttk.Frame(self.notebook)
        self.notebook.add(tab_hotkeys, text="⌨️ Hotkeys & Search")
        self._build_hotkeys_tab(tab_hotkeys)

        # Tab 3: Habits & Focus (Default selected tab)
        tab_wellness = ttk.Frame(self.notebook)
        self.notebook.add(tab_wellness, text="⏳ Habits & Focus")
        self._build_wellness_tab(tab_wellness)
        self.notebook.select(2)

        # 3. Bottom Action Bar
        bottom_bar = tk.Frame(self.window, bg="#F5ECE1", height=56)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)

        lbl_hint = tk.Label(
            bottom_bar,
            text="✨ Changes sync live across desktop & tray",
            font=("Segoe UI", 8),
            bg="#F5ECE1",
            fg="#8C7E72",
        )
        lbl_hint.pack(side=tk.LEFT, padx=16, pady=12)

        btn_cancel = tk.Button(
            bottom_bar,
            text="Cancel",
            font=("Segoe UI", 9),
            bg="#FFFFFF",
            fg="#66584C",
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._on_close,
        )
        btn_cancel.pack(side=tk.RIGHT, padx=16, pady=10)

        btn_save = tk.Button(
            bottom_bar,
            text="Save & Apply ✦",
            font=("Segoe UI", 9, "bold"),
            bg="#FF7E67",
            activebackground="#FF6B8B",
            fg="#FFFFFF",
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
        acc = self.var_accessory.get()

        # Happy Golden Sparkles ✨
        c.create_text(16, 16, text="✨", fill="#FFD700", font=("Segoe UI", 10))
        c.create_text(82, 20, text="✦", fill="#FFD700", font=("Segoe UI", 8))

        # Floppy Ears with fuzzy natural shading
        c.create_polygon([24, 46, 20, 14, 32, 9, 39, 20, 36, 46], fill=color, outline="#4A3B32", width=2)
        c.create_polygon([72, 46, 69, 20, 76, 9, 88, 14, 84, 46], fill=color, outline="#4A3B32", width=2)
        c.create_polygon([25, 38, 23, 18, 30, 13, 35, 22], fill="#FCE4C8")
        c.create_polygon([73, 22, 78, 13, 85, 18, 83, 38], fill="#FCE4C8")

        # Chubby Bunny Body
        c.create_oval([14, 32, 90, 92], fill=color, outline="#4A3B32", width=2)
        # Soft Cream Belly
        c.create_oval([30, 56, 74, 88], fill="#FFFDF8", outline="")

        # Cute Little Paws
        c.create_oval([24, 84, 40, 92], fill=color, outline="#4A3B32", width=1.5)
        c.create_oval([64, 84, 80, 92], fill=color, outline="#4A3B32", width=1.5)

        # Sparkle Eyes
        c.create_oval([33, 49, 41, 59], fill="#1B1715")
        c.create_oval([35, 51, 38, 54], fill="#FFFFFF")
        c.create_oval([63, 49, 71, 59], fill="#1B1715")
        c.create_oval([65, 51, 68, 54], fill="#FFFFFF")

        # Nose & Smile
        c.create_polygon([52, 59, 56, 59, 54, 62], fill="#FF708F")
        c.create_arc([48, 61, 54, 67], start=0, extent=180, style=tk.ARC, outline="#4A3B32", width=1.8)
        c.create_arc([54, 61, 60, 67], start=0, extent=180, style=tk.ARC, outline="#4A3B32", width=1.8)

        # Cheerful Blush
        c.create_oval([24, 60, 32, 66], fill="#FFAAA6", outline="")
        c.create_oval([72, 60, 80, 66], fill="#FFAAA6", outline="")

        # Draw Selected Outfit / Accessory
        acc_lower = acc.lower()
        if "ribbon" in acc_lower:
            c.create_oval(18, 22, 30, 34, fill="#FF6B81", outline="#4A3B32", width=1.5)
            c.create_oval(30, 22, 42, 34, fill="#FF6B81", outline="#4A3B32", width=1.5)
            c.create_oval(26, 24, 34, 32, fill="#FF3366", outline="#4A3B32", width=1.5)
            c.create_line(28, 32, 22, 42, fill="#FF6B81", width=2)
            c.create_line(32, 32, 38, 42, fill="#FF6B81", width=2)
        elif "crown" in acc_lower:
            crown_pts = [38, 30, 34, 14, 46, 22, 54, 10, 62, 22, 74, 14, 70, 30]
            c.create_polygon(crown_pts, fill="#FFD700", outline="#B8860B", width=1.5)
            c.create_oval(52, 20, 56, 24, fill="#FF1744", outline="")
        elif "sakura" in acc_lower or "flower" in acc_lower:
            fx, fy = 28, 26
            for angle in [0, 72, 144, 216, 288]:
                rad = math.radians(angle)
                px = fx + math.cos(rad) * 6
                py = fy + math.sin(rad) * 6
                c.create_oval(px - 5, py - 5, px + 5, py + 5, fill="#FFB7C5", outline="#FF85A1", width=1)
            c.create_oval(fx - 3, fy - 3, fx + 3, fy + 3, fill="#FFE082", outline="")
        elif "glasses" in acc_lower:
            c.create_oval(28, 45, 47, 63, outline="#2C3E50", width=2)
            c.create_oval(57, 45, 76, 63, outline="#2C3E50", width=2)
            c.create_line(47, 54, 57, 54, fill="#2C3E50", width=2)
        elif "hat" in acc_lower:
            c.create_oval(34, 28, 74, 36, fill="#2B2B2B", outline="#1A1A1A", width=1.5)
            c.create_rectangle(42, 10, 66, 30, fill="#383838", outline="#1A1A1A", width=1.5)
            c.create_rectangle(42, 24, 66, 30, fill="#E74C3C", outline="")
        elif "scarf" in acc_lower:
            c.create_oval(26, 68, 78, 82, fill="#FF9AA2", outline="#E57373", width=1.5)
            c.create_rectangle(62, 74, 72, 90, fill="#FF9AA2", outline="#E57373", width=1.5)
            c.create_line(62, 88, 72, 88, fill="#B71C1C", width=1.5)

    def _build_wardrobe_tab(self, parent: ttk.Frame) -> None:
        container = tk.Frame(parent, bg="#FAF7F2")
        container.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        card = tk.Frame(container, bg="#FFFFFF", highlightbackground="#EDE4D8", highlightthickness=1, bd=0, padx=16, pady=12)
        card.pack(fill=tk.BOTH, expand=True)

        # 1. Name Input Box
        lbl_name = tk.Label(card, text="🐾 Companion Name:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_name.pack(anchor="w", pady=(0, 4))

        name_box = tk.Frame(card, bg="#FAF7F2", highlightbackground="#EDE4D8", highlightthickness=1, bd=0, padx=8, pady=3)
        name_box.pack(fill=tk.X, pady=(0, 10))

        ent_name = tk.Entry(
            name_box,
            textvariable=self.var_name,
            font=("Segoe UI", 10),
            bg="#FAF7F2",
            relief=tk.FLAT,
            bd=0,
        )
        ent_name.pack(fill=tk.X, expand=True)
        ent_name.bind("<KeyRelease>", lambda e: self.lbl_header_name.config(text=f"🐾 {self.var_name.get() or 'Mochi'}"))

        # 2. Outfits & Accessories Grid
        lbl_acc = tk.Label(card, text="👗 Outfits & Accessories:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_acc.pack(anchor="w", pady=(0, 4))

        acc_grid = tk.Frame(card, bg="#FFFFFF")
        acc_grid.pack(fill=tk.X, pady=(0, 10))

        self.accessory_cards.clear()
        curr_acc = self.var_accessory.get()

        for idx, (label, acc_id) in enumerate(ACCESSORY_OPTIONS):
            row = idx // 4
            col = idx % 4

            a_frame = tk.Frame(acc_grid, bg="#FAF7F2", highlightbackground="#EDE4D8", highlightthickness=1, bd=0, padx=6, pady=4, cursor="hand2")
            a_frame.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

            a_lbl = tk.Label(a_frame, text=label, font=("Segoe UI", 8), bg="#FAF7F2", fg="#2C3E50")
            a_lbl.pack(side=tk.LEFT)

            a_check = tk.Label(a_frame, text="✓" if acc_id == curr_acc else "", font=("Segoe UI", 8, "bold"), bg="#FAF7F2", fg="#FF7E67")
            a_check.pack(side=tk.RIGHT)

            self.accessory_cards[acc_id] = (a_frame, a_check)

            def make_acc_handler(a_target):
                return lambda e: self._select_accessory(a_target)

            h = make_acc_handler(acc_id)
            a_frame.bind("<Button-1>", h)
            a_lbl.bind("<Button-1>", h)
            a_check.bind("<Button-1>", h)

        for c in range(4):
            acc_grid.columnconfigure(c, weight=1)

        # 3. Modern Palette Swatch Cards
        lbl_colors = tk.Label(card, text="🎨 Skin Palette & Wardrobe Colors:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_colors.pack(anchor="w", pady=(0, 4))

        palette_grid = tk.Frame(card, bg="#FFFFFF")
        palette_grid.pack(fill=tk.X, pady=(0, 8))

        self.swatch_cards.clear()
        current_active = self.var_color.get().upper()

        for idx, (c_name, hex_code) in enumerate(PRESET_COLORS):
            row = idx // 4
            col = idx % 4

            frame = tk.Frame(palette_grid, bg="#FAF7F2", highlightbackground="#EDE4D8", highlightthickness=1, bd=0, padx=6, pady=4, cursor="hand2")
            frame.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

            c_preview = tk.Canvas(frame, width=16, height=16, bg="#FAF7F2", highlightthickness=0)
            c_preview.pack(side=tk.LEFT, padx=(0, 4))
            c_preview.create_oval(1, 1, 15, 15, fill=hex_code, outline="#999999", width=1)

            lbl_txt = tk.Label(frame, text=c_name, font=("Segoe UI", 8), bg="#FAF7F2", fg="#2C3E50")
            lbl_txt.pack(side=tk.LEFT)

            lbl_check = tk.Label(frame, text="✓" if hex_code.upper() == current_active else "", font=("Segoe UI", 8, "bold"), bg="#FAF7F2", fg="#FF7E67")
            lbl_check.pack(side=tk.RIGHT)

            self.swatch_cards[hex_code.upper()] = (frame, lbl_check, c_preview)

            def make_handler(h_code):
                return lambda e: self._select_swatch(h_code)

            handler = make_handler(hex_code)
            frame.bind("<Button-1>", handler)
            c_preview.bind("<Button-1>", handler)
            lbl_txt.bind("<Button-1>", handler)
            lbl_check.bind("<Button-1>", handler)

        for c in range(4):
            palette_grid.columnconfigure(c, weight=1)

        # Custom Color Picker Row
        custom_row = tk.Frame(card, bg="#FFFFFF")
        custom_row.pack(fill=tk.X, pady=(0, 10))

        btn_custom = tk.Button(
            custom_row,
            text="🌈 Custom Palette Color...",
            font=("Segoe UI", 8),
            bg="#FAF7F2",
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._pick_custom_color,
        )
        btn_custom.pack(side=tk.LEFT)

        self.lbl_custom_hex = tk.Label(custom_row, text=f"Selected: {self.var_color.get()}", font=("Segoe UI", 8), bg="#FFFFFF", fg="#7F8C8D")
        self.lbl_custom_hex.pack(side=tk.LEFT, padx=(8, 0))

        # 4. Size Scale Slider
        lbl_scale = tk.Label(card, text="Mochi Scale Size:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_scale.pack(anchor="w", pady=(0, 2))

        scale_row = tk.Frame(card, bg="#FFFFFF")
        scale_row.pack(fill=tk.X, pady=(0, 6))

        lbl_scale_val = tk.Label(scale_row, text=f"{int(self.var_scale.get()*100)}%", font=("Segoe UI", 9, "bold"), bg="#FFF2E5", fg="#D97706", padx=6, pady=2)
        lbl_scale_val.pack(side=tk.RIGHT)

        slider_scale = ttk.Scale(
            scale_row,
            from_=0.7,
            to=1.5,
            variable=self.var_scale,
            command=lambda v: lbl_scale_val.config(text=f"{int(float(v)*100)}%"),
        )
        slider_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        # 5. Auto-adapt Checkbox
        chk_auto = tk.Checkbutton(
            card,
            text="Auto-adapt color based on emotional states and bedtime",
            variable=self.var_auto_color,
            bg="#FFFFFF",
            font=("Segoe UI", 8),
            activebackground="#FFFFFF",
        )
        chk_auto.pack(anchor="w")

        self._refresh_swatch_highlights()
        self._refresh_accessory_highlights()

    def _select_swatch(self, hex_code: str) -> None:
        self.var_color.set(hex_code)
        if hasattr(self, "lbl_custom_hex") and self.lbl_custom_hex:
            self.lbl_custom_hex.config(text=f"Selected: {hex_code}")
        self._refresh_swatch_highlights()
        self._redraw_avatar_preview()

    def _select_accessory(self, acc_id: str) -> None:
        self.var_accessory.set(acc_id)
        self._refresh_accessory_highlights()
        self._redraw_avatar_preview()

    def _refresh_swatch_highlights(self) -> None:
        curr = self.var_color.get().upper()
        for hex_code, (frame, lbl_check, c_preview) in self.swatch_cards.items():
            if hex_code == curr:
                frame.config(bg="#FFF0E0", highlightbackground="#D97706", highlightthickness=1)
                lbl_check.config(text="✓", fg="#D97706", bg="#FFF0E0")
                c_preview.config(bg="#FFF0E0")
            else:
                frame.config(bg="#FAF7F2", highlightbackground="#EDE4D8", highlightthickness=1)
                lbl_check.config(text="", fg="#FAF7F2", bg="#FAF7F2")
                c_preview.config(bg="#FAF7F2")

    def _refresh_accessory_highlights(self) -> None:
        curr = self.var_accessory.get()
        for acc_id, (frame, lbl_check) in self.accessory_cards.items():
            if acc_id == curr:
                frame.config(bg="#FFF0E0", highlightbackground="#D97706", highlightthickness=1)
                lbl_check.config(text="✓", fg="#D97706", bg="#FFF0E0")
            else:
                frame.config(bg="#FAF7F2", highlightbackground="#EDE4D8", highlightthickness=1)
                lbl_check.config(text="", fg="#FAF7F2", bg="#FAF7F2")

    def _pick_custom_color(self) -> None:
        color = colorchooser.askcolor(initialcolor=self.var_color.get(), title="Select Custom Wardrobe Color", parent=self.window)
        if color and color[1]:
            self._select_swatch(color[1])

    def _build_hotkeys_tab(self, parent: ttk.Frame) -> None:
        container = tk.Frame(parent, bg="#FAF7F2")
        container.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        card = tk.Frame(container, bg="#FFFFFF", highlightbackground="#EDE4D8", highlightthickness=1, bd=0, padx=16, pady=14)
        card.pack(fill=tk.BOTH, expand=True)

        lbl_hk_title = tk.Label(
            card,
            text="Summon / Dismiss Hotkey:",
            font=("Segoe UI", 10, "bold"),
            bg="#FFFFFF",
            fg="#2C3E50",
        )
        lbl_hk_title.pack(anchor="w", pady=(0, 4))

        lbl_hk_desc = tk.Label(
            card,
            text="Choose any hotkey combination to toggle Mochi on/off the screen anytime:",
            font=("Segoe UI", 8),
            bg="#FFFFFF",
            fg="#7F8C8D",
        )
        lbl_hk_desc.pack(anchor="w", pady=(0, 8))

        # Keycap visual pill display
        pill_frame = tk.Frame(card, bg="#FAF7F2", highlightbackground="#EDE4D8", highlightthickness=1, bd=0, padx=14, pady=8)
        pill_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_hotkey_caps = tk.Label(
            pill_frame,
            text=self._format_keycap_display(self.var_hotkey.get()),
            font=("Segoe UI", 12, "bold"),
            bg="#FAF7F2",
            fg="#2C3E50",
        )
        self.lbl_hotkey_caps.pack(side=tk.LEFT)

        self.btn_record = tk.Button(
            pill_frame,
            text="Record Keys ⏺️",
            font=("Segoe UI", 9, "bold"),
            bg="#FFB6C1",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._start_recording_hotkey,
        )
        self.btn_record.pack(side=tk.RIGHT)

        # Quick Popular Presets
        lbl_presets = tk.Label(card, text="Or Pick a Popular Preset Combination:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_presets.pack(anchor="w", pady=(0, 6))

        preset_row = tk.Frame(card, bg="#FFFFFF")
        preset_row.pack(fill=tk.X, pady=(0, 12))

        presets = [
            ("Alt + Q", "alt+q"),
            ("Ctrl + Space", "ctrl+space"),
            ("Ctrl + Shift + B", "ctrl+shift+b"),
            ("Ctrl + Q", "ctrl+q"),
            ("F8", "f8"),
            ("Win + Z", "win+z"),
        ]
        for label, hk in presets:
            btn = tk.Button(
                preset_row,
                text=label,
                font=("Segoe UI", 8),
                bg="#FAF7F2",
                relief=tk.FLAT,
                padx=8,
                pady=3,
                cursor="hand2",
                command=lambda k=hk: self._set_hotkey(k),
            )
            btn.pack(side=tk.LEFT, padx=3)

        # Direct Manual Entry Box
        lbl_direct = tk.Label(card, text="Direct Hotkey String:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2C3E50")
        lbl_direct.pack(anchor="w", pady=(0, 4))

        ent_hk = tk.Entry(
            card,
            textvariable=self.var_hotkey,
            font=("Segoe UI", 10),
            bg="#FAF7F2",
            relief=tk.FLAT,
            highlightbackground="#EDE4D8",
            highlightthickness=1,
            bd=0,
        )
        ent_hk.pack(fill=tk.X, pady=(0, 12))
        ent_hk.bind("<KeyRelease>", lambda e: self.lbl_hotkey_caps.config(text=self._format_keycap_display(self.var_hotkey.get())))

        # Windows Search Integration Callout Card
        search_card = tk.Frame(card, bg="#FFF8F0", highlightbackground="#FEE2C5", highlightthickness=1, bd=0, padx=12, pady=10)
        search_card.pack(fill=tk.X)

        lbl_search_info = tk.Label(
            search_card,
            text=(
                "🔍 Windows Search Bar Integration:\n"
                f"• Renaming your pet automatically updates the Windows Start Menu\n"
                f"  shortcut name so searching '{self.var_name.get()}' in Windows finds it immediately!\n"
                f"• Clicking the search result or pressing your hotkey opens/closes Mochi."
            ),
            font=("Segoe UI", 9),
            bg="#FFF8F0",
            fg="#9A3412",
            justify=tk.LEFT,
        )
        lbl_search_info.pack(anchor="w")

    def _build_wellness_tab(self, parent: ttk.Frame) -> None:
        """Card-based presentation for Habits, Corner Docking, and Focus."""
        container = tk.Frame(parent, bg="#FAF7F2")
        container.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Card 1: Taskbar Corner Roosting
        card_dock = tk.Frame(container, bg="#FFFFFF", highlightbackground="#EDE4D8", highlightthickness=1, bd=0, padx=16, pady=12)
        card_dock.pack(fill=tk.X, pady=(0, 8))

        dock_head = tk.Frame(card_dock, bg="#FFFFFF")
        dock_head.pack(fill=tk.X, pady=(0, 2))

        lbl_dock_title = tk.Label(
            dock_head,
            text="📍 Taskbar Corner Roosting (Inactivity Delay)",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#2C3E50",
        )
        lbl_dock_title.pack(side=tk.LEFT)

        self.lbl_dock_val = tk.Label(
            dock_head,
            text=f"{self.var_dock_delay.get()} sec",
            font=("Segoe UI", 8, "bold"),
            bg="#FFF2E5",
            fg="#D97706",
            padx=8,
            pady=2,
        )
        self.lbl_dock_val.pack(side=tk.RIGHT)

        lbl_dock_sub = tk.Label(
            card_dock,
            text="When working, Mochi smoothly loaves in the bottom-right corner above your clock.",
            font=("Segoe UI", 8),
            bg="#FFFFFF",
            fg="#7F8C8D",
        )
        lbl_dock_sub.pack(anchor="w", pady=(0, 6))

        slider_dock = ttk.Scale(
            card_dock,
            from_=5,
            to=60,
            variable=self.var_dock_delay,
            command=self._on_dock_slider,
        )
        slider_dock.pack(fill=tk.X, pady=(0, 8))

        # Capsule Buttons for corner delay
        chips_dock = tk.Frame(card_dock, bg="#FFFFFF")
        chips_dock.pack(fill=tk.X)
        self.dock_chips.clear()
        for label, val in [("5s (Quick)", 5), ("15s (Standard)", 15), ("30s (Cozy)", 30), ("60s (Slow)", 60)]:
            btn = tk.Button(
                chips_dock,
                text=label,
                font=("Segoe UI", 8),
                bg="#FAF7F2",
                fg="#554A40",
                relief=tk.FLAT,
                padx=10,
                pady=3,
                cursor="hand2",
                command=lambda v=val: self._select_dock_chip(v),
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.dock_chips[val] = btn
        self._refresh_dock_chips()

        # Card 2: Pomodoro Focus Timer
        card_pomo = tk.Frame(container, bg="#FFFFFF", highlightbackground="#EDE4D8", highlightthickness=1, bd=0, padx=16, pady=12)
        card_pomo.pack(fill=tk.X, pady=(0, 8))

        pomo_head = tk.Frame(card_pomo, bg="#FFFFFF")
        pomo_head.pack(fill=tk.X, pady=(0, 2))

        lbl_pomo_title = tk.Label(
            pomo_head,
            text="🎓 Pomodoro Study & Focus Timer",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#2C3E50",
        )
        lbl_pomo_title.pack(side=tk.LEFT)

        self.lbl_pomo_val = tk.Label(
            pomo_head,
            text=f"{self.var_focus_work.get()} min work",
            font=("Segoe UI", 8, "bold"),
            bg="#FFF2E5",
            fg="#D97706",
            padx=8,
            pady=2,
        )
        self.lbl_pomo_val.pack(side=tk.RIGHT)

        lbl_pomo_sub = tk.Label(
            card_pomo,
            text="Mochi wears study glasses and quietly accompanies your deep work sprints.",
            font=("Segoe UI", 8),
            bg="#FFFFFF",
            fg="#7F8C8D",
        )
        lbl_pomo_sub.pack(anchor="w", pady=(0, 6))

        slider_pomo = ttk.Scale(
            card_pomo,
            from_=15,
            to=60,
            variable=self.var_focus_work,
            command=self._on_pomo_slider,
        )
        slider_pomo.pack(fill=tk.X, pady=(0, 8))

        # Capsule Buttons for Pomodoro
        chips_pomo = tk.Frame(card_pomo, bg="#FFFFFF")
        chips_pomo.pack(fill=tk.X)
        self.pomo_chips.clear()
        for label, val in [("15 min", 15), ("25 min (Standard)", 25), ("45 min", 45), ("60 min", 60)]:
            btn = tk.Button(
                chips_pomo,
                text=label,
                font=("Segoe UI", 8),
                bg="#FAF7F2",
                fg="#554A40",
                relief=tk.FLAT,
                padx=10,
                pady=3,
                cursor="hand2",
                command=lambda v=val: self._select_pomo_chip(v),
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.pomo_chips[val] = btn
        self._refresh_pomo_chips()

        # Card 3: Circadian Day / Night Schedule
        card_sleep = tk.Frame(container, bg="#FFFFFF", highlightbackground="#EDE4D8", highlightthickness=1, bd=0, padx=16, pady=12)
        card_sleep.pack(fill=tk.X, pady=(0, 8))

        lbl_sleep_title = tk.Label(
            card_sleep,
            text="🌙 Circadian Sleep & Wake Rhythm",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#2C3E50",
        )
        lbl_sleep_title.pack(anchor="w")

        lbl_sleep_sub = tk.Label(
            card_sleep,
            text="Mochi gets sleepy and tucks into a bedtime loaf at night, waking up refreshed with you.",
            font=("Segoe UI", 8),
            bg="#FFFFFF",
            fg="#7F8C8D",
        )
        lbl_sleep_sub.pack(anchor="w", pady=(1, 6))

        sleep_row = tk.Frame(card_sleep, bg="#FFFFFF")
        sleep_row.pack(fill=tk.X)

        # Bedtime pill
        bed_frame = tk.Frame(sleep_row, bg="#FAF7F2", highlightbackground="#EADFCF", highlightthickness=1, bd=0, padx=10, pady=4)
        bed_frame.pack(side=tk.LEFT, padx=(0, 16))
        tk.Label(bed_frame, text="Bedtime:", font=("Segoe UI", 8, "bold"), bg="#FAF7F2", fg="#2C3E50").pack(side=tk.LEFT, padx=(0, 6))
        tk.Spinbox(bed_frame, from_=0, to=23, width=3, textvariable=self.var_bedtime, font=("Segoe UI", 9, "bold"), bd=0, bg="#FAF7F2").pack(side=tk.LEFT)
        tk.Label(bed_frame, text=":00 hrs", font=("Segoe UI", 8), bg="#FAF7F2", fg="#7F8C8D").pack(side=tk.LEFT, padx=(4, 0))

        # Wake pill
        wake_frame = tk.Frame(sleep_row, bg="#FAF7F2", highlightbackground="#EADFCF", highlightthickness=1, bd=0, padx=10, pady=4)
        wake_frame.pack(side=tk.LEFT)
        tk.Label(wake_frame, text="Wake Time:", font=("Segoe UI", 8, "bold"), bg="#FAF7F2", fg="#2C3E50").pack(side=tk.LEFT, padx=(0, 6))
        tk.Spinbox(wake_frame, from_=0, to=23, width=3, textvariable=self.var_wake, font=("Segoe UI", 9, "bold"), bd=0, bg="#FAF7F2").pack(side=tk.LEFT)
        tk.Label(wake_frame, text=":00 hrs", font=("Segoe UI", 8), bg="#FAF7F2", fg="#7F8C8D").pack(side=tk.LEFT, padx=(4, 0))

        # Card 4: Wellness Reminders Checkbox
        card_wellness = tk.Frame(container, bg="#FFFFFF", highlightbackground="#EDE4D8", highlightthickness=1, bd=0, padx=16, pady=10)
        card_wellness.pack(fill=tk.X)

        chk_wellness = tk.Checkbutton(
            card_wellness,
            text="Enable gentle wellness speech bubbles",
            variable=self.var_wellness_enabled,
            bg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            activebackground="#FFFFFF",
        )
        chk_wellness.pack(anchor="w")

        lbl_wellness_sub = tk.Label(
            card_wellness,
            text="💧 Hydration   •   👁️ 20-20-20 Eye Rests   •   🧘 Posture Check",
            font=("Segoe UI", 8),
            bg="#FFFFFF",
            fg="#7F8C8D",
        )
        lbl_wellness_sub.pack(anchor="w", padx=(24, 0), pady=(1, 0))

    def _select_dock_chip(self, val: int) -> None:
        self.var_dock_delay.set(val)
        self.lbl_dock_val.config(text=f"{val} sec")
        self._refresh_dock_chips()

    def _on_dock_slider(self, val) -> None:
        int_val = int(float(val))
        self.lbl_dock_val.config(text=f"{int_val} sec")
        self._refresh_dock_chips()

    def _refresh_dock_chips(self) -> None:
        curr = int(self.var_dock_delay.get())
        for val, btn in self.dock_chips.items():
            if val == curr:
                btn.config(bg="#FF9F68", fg="#FFFFFF", font=("Segoe UI", 8, "bold"))
            else:
                btn.config(bg="#FAF7F2", fg="#554A40", font=("Segoe UI", 8))

    def _select_pomo_chip(self, val: int) -> None:
        self.var_focus_work.set(val)
        self.lbl_pomo_val.config(text=f"{val} min work")
        self._refresh_pomo_chips()

    def _on_pomo_slider(self, val) -> None:
        int_val = int(float(val))
        self.lbl_pomo_val.config(text=f"{int_val} min work")
        self._refresh_pomo_chips()

    def _refresh_pomo_chips(self) -> None:
        curr = int(self.var_focus_work.get())
        for val, btn in self.pomo_chips.items():
            if val == curr:
                btn.config(bg="#FF9F68", fg="#FFFFFF", font=("Segoe UI", 8, "bold"))
            else:
                btn.config(bg="#FAF7F2", fg="#554A40", font=("Segoe UI", 8))

    def _format_keycap_display(self, hk_str: str) -> str:
        parts = [p.capitalize() for p in hk_str.replace("+", " ").split() if p.strip()]
        return " + ".join(f"[{p}]" for p in parts) if parts else "[None]"

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
        has_win = (state & 0x0040) != 0 or key_sym in ("super_l", "super_r", "win_l", "win_r")

        if key_sym in ("control_l", "control_r", "shift_l", "shift_r", "alt_l", "alt_r", "super_l", "super_r", "caps_lock"):
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
        if has_win:
            parts.append("win")

        if not parts and not (key_name.startswith("f") and key_name[1:].isdigit()):
            parts.append("ctrl")

        parts.append(key_name)
        new_hk = "+".join(parts)
        self._set_hotkey(new_hk)
        self._stop_recording_hotkey()

    def _set_hotkey(self, hk_str: str) -> None:
        self.var_hotkey.set(hk_str.lower())
        self.lbl_hotkey_caps.config(text=self._format_keycap_display(hk_str), fg="#2C3E50")

    def _stop_recording_hotkey(self) -> None:
        self.is_recording_hotkey = False
        self.btn_record.config(text="Record Keys ⏺️", bg="#FFB6C1")
        try:
            self.window.unbind("<Key>")
        except Exception:
            pass

    def _save_and_apply(self) -> None:
        updated = copy.deepcopy(self.config_data)

        new_name = self.var_name.get().strip() or "Mochi"
        updated["pet_name"] = new_name
        updated["base_color"] = self.var_color.get()
        updated["accessory"] = self.var_accessory.get()
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
