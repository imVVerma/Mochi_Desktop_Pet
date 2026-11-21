# 🐾 Mochi_Desktop_Pet (Floppy Bunny)

> A delightful, lifelike, cute, and genuinely useful virtual desktop companion for Windows.

## 📥 Download Mochi (Zero-Setup)
No Python, terminal, or installation required!
* 🪟 **[Download DesktopPet.exe for Windows](https://github.com/imVVerma/Mochi_Desktop_Pet/releases/latest/download/DesktopPet.exe)** *(Double-click to run! Press `Alt+Q` to summon or dismiss)*
* 🍏 **macOS** & 🐧 **Linux**: In active development
* 📱 **Mobile (iOS & Android)**: Wispr Flow-style floating companion & Dynamic Island in progress!

Desktop Pet is a lightweight, zero-install desktop companion built with Python and Tkinter. Floating framelessly on top of all your application windows, the pet features a procedural vector **Floppy Bunny** character (infinitely scalable, zero bitmap sprite dependencies) with dynamic floppy ear physics, cozy bottom-right corner docking above the taskbar, emotional states, circadian sleep cycles, and real-world productivity assistance.

---

## ✨ Features

- **Cute & Lifelike Floppy Bunny Aesthetics:**
  - **Dynamic Floppy Ears:** Long ears with springy lag/sway physics that droop when sleepy/tired, perk up straight when excited, and trail back during jumps or falls.
  - **3D Depth & Details:** Soft cream belly patch (`#FFF9F2`), fluffy white cotton tail with gentle wagging, and stepped front/back paws with walking gait.
  - **Expressive Anime Sparkle Eyes:** Layered primary specular reflection and micro-twinkle highlight, twitchy whiskers, pink heart-nose, and adorable `:3` mouth.

- **Cozy Corner Stationing:**
  - Naturally roosts in the **bottom-right corner** right above the Windows taskbar clock/tray without obstructing your primary workspace.
  - Autonomous homing behavior (`RETURNING_HOME` state): After wandering or playing, the bunny gently hops back to its home corner to rest.

- **Lifelike Kinematics & Physics:**
  - Acceleration curves, velocity damping, air resistance, and gravity.
  - Procedural **squash-and-stretch** upon landing from jumps or drops.
  - Multi-monitor boundary awareness (including secondary displays placed to the left or top with negative coordinates).
  - Windows taskbar awareness: Perches smoothly right on top of your taskbar!
  - Toss physics: Fling your bunny across your screens with realistic parabolic inertia.

- **Living Personality & Emotional FSM:**
  - Dynamic procedural expressions:
    - Normal / Curious: Pupils follow your mouse cursor smoothly (`o _ O`).
    - Excited / Happy: Dilated eyes, open happy smile, heart particles (`♥`).
    - Dancing: Joyful rhythmic winking (`> <`) and squash bounce.
    - Sleeping: Calm closed eyes (`- _ -`) with floating `z Z Z` particles.
    - Dizzy / Tossed: Concentric spiral eyes (`@ _ @`) when thrown at high velocity.
    - Focus Mode: Tiny wireframe reading glasses!
  - Life meters: `Energy` (0–100), `Happiness` (0–100), `Curiosity` (0–100).
  - Circadian rhythm: Automatically curls up to sleep after 23:00 or during long user inactivity, throttling CPU to < 0.2%.

- **Practical Productivity & Wellness:**
  - **Pomodoro Focus Sprints:** Put Mochi into Focus Mode (`Ctrl+Shift+F`); Mochi puts on study glasses and sits quietly beside you for 25-minute sprints.
  - **Ergonomics & Wellness Speech Bubbles:** Gentle procedural reminders to hydrate, do 20-20-20 eye breaks, stretch shoulders, and check posture.

- **Non-Admin System Integration:**
  - System Tray icon (`pystray`) with right-click menu: Toggle Visibility, Bedtime, Focus Mode, Petting, Skin Color Picker, Exit.
  - Native Windows global hotkeys via Win32 `RegisterHotKey`: **Zero admin/root privileges required** and zero antivirus false positives!
  - Hot-reloadable `config.json`: Change colors, speeds, reminders, or hotkeys without restarting.

---

## 🎮 Controls & Interactions

| Action | Control / Shortcut | Description |
| :--- | :--- | :--- |
| **Pick up & Drag** | `Left Click + Drag` | Pick up Mochi and move him around your screens. |
| **Toss / Fling** | `Fling + Release` | Release cursor while dragging to toss Mochi in an arc. |
| **Pet Mochi** | `Right Click` or `Double Click` | Pet Mochi to boost happiness and trigger happy dances (`Ctrl+Shift+P`). |
| **Summon / Dismiss** | `Ctrl + Shift + B` | Instantly hide Mochi to tray or bring him back to your cursor. |
| **Toggle Focus Mode** | `Ctrl + Shift + F` | Start/pause a 25-minute Pomodoro study sprint. |
| **Context Menu** | `Right Click` (or Tray) | Change skin color, toggle bedtime, or exit. |

---

## 🚀 Getting Started

### Option 1: Standalone Zero-Install Executable (No Python Required)

Run the pre-compiled standalone binary:
```cmd
dist\DesktopPet.exe
```

### Option 2: Run with Python (Zero External Dependencies)

Desktop Pet runs on any system with standard Python 3.8+ and built-in Tkinter:

```bash
# Run directly with standard library
python main.py
```

### Option 3: Full Experience with System Tray & Virtualenv

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install optional enhancements (system tray & testing)
pip install -r requirements.txt

# 3. Launch
python main.py
```

---

## ⚙️ Configuration (`config.json`)

Mochi can be fully customized via `config.json`. Any changes saved to this file are **hot-reloaded automatically**:

```json
{
  "pet_name": "Mochi",
  "scale": 1.0,
  "base_color": "#FFB6C1",
  "auto_color": true,
  "eye_color": "#2C3E50",
  "walk_speed": 3.0,
  "taskbar_height": 45,
  "transparent_color": "#000001",
  "focus_mode": {
    "work_duration_minutes": 25,
    "break_duration_minutes": 5,
    "auto_break": true
  },
  "wellness_reminders": {
    "enabled": true,
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
```

---

## 🧪 Automated Evals & Test Suite

Run the full automated test and stress benchmark suite:

```bash
pytest -v
```

The eval suite tests:
- **State Machine Invariants (`test_fsm.py`):** 5,000 tick deadlock verification, energy depletion guarantee, interruption guarantee, Pomodoro invariants.
- **Physics & Boundaries (`test_physics.py`):** Negative multi-monitor clamping, taskbar perching, parabolic fling physics, squash-and-stretch damping.
- **Resilience & Hot-Reload (`test_config.py`):** Corrupt JSON fallback recovery, deep schema merge, live hot-reloading.
- **Stress & Resource Bounds (`test_stress.py`):**
  - **CPU Ceiling:** < 2.0 ms per simulation frame.
  - **Zero Leaks:** 50,000-tick endurance run with < 5.0 MB heap delta.
  - **Chaos Drag:** 1,000 rapid chaotic flings with zero NaN or bounding errors.

---

## 📦 Building the Standalone Executable

To compile into a single `.exe`:

```cmd
build\build.bat
```
or run PyInstaller directly:
```bash
pyinstaller --noconsole --onefile --name "DesktopPet" --icon "build/icon.ico" --add-data "config.json;." main.py
```
The compiled binary will be placed in `dist/DesktopPet.exe`.
