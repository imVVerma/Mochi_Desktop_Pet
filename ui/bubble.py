import tkinter as tk
from typing import Optional


class SpeechBubble:
    """Procedural speech bubble that renders above the pet on the canvas with auto-fade."""

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

    def draw(self, canvas: tk.Canvas, pet_cx: float, pet_top_y: float) -> None:
        if not self.is_active or not self.text:
            return

        # Word wrap text manually if needed
        words = self.text.split(" ")
        lines = []
        cur_line = []
        for word in words:
            cur_line.append(word)
            if len(" ".join(cur_line)) > 18:
                lines.append(" ".join(cur_line))
                cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))

        display_text = "\n".join(lines)
        line_count = len(lines)

        # Bubble geometry
        bubble_w = max(100, min(130, max(len(l) for l in lines) * 7 + 16))
        bubble_h = line_count * 14 + 12

        bx = pet_cx
        by = max(bubble_h / 2 + 4, pet_top_y - bubble_h / 2 - 8)

        left = bx - bubble_w / 2
        right = bx + bubble_w / 2
        top = by - bubble_h / 2
        bottom = by + bubble_h / 2

        # Draw rounded rectangle bubble background
        r = 6
        points = [
            left + r, top,
            right - r, top,
            right, top + r,
            right, bottom - r,
            right - r, bottom,
            bx + 4, bottom,
            bx, pet_top_y - 2,  # Tail pointing down to pet
            bx - 4, bottom,
            left + r, bottom,
            left, bottom - r,
            left, top + r,
        ]

        canvas.create_polygon(
            points,
            smooth=True,
            fill="#FFFFFF",
            outline="#44444A",
            width=2,
            tags="bubble"
        )

        # Draw text inside bubble
        canvas.create_text(
            bx,
            by - 1,
            text=display_text,
            fill="#1E1E24",
            font=("Segoe UI", 8, "bold"),
            justify=tk.CENTER,
            tags="bubble"
        )
