import tkinter as tk
from typing import Optional


class SpeechBubble:
    """Procedural speech bubble that renders above the pet on the canvas with auto-fade and bounds clamping."""

    def __init__(self):
        self.text: str = ""
        self.is_active: bool = False
        self.ticks_remaining: int = 0
        self.max_ticks: int = 80

    def show(self, text: str, duration_seconds: float = 4.0) -> None:
        self.text = text
        self.is_active = True
        self.max_ticks = int(duration_seconds * 20)  # ~20 ticks/sec
        self.ticks_remaining = self.max_ticks

    def dismiss(self) -> None:
        self.is_active = False
        self.ticks_remaining = 0

    def tick(self) -> None:
        if self.is_active:
            self.ticks_remaining -= 1
            if self.ticks_remaining <= 0:
                self.is_active = False

    def draw(
        self,
        canvas: tk.Canvas,
        pet_cx: float,
        pet_top_y: float,
        canvas_width: float = 140.0,
        canvas_height: float = 140.0,
    ) -> None:
        if not self.is_active or not self.text:
            return

        # Word wrap text manually if needed
        words = self.text.split(" ")
        lines = []
        cur_line = []
        for word in words:
            cur_line.append(word)
            if len(" ".join(cur_line)) > 16:
                lines.append(" ".join(cur_line))
                cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))

        display_text = "\n".join(lines)
        line_count = len(lines)

        s = max(0.5, min(canvas_width / 140.0, canvas_height / 140.0))

        # Bubble geometry scaled and bounded within canvas borders
        bubble_w = min(canvas_width - 8.0, max(75.0 * s, max(len(l) for l in lines) * (6.5 * s) + 14.0 * s))
        bubble_h = max(18.0 * s, line_count * (12.0 * s) + 8.0 * s)

        bx = max(bubble_w / 2.0 + 4.0, min(canvas_width - bubble_w / 2.0 - 4.0, pet_cx))
        # Place bubble above pet, but clamped so it NEVER exits canvas top
        by = max(bubble_h / 2.0 + 3.0, min(pet_top_y - bubble_h / 2.0 - 4.0 * s, canvas_height - bubble_h / 2.0 - 3.0))

        left = bx - bubble_w / 2.0
        right = bx + bubble_w / 2.0
        top = by - bubble_h / 2.0
        bottom = by + bubble_h / 2.0

        # Draw rounded rectangle bubble background
        r = max(3.0, 5.0 * s)
        tail_tip_y = min(canvas_height - 2.0, max(bottom, pet_top_y - 2.0 * s))
        points = [
            left + r, top,
            right - r, top,
            right, top + r,
            right, bottom - r,
            right - r, bottom,
            bx + 4.0 * s, bottom,
            bx, tail_tip_y,  # Tail pointing down to pet
            bx - 4.0 * s, bottom,
            left + r, bottom,
            left, bottom - r,
            left, top + r,
        ]

        canvas.create_polygon(
            points,
            smooth=True,
            fill="#FFFFFF",
            outline="#44444A",
            width=max(1, int(1.5 * s)),
            tags="bubble"
        )

        font_size = max(6, int(8.0 * s))
        # Draw text inside bubble
        canvas.create_text(
            bx,
            by - 1,
            text=display_text,
            fill="#1E1E24",
            font=("Segoe UI", font_size, "bold"),
            justify=tk.CENTER,
            tags="bubble"
        )
