import math
import random
import tkinter as tk
from typing import Dict, List, Tuple
from core.fsm import State
from core.stats import PetStats
from ui.bubble import SpeechBubble

# Dark stroke color that appears black to the user but does NOT match the transparent color key (#000001)
OUTLINE_COLOR = "#222228"
PUPIL_COLOR = "#18181D"
BLUSH_COLOR = "#FFB6C1"
INNER_EAR_COLOR = "#FFD1DC"
BELLY_COLOR = "#FFF9F2"
NOSE_COLOR = "#FF7597"


class CanvasRenderer:
    """Procedural vector graphics renderer for Floppy Bunny Desktop Pet on Tkinter Canvas."""

    def __init__(self, canvas: tk.Canvas, width: int = 140, height: int = 140):
        self.canvas = canvas
        self.width = width
        self.height = height

        self.color_hue: float = 0.5
        self.anim_tick: int = 0
        self.blink_timer: int = 0
        self.is_blinking: bool = False
        self.is_sleeping: bool = False
        self.particles: List[Dict] = []
        self.speech_bubble = SpeechBubble()

        # Dynamic ear physics state
        self.ear_flop_l: float = -14.0
        self.ear_flop_r: float = 14.0

        # Codex-style organic kinematics: corner loafing and curious head tilt
        self.loaf_factor: float = 0.0
        self.head_tilt_x: float = 0.0

    def get_color(self, state: State, stats: PetStats, auto_color: bool = True, base_color: str = "#FFB6C1") -> str:
        """Calculates dynamic body color responding to emotion and circadian rhythm."""
        if not auto_color:
            return base_color

        if state == State.SLEEPING:
            return "#B4C5CF"  # Muted dreamy periwinkle/slate
        elif state == State.FOCUS:
            return "#C7E9C0"  # Calming mint sage for study
        elif state == State.EXCITED:
            return "#FFB7B2"  # Energetic blossom pink
        elif state == State.TIRED:
            return "#C2D4E5"  # Soft sleepy lavender-blue
        elif state == State.DANCING:
            return "#FF9AA2"  # Vibrant happy rose

        # Smooth rainbow pastel cycle during normal wakefulness
        r = int(220 + 30 * math.sin(self.color_hue))
        g = int(210 + 35 * math.sin(self.color_hue + 2.094))
        b = int(230 + 25 * math.cos(self.color_hue))
        return f"#{r:02x}{g:02x}{b:02x}"

    def spawn_particle(self, text: str, color: str, size: int = 12, lifetime: int = 24) -> None:
        self.particles.append({
            "x": self.width / 2 + random.uniform(-25, 25),
            "y": 38.0,
            "vx": random.uniform(-0.5, 0.5),
            "vy": random.uniform(-1.8, -1.0),
            "text": text,
            "color": color,
            "size": size,
            "life": lifetime,
        })

    def update_particles(self) -> None:
        """Animates and reaps active particles."""
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw(
        self,
        state: State,
        stats: PetStats,
        offset_y: float = 0.0,
        stretch_x: float = 0.0,
        mouse_rel_x: float = 0.0,
        mouse_rel_y: float = 0.0,
        velocity_speed: float = 0.0,
        auto_color: bool = True,
        base_color: str = "#FFB6C1",
        is_docked: bool = False,
        accessory: str = "None",
    ) -> None:
        """Draws procedural Floppy Bunny body, ears, tail, paws, anime facial features, and speech bubble."""
        self.canvas.delete("all")
        self.anim_tick += 1
        self.color_hue += 0.015
        self.update_particles()
        self.speech_bubble.tick()

        # State flags
        is_sleeping = (state == State.SLEEPING)
        is_tired = (state == State.TIRED)
        is_moving = (state in [State.WANDERING, State.RETURNING_HOME])
        self.is_sleeping = is_sleeping

        # Blinking logic
        self.blink_timer += 1
        if self.blink_timer > 85 and not self.is_blinking:
            if random.random() < 0.09:
                self.is_blinking = True
                self.blink_timer = 0
        elif self.is_blinking and self.blink_timer > 3:
            self.is_blinking = False
            self.blink_timer = 0

        # Codex-style organic kinematics: smooth loafing when docked in home corner
        is_loafing = (is_docked and not is_moving and not is_sleeping and state != State.DRAGGED)
        target_loaf = 1.0 if is_loafing else 0.0
        self.loaf_factor += (target_loaf - self.loaf_factor) * 0.12

        # Idle procedural breathing loop (continuous gentle inhalation / exhalation)
        breath_speed = 0.045 if is_sleeping else 0.085
        breath_amp = 1.8 if is_sleeping else 1.2
        breath_offset = math.sin(self.anim_tick * breath_speed) * breath_amp

        # Body center and radii with squash & stretch, breathing, and corner loaf compression
        cx = self.width / 2
        cy = self.height / 2 + offset_y + 14 - (breath_offset * 0.5) + (self.loaf_factor * 2.5)
        rx = max(28.0, 42 + stretch_x - (breath_offset * 0.4) + (self.loaf_factor * 3.5))
        ry = max(24.0, 40 - stretch_x * 0.5 + breath_offset - (self.loaf_factor * 2.5))

        body_color = self.get_color(state, stats, auto_color, base_color)

        # -------------------------------------------------------------------------
        # 1. Fluffy Bunny Puffball Tail (Drawn behind body)
        # -------------------------------------------------------------------------
        tail_dir = -1 if mouse_rel_x >= 0 else 1
        tail_wag = math.sin(self.anim_tick * 0.28) * (3.0 if not is_sleeping else 0.5)
        tail_cx = cx + tail_dir * (rx * 0.82)
        tail_cy = cy + ry * 0.32 + tail_wag
        tail_r = 13.0

        self.canvas.create_oval(
            tail_cx - tail_r, tail_cy - tail_r,
            tail_cx + tail_r, tail_cy + tail_r,
            fill="#FFFFFF",
            outline=OUTLINE_COLOR,
            width=2,
            tags="tail"
        )
        self.canvas.create_oval(
            tail_cx - tail_r * 0.5, tail_cy - tail_r * 0.5,
            tail_cx + tail_r * 0.5, tail_cy + tail_r * 0.5,
            fill="#FFFBF7",
            outline="",
            tags="tail"
        )

        # -------------------------------------------------------------------------
        # 2. Long Floppy Bunny Ears with Kinematic Flop Physics & Micro-Flutter
        # -------------------------------------------------------------------------
        if is_sleeping or is_tired:
            target_flop_l = -58.0  # Drooped down along cheeks
            target_flop_r = 58.0
        elif state in [State.EXCITED, State.DANCING]:
            target_flop_l = -5.0 + math.sin(self.anim_tick * 0.5) * 6  # Perked straight up & twitchy
            target_flop_r = 5.0 - math.sin(self.anim_tick * 0.5) * 6
        elif state == State.FALLING or velocity_speed > 6.0:
            target_flop_l = -35.0  # Streamed back by air drag
            target_flop_r = 35.0
        else:
            # Gentle relaxed flop sway with organic tip micro-flutter
            ear_sway = math.sin(self.anim_tick * 0.12) * 3.5 + math.sin(self.anim_tick * 0.24) * 1.0
            loaf_ear_drape = self.loaf_factor * 16.0
            target_flop_l = -16.0 - loaf_ear_drape + ear_sway
            target_flop_r = 16.0 + loaf_ear_drape - ear_sway

        # Smooth interpolation of ear angles
        self.ear_flop_l += (target_flop_l - self.ear_flop_l) * 0.25
        self.ear_flop_r += (target_flop_r - self.ear_flop_r) * 0.25

        ear_len = 50.0
        ear_head_y = cy - ry * 0.72

        def draw_ear(base_x: float, base_y: float, angle_deg: float, ear_sign: float):
            rad = math.radians(angle_deg)
            tip_x = base_x + math.sin(rad) * ear_len
            tip_y = base_y - math.cos(rad) * ear_len

            mid_rad = math.radians(angle_deg * 0.7)
            mid_x = base_x + math.sin(mid_rad) * (ear_len * 0.55) + (ear_sign * 9.0)
            mid_y = base_y - math.cos(mid_rad) * (ear_len * 0.55)

            points = [
                base_x - 7, base_y,
                base_x - 10, base_y - 12,
                mid_x - 8 * ear_sign, mid_y,
                tip_x, tip_y,
                mid_x + 8 * ear_sign, mid_y,
                base_x + 7, base_y
            ]
            self.canvas.create_polygon(points, smooth=True, fill=body_color, outline=OUTLINE_COLOR, width=2, tags="ear")

            inner_points = [
                base_x - 3, base_y - 4,
                base_x - 5, base_y - 14,
                mid_x - 4 * ear_sign, mid_y,
                tip_x * 0.92 + base_x * 0.08, tip_y * 0.92 + base_y * 0.08,
                mid_x + 4 * ear_sign, mid_y,
                base_x + 3, base_y - 4
            ]
            self.canvas.create_polygon(inner_points, smooth=True, fill=INNER_EAR_COLOR, outline="", tags="ear")

        # Draw left and right ears
        draw_ear(cx - 16, ear_head_y, self.ear_flop_l, ear_sign=-1.0)
        draw_ear(cx + 16, ear_head_y, self.ear_flop_r, ear_sign=1.0)

        # -------------------------------------------------------------------------
        # 3. Main Chubby Bunny Body
        # -------------------------------------------------------------------------
        self.canvas.create_oval(
            cx - rx, cy - ry,
            cx + rx, cy + ry,
            fill=body_color,
            outline=OUTLINE_COLOR,
            width=2.5,
            tags="body"
        )

        # -------------------------------------------------------------------------
        # 4. Soft Creamy Belly Patch (Adds 3D dimensional cuteness)
        # -------------------------------------------------------------------------
        belly_rx = rx * 0.54
        belly_ry = ry * 0.52
        belly_cy = cy + ry * 0.28
        self.canvas.create_oval(
            cx - belly_rx, belly_cy - belly_ry,
            cx + belly_rx, belly_cy + belly_ry,
            fill=BELLY_COLOR,
            outline="",
            tags="belly"
        )

        # -------------------------------------------------------------------------
        # 5. Little Bunny Paws / Feet (Stepping walk, tucks into loaf in corner)
        # -------------------------------------------------------------------------
        if not is_sleeping:
            step_phase = math.sin(self.anim_tick * 0.45) * 4.0 if is_moving else 0.0
            left_foot_y = cy + ry - 4 + step_phase
            right_foot_y = cy + ry - 4 - step_phase
            foot_w = max(9.0, 13.0 - self.loaf_factor * 3.5)
            foot_h = max(5.0, 8.0 - self.loaf_factor * 2.5)
            foot_spacing = 24.0 - self.loaf_factor * 10.0

            # Left Foot
            self.canvas.create_oval(
                cx - foot_spacing - foot_w, left_foot_y - foot_h,
                cx - foot_spacing + foot_w, left_foot_y + foot_h,
                fill=body_color, outline=OUTLINE_COLOR, width=2, tags="foot"
            )
            # Right Foot
            self.canvas.create_oval(
                cx + foot_spacing - foot_w, right_foot_y - foot_h,
                cx + foot_spacing + foot_w, right_foot_y + foot_h,
                fill=body_color, outline=OUTLINE_COLOR, width=2, tags="foot"
            )
            # Cute little toe lines (fade slightly in loaf)
            if self.loaf_factor < 0.8:
                self.canvas.create_line(cx - foot_spacing, left_foot_y + 2, cx - foot_spacing, left_foot_y + foot_h, fill=OUTLINE_COLOR, width=1.5)
                self.canvas.create_line(cx + foot_spacing, right_foot_y + 2, cx + foot_spacing, right_foot_y + foot_h, fill=OUTLINE_COLOR, width=1.5)

        # -------------------------------------------------------------------------
        # 6. Cursor Curiosity & Head Tilt (Face subtly turns towards nearby cursor)
        # -------------------------------------------------------------------------
        dist = math.hypot(mouse_rel_x, mouse_rel_y) or 1.0
        target_tilt = (mouse_rel_x / dist) * min(3.5, dist * 0.035) if (not is_sleeping and dist < 180.0) else 0.0
        self.head_tilt_x += (target_tilt - self.head_tilt_x) * 0.15
        face_cx = cx + self.head_tilt_x

        # -------------------------------------------------------------------------
        # 7. Rosy Cheek Blush (Breathing pulse)
        # -------------------------------------------------------------------------
        if not is_sleeping:
            blush_rx = 9.0 + breath_offset * 0.3
            blush_ry = 5.0
            self.canvas.create_oval(face_cx - rx * 0.68 - blush_rx, cy + 3 - blush_ry, face_cx - rx * 0.68 + blush_rx, cy + 3 + blush_ry, fill=BLUSH_COLOR, outline="")
            self.canvas.create_oval(face_cx + rx * 0.68 - blush_rx, cy + 3 - blush_ry, face_cx + rx * 0.68 + blush_rx, cy + 3 + blush_ry, fill=BLUSH_COLOR, outline="")

        # -------------------------------------------------------------------------
        # 8. Delicate Bunny Whiskers
        # -------------------------------------------------------------------------
        whisker_wiggle = math.sin(self.anim_tick * 0.3) * 1.5 if not is_sleeping else 0.0
        # Left Whiskers
        self.canvas.create_line(face_cx - 20, cy + 3, face_cx - 38, cy + 1 + whisker_wiggle, fill=OUTLINE_COLOR, width=1.5)
        self.canvas.create_line(face_cx - 20, cy + 7, face_cx - 36, cy + 9 - whisker_wiggle, fill=OUTLINE_COLOR, width=1.5)
        # Right Whiskers
        self.canvas.create_line(face_cx + 20, cy + 3, face_cx + 38, cy + 1 + whisker_wiggle, fill=OUTLINE_COLOR, width=1.5)
        self.canvas.create_line(face_cx + 20, cy + 7, face_cx + 36, cy + 9 - whisker_wiggle, fill=OUTLINE_COLOR, width=1.5)

        # -------------------------------------------------------------------------
        # 9. Dynamic Mouse Pupil Tracking
        # -------------------------------------------------------------------------
        pupil_max = 4.5
        pupil_x = (mouse_rel_x / dist) * min(pupil_max, dist * 0.07)
        pupil_y = (mouse_rel_y / dist) * min(pupil_max, dist * 0.07)

        # -------------------------------------------------------------------------
        # 10. Expressive Anime Eyes
        # -------------------------------------------------------------------------
        eye_lx = face_cx - 14
        eye_rx = face_cx + 14
        eye_y = cy - 7

        if is_sleeping:
            # Peaceful closed crescent eyes with delicate lashes
            self.canvas.create_arc(eye_lx - 8, eye_y - 4, eye_lx + 8, eye_y + 8, start=180, extent=180, style=tk.ARC, width=2.5, outline=OUTLINE_COLOR)
            self.canvas.create_arc(eye_rx - 8, eye_y - 4, eye_rx + 8, eye_y + 8, start=180, extent=180, style=tk.ARC, width=2.5, outline=OUTLINE_COLOR)

        elif self.is_blinking:
            # Quick blink line
            self.canvas.create_line(eye_lx - 8, eye_y + 1, eye_lx + 8, eye_y + 1, fill=OUTLINE_COLOR, width=2.5, capstyle=tk.ROUND)
            self.canvas.create_line(eye_rx - 8, eye_y + 1, eye_rx + 8, eye_y + 1, fill=OUTLINE_COLOR, width=2.5, capstyle=tk.ROUND)

        elif state == State.DANCING:
            # Happy winking eyes (> <)
            self.canvas.create_line(eye_lx - 8, eye_y - 5, eye_lx, eye_y, fill=OUTLINE_COLOR, width=3, capstyle=tk.ROUND)
            self.canvas.create_line(eye_lx - 8, eye_y + 5, eye_lx, eye_y, fill=OUTLINE_COLOR, width=3, capstyle=tk.ROUND)
            self.canvas.create_line(eye_rx, eye_y, eye_rx + 8, eye_y - 5, fill=OUTLINE_COLOR, width=3, capstyle=tk.ROUND)
            self.canvas.create_line(eye_rx, eye_y, eye_rx + 8, eye_y + 5, fill=OUTLINE_COLOR, width=3, capstyle=tk.ROUND)

        elif state == State.FOCUS:
            # Round wireframe reading glasses + focused gaze
            glass_r = 9.0
            self.canvas.create_oval(eye_lx - glass_r, eye_y - glass_r, eye_lx + glass_r, eye_y + glass_r, outline=OUTLINE_COLOR, width=2)
            self.canvas.create_oval(eye_rx - glass_r, eye_y - glass_r, eye_rx + glass_r, eye_y + glass_r, outline=OUTLINE_COLOR, width=2)
            self.canvas.create_line(eye_lx + glass_r, eye_y, eye_rx - glass_r, eye_y, fill=OUTLINE_COLOR, width=2)
            # Pupils
            self.canvas.create_oval(eye_lx - 3, eye_y - 3, eye_lx + 3, eye_y + 3, fill=PUPIL_COLOR, outline="")
            self.canvas.create_oval(eye_rx - 3, eye_y - 3, eye_rx + 3, eye_y + 3, fill=PUPIL_COLOR, outline="")

        elif velocity_speed > 8.0 or state == State.FALLING:
            # Dizzy spiral eyes (@ @)
            for ex in [eye_lx, eye_rx]:
                self.canvas.create_oval(ex - 8, eye_y - 8, ex + 8, eye_y + 8, fill="#FFFFFF", outline=OUTLINE_COLOR, width=2)
                self.canvas.create_oval(ex - 4, eye_y - 4, ex + 4, eye_y + 4, fill=PUPIL_COLOR, outline="")

        else:
            # Large, Shiny Anime Sparkle Eyes
            eye_rw, eye_rh = 8.5, 11.0
            for ex in [eye_lx, eye_rx]:
                # Sclera / eye background
                self.canvas.create_oval(ex - eye_rw, eye_y - eye_rh, ex + eye_rw, eye_y + eye_rh, fill="#FFFFFF", outline=OUTLINE_COLOR, width=2)
                # Iris / Dark Pupil
                px, py = ex + pupil_x, eye_y + pupil_y
                self.canvas.create_oval(px - 5.5, py - 6.5, px + 5.5, py + 6.5, fill=PUPIL_COLOR, outline="")
                # Primary Sparkle Highlight (Big reflection)
                self.canvas.create_oval(px - 4.5, py - 5.0, px - 0.5, py - 1.0, fill="#FFFFFF", outline="")
                # Secondary Twinkle Highlight (Cute tiny reflection)
                self.canvas.create_oval(px + 1.5, py + 1.5, px + 3.5, py + 3.5, fill="#FFFFFF", outline="")

        # -------------------------------------------------------------------------
        # 10. Bunny Nose & Split Lip (:3 / w Smile)
        # -------------------------------------------------------------------------
        nose_y = cy + 2
        # Tiny pink nose
        self.canvas.create_polygon(
            [face_cx - 3.5, nose_y, face_cx + 3.5, nose_y, face_cx, nose_y + 3.5],
            fill=NOSE_COLOR,
            outline="",
            tags="nose"
        )

        if state == State.EXCITED or state == State.DANCING:
            # Open happy smiling mouth
            self.canvas.create_oval(face_cx - 5, nose_y + 5, face_cx + 5, nose_y + 13, fill="#FF6B6B", outline=OUTLINE_COLOR, width=1.5)
        else:
            # Classic bunny split lip (:3 smile)
            self.canvas.create_line(face_cx, nose_y + 3.5, face_cx, nose_y + 6.5, fill=OUTLINE_COLOR, width=1.5)
            self.canvas.create_arc(face_cx - 8, nose_y + 2.5, face_cx, nose_y + 9.5, start=200, extent=140, style=tk.ARC, width=1.5, outline=OUTLINE_COLOR)
            self.canvas.create_arc(face_cx, nose_y + 2.5, face_cx + 8, nose_y + 9.5, start=200, extent=140, style=tk.ARC, width=1.5, outline=OUTLINE_COLOR)

        # -------------------------------------------------------------------------
        # 10.5. Outfits & Accessories (Ribbon, Crown, Sakura, Glasses, Top Hat, Scarf)
        # -------------------------------------------------------------------------
        self._draw_accessory(accessory, face_cx, cy, rx, ry)

        # -------------------------------------------------------------------------
        # 11. Render Active Floating Particles
        # -------------------------------------------------------------------------
        for p in self.particles:
            self.canvas.create_text(
                p["x"],
                p["y"],
                text=p["text"],
                fill=p["color"],
                font=("Segoe UI", p["size"], "bold"),
                tags="particle"
            )

        # -------------------------------------------------------------------------
        # 12. Render Procedural Speech Bubble if active
        # -------------------------------------------------------------------------
        pet_top_y = cy - ry - 25.0  # Above floppy ears
        self.speech_bubble.draw(self.canvas, cx, pet_top_y)

    def _draw_accessory(self, accessory: str, cx: float, cy: float, rx: float, ry: float) -> None:
        """Procedurally renders outfits and accessories on Floppy Bunny."""
        if not accessory or accessory in ("None", "🐾 Natural (None)", "🐾 Natural"):
            return

        acc_lower = accessory.lower()

        # 1. Silk Ribbon Bow
        if "ribbon" in acc_lower or "bow" in acc_lower:
            rx_pos = cx - rx * 0.55
            ry_pos = cy - ry * 0.75
            # Ribbon loops
            self.canvas.create_oval(rx_pos - 12, ry_pos - 8, rx_pos, ry_pos + 6, fill="#FF6B81", outline="#222228", width=1.5)
            self.canvas.create_oval(rx_pos, ry_pos - 8, rx_pos + 12, ry_pos + 6, fill="#FF6B81", outline="#222228", width=1.5)
            # Ribbon center knot
            self.canvas.create_oval(rx_pos - 4, ry_pos - 4, rx_pos + 4, ry_pos + 4, fill="#FF3366", outline="#222228", width=1.5)
            # Ribbon tails
            self.canvas.create_line(rx_pos - 2, ry_pos + 3, rx_pos - 8, ry_pos + 14, fill="#FF6B81", width=2.5)
            self.canvas.create_line(rx_pos + 2, ry_pos + 3, rx_pos + 8, ry_pos + 14, fill="#FF6B81", width=2.5)

        # 2. Royal Golden Crown
        elif "crown" in acc_lower:
            top_y = cy - ry - 4
            crown_pts = [
                cx - 16, top_y,
                cx - 20, top_y - 18,
                cx - 8, top_y - 8,
                cx, top_y - 22,
                cx + 8, top_y - 8,
                cx + 20, top_y - 18,
                cx + 16, top_y,
            ]
            self.canvas.create_polygon(crown_pts, fill="#FFD700", outline="#B8860B", width=1.5)
            # Ruby jewel at crown center
            self.canvas.create_oval(cx - 3, top_y - 10, cx + 3, top_y - 4, fill="#FF1744", outline="#B8860B", width=1)
            self.canvas.create_oval(cx - 1, top_y - 9, cx + 1, top_y - 7, fill="#FFFFFF", outline="")

        # 3. Sakura Cherry Blossom
        elif "sakura" in acc_lower or "flower" in acc_lower:
            fx, fy = cx - rx * 0.6, cy - ry * 0.65
            petal_r = 6.0
            import math
            for angle in [0, 72, 144, 216, 288]:
                rad = math.radians(angle)
                px = fx + math.cos(rad) * 7
                py = fy + math.sin(rad) * 7
                self.canvas.create_oval(px - petal_r, py - petal_r, px + petal_r, py + petal_r, fill="#FFB7C5", outline="#FF85A1", width=1)
            # Center pollen
            self.canvas.create_oval(fx - 3.5, fy - 3.5, fx + 3.5, fy + 3.5, fill="#FFE082", outline="#FFA000", width=1)

        # 4. Smart Glasses
        elif "glasses" in acc_lower:
            gr = 9.5
            gl_x = cx - 18
            gr_x = cx + 18
            gy = cy - 2
            self.canvas.create_oval(gl_x - gr, gy - gr, gl_x + gr, gy + gr, outline="#2C3E50", width=2)
            self.canvas.create_oval(gr_x - gr, gy - gr, gr_x + gr, gy + gr, outline="#2C3E50", width=2)
            self.canvas.create_line(gl_x + gr, gy, gr_x - gr, gy, fill="#2C3E50", width=2)

        # 5. Gentleman Top Hat
        elif "hat" in acc_lower:
            hx = cx + 4
            hy = cy - ry - 2
            # Brim
            self.canvas.create_oval(hx - 22, hy - 4, hx + 22, hy + 6, fill="#2B2B2B", outline="#1A1A1A", width=1.5)
            # Crown
            self.canvas.create_rectangle(hx - 14, hy - 24, hx + 14, hy, fill="#383838", outline="#1A1A1A", width=1.5)
            # Red silk ribbon band
            self.canvas.create_rectangle(hx - 14, hy - 7, hx + 14, hy, fill="#E74C3C", outline="#C0392B", width=1)

        # 6. Cozy Knit Scarf
        elif "scarf" in acc_lower:
            sy = cy + ry * 0.55
            # Scarf collar around neck
            self.canvas.create_oval(cx - 24, sy - 6, cx + 24, sy + 10, fill="#FF9AA2", outline="#E57373", width=1.5)
            # Hanging scarf fringe
            self.canvas.create_rectangle(cx + 8, sy + 2, cx + 18, sy + 22, fill="#FF9AA2", outline="#E57373", width=1.5)
            self.canvas.create_line(cx + 8, sy + 22, cx + 18, sy + 22, fill="#B71C1C", width=2)

