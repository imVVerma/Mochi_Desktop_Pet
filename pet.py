import math
import random
import tkinter as tk

class AlivePet:
    def __init__(self):
        self.window = tk.Tk()
        
        # --- OVERLAY CONFIGURATION ---
        self.window.config(bg='black')
        self.window.overrideredirect(True)          # Frameless
        self.window.attributes('-topmost', True)     # Stay on top
        self.window.wm_attributes('-transparentcolor', 'black') # Transparent background
        
        self.width, self.height = 140, 140
        self.screen_w = self.window.winfo_screenwidth()
        self.screen_h = self.window.winfo_screenheight()
        
        # Start near bottom of screen above taskbar
        self.x = self.screen_w - 200
        self.y = self.screen_h - 220
        self.window.geometry(f'{self.width}x{self.height}+{int(self.x)}+{int(self.y)}')

        # --- PROCEDURAL CANVAS ---
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg='black', highlightthickness=0)
        self.canvas.pack()

        # --- PET PERSONALITY & LIVING STATES ---
        # States: IDLE, WANDERING, DANCING, JUMPING, SLEEPING, EXCITED
        self.state = "IDLE"
        self.frame = 0
        self.color_hue = 0.5
        self.direction = 1  # 1 = right, -1 = left
        self.walk_speed = 3
        
        # Life meters
        self.stamina = 100
        self.happiness = 80
        
        # Particles (for sleeping Zzz or hearts)
        self.particles = []

        # Mouse interaction bindings
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.drag_pet)
        self.canvas.bind('<Button-3>', lambda e: self.window.destroy()) # Right click exits

        # Start Living Loops
        self.update_loop()
        self.brain_loop()
        self.window.mainloop()

    def get_pet_color(self):
        """Generates soft soothing pastels that react to state."""
        if self.state == "SLEEPING":
            return '#8A9EA7' # Muted slate blue when sleeping
        elif self.state == "EXCITED":
            return '#FF9AA2' # Energetic pink/rose
        
        # Dynamic rainbow cycle for normal states
        r = int(180 + 50 * math.sin(self.color_hue))
        g = int(180 + 50 * math.sin(self.color_hue + 2))
        b = int(210 + 45 * math.cos(self.color_hue))
        return f'#{r:02x}{g:02x}{b:02x}'

    def draw_pet(self, offset_y=0, stretch_x=0):
        """Draws body, dynamic eye-tracking pupils, and particle effects."""
        self.canvas.delete("all")
        color = self.get_pet_color()
        
        cx, cy = 70, 70 + offset_y
        rx = 45 + stretch_x
        ry = 45 - (stretch_x * 0.5)

        # 1. Main Blob Body
        self.canvas.create_oval(cx - rx, cy - ry, cx + rx, cy + ry, fill=color, outline="")

        # 2. Eye Tracking (Calculate relative mouse angle)
        mx = self.window.winfo_pointerx() - (self.x + cx)
        my = self.window.winfo_pointery() - (self.y + cy)
        dist = math.hypot(mx, my) or 1
        # Limit pupil shift range
        pupil_x = (mx / dist) * 4
        pupil_y = (my / dist) * 4

        # 3. Expressions based on state
        if self.state == "SLEEPING":
            # Closed calm eyes (- -)
            self.canvas.create_line(cx - 20, cy - 4, cx - 8, cy - 4, fill="#333333", width=3)
            self.canvas.create_line(cx + 8, cy - 4, cx + 20, cy - 4, fill="#333333", width=3)
            self.canvas.create_arc(cx - 6, cy - 2, cx + 6, cy + 6, start=180, extent=180, style=tk.ARC, width=2, outline="#333333")
        
        elif self.state == "EXCITED":
            # Wide open eyes with pupils following mouse
            self.canvas.create_oval(cx - 22, cy - 14, cx - 6, cy + 2, fill="white", outline="#333333", width=2)
            self.canvas.create_oval(cx + 6, cy - 14, cx + 22, cy + 2, fill="white", outline="#333333", width=2)
            # Pupils
            self.canvas.create_oval(cx - 16 + pupil_x, cy - 8 + pupil_y, cx - 12 + pupil_x, cy - 4 + pupil_y, fill="#222")
            self.canvas.create_oval(cx + 12 + pupil_x, cy - 8 + pupil_y, cx + 16 + pupil_x, cy - 4 + pupil_y, fill="#222")
            # Open surprised mouth
            self.canvas.create_oval(cx - 6, cy + 4, cx + 6, cy + 14, fill="#FF6B6B", outline="")

        elif self.state == "DANCING":
            # Happy Winking eyes (> <)
            self.canvas.create_line(cx - 20, cy - 8, cx - 10, cy - 2, fill="#333", width=3)
            self.canvas.create_line(cx - 20, cy + 2, cx - 10, cy - 2, fill="#333", width=3)
            self.canvas.create_line(cx + 10, cy - 2, cx + 20, cy - 8, fill="#333", width=3)
            self.canvas.create_line(cx + 10, cy - 2, cx + 20, cy + 2, fill="#333", width=3)
            # Smile
            self.canvas.create_arc(cx - 10, cy - 2, cx + 10, cy + 10, start=180, extent=180, style=tk.ARC, width=2, outline="#333")

        else: # IDLE or WANDERING
            # Normal eyes with pupils tracking mouse
            self.canvas.create_oval(cx - 20, cy - 10, cx - 8, cy + 2, fill="white", outline="#333", width=2)
            self.canvas.create_oval(cx + 8, cy - 10, cx + 20, cy + 2, fill="white", outline="#333", width=2)
            # Pupils
            self.canvas.create_oval(cx - 16 + pupil_x, cy - 6 + pupil_y, cx - 12 + pupil_x, cy - 2 + pupil_y, fill="#222")
            self.canvas.create_oval(cx + 12 + pupil_x, cy - 6 + pupil_y, cx + 16 + pupil_x, cy - 2 + pupil_y, fill="#222")
            # Cute smile
            self.canvas.create_arc(cx - 8, cy, cx + 8, cy + 8, start=180, extent=180, style=tk.ARC, width=2, outline="#333")

        # 4. Render Active Particles (Zzz when sleeping, hearts when excited)
        for p in self.particles:
            self.canvas.create_text(p['x'], p['y'], text=p['text'], fill=p['color'], font=("Arial", p['size'], "bold"))

    def update_particles(self):
        """Animates floating particles upward."""
        for p in self.particles[:]:
            p['y'] -= 1.5
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)

    def spawn_particle(self, text, color, size=12):
        self.particles.append({'x': 70 + random.randint(-20, 20), 'y': 30, 'text': text, 'color': color, 'size': size, 'life': 20})

    def update_loop(self):
        """Main physical animation and motion tick (~20 FPS)."""
        self.frame += 1
        self.color_hue += 0.02
        self.update_particles()

        offset_y = 0
        stretch_x = 0

        # Mouse Distance Awareness
        mx = self.window.winfo_pointerx() - (self.x + 70)
        my = self.window.winfo_pointery() - (self.y + 70)
        mouse_dist = math.hypot(mx, my)

        # Trigger reaction if mouse comes too close while idle/wandering
        if mouse_dist < 80 and self.state in ["IDLE", "WANDERING"]:
            self.state = "EXCITED"
            self.spawn_particle("!", "#FF4081", size=14)

        # State Physics Behaviors
        if self.state == "WANDERING":
            self.x += self.walk_speed * self.direction
            # Bounce off screen boundaries
            if self.x <= 10 or self.x >= self.screen_w - 150:
                self.direction *= -1
            offset_y = int(5 * math.abs(math.sin(self.frame * 0.3))) # Walking bob
            self.stamina -= 0.05

        elif self.state == "DANCING":
            offset_y = int(8 * math.sin(self.frame * 0.4))
            stretch_x = int(6 * math.cos(self.frame * 0.4))
            self.stamina -= 0.1

        elif self.state == "JUMPING":
            jump_phase = (self.frame % 15) / 15.0
            offset_y = int(-35 * math.sin(jump_phase * math.pi))
            stretch_x = int(-6 * math.sin(jump_phase * math.pi))
            self.stamina -= 0.15

        elif self.state == "SLEEPING":
            # Slow breathing cycle
            breathe = math.sin(self.frame * 0.05)
            stretch_x = int(8 * breathe)
            offset_y = int(-2 * breathe)
            self.stamina = min(100, self.stamina + 0.2) # Recharge stamina
            
            if self.frame % 30 == 0:
                self.spawn_particle("z", "#7E57C2", size=10)

        elif self.state == "EXCITED":
            offset_y = int(-12 * math.abs(math.sin(self.frame * 0.5)))
            if self.frame % 15 == 0:
                self.spawn_particle("♥", "#FF4081", size=12)

        else: # IDLE
            offset_y = int(3 * math.sin(self.frame * 0.15))

        # Apply Window Movement
        self.window.geometry(f'{self.width}x{self.height}+{int(self.x)}+{int(self.y)}')
        self.draw_pet(offset_y, stretch_x)

        self.window.after(50, self.update_loop)

    def brain_loop(self):
        """Autonomous Decision Making (AI State Machine)."""
        # If exhausted, force sleep
        if self.stamina <= 10 and self.state != "SLEEPING":
            self.state = "SLEEPING"
        elif self.state == "SLEEPING" and self.stamina < 90:
            pass # Keep sleeping until rested
        else:
            # Randomly pick autonomous action
            choices = ["IDLE", "WANDERING", "WANDERING", "DANCING", "JUMPING"]
            self.state = random.choice(choices)
            if self.state == "WANDERING":
                self.direction = random.choice([1, -1])

        # Schedule next thought/state shift in 4 to 8 seconds
        next_thought = random.randint(4000, 8000)
        self.window.after(next_thought, self.brain_loop)

    def on_click(self, event):
        """Direct User Interaction (Petting / Waking up)."""
        if self.state == "SLEEPING":
            self.state = "EXCITED"
            self.spawn_particle("!", "#FFB74D", size=14)
        else:
            self.happiness = min(100, self.happiness + 10)
            self.state = "DANCING"
            self.spawn_particle("♥", "#E91E63", size=14)

    def drag_pet(self, event):
        self.x = self.window.winfo_pointerx() - 70
        self.y = self.window.winfo_pointery() - 70
        self.window.geometry(f'{self.width}x{self.height}+{int(self.x)}+{int(self.y)}')

if __name__ == '__main__':
    AlivePet()