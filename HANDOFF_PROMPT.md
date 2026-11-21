# Developer & AI Agent Handoff: Desktop Pet Project
> **Target Repository:** `c:\Users\Vaibhav Verma\Documents\VV-Plak\WB\Eggoz\desktop_pet`  
> **Status Reference:** `PROJECT_STATUS.md` & `desktop_pet_ARCHAEOLOGY.md`  
> **Objective:** Transform a raw prototype Python/Tkinter script into a polished, delightful, stress-tested, and fully packaged desktop virtual companion ready for real daily users.

---

## Instructions for the Incoming Agent / Developer

You are stepping in as the lead engineer and product designer for **Desktop Pet**. 

Your goal is not just to edit a script, but to build, validate, stress-test, and package an actual product that people will love having on their desktop every day. You will follow an autonomous, eval-driven engineering loop:
1. **Analyze Baseline & Architecture**: Understand what exists and decouple the monolithic script into a clean, testable architecture.
2. **Build an Automated Eval & Simulation Suite**: Create headless test harnesses that validate physics, state machine invariants, CPU limits, screen boundaries, and configuration resilience without needing a physical human clicking for 5 hours.
3. **Implement Core Upgrades**: Add kinematic physics, living mood/circadian systems, productivity modes (pomodoro/water breaks), system tray controls, and hot-reloadable configs.
4. **Stress-Test & Harden**: Simulate multi-monitor setups, high-DPI scaling, memory leak benchmarks, and rapid drag-and-drop chaos.
5. **Package for Distribution**: Create a zero-install standalone Windows executable (`.exe`) with professional icon and documentation.

---

## 1. Current Codebase Baseline & Audit

### Existing Files in `desktop_pet/`:
* `pet.py` (234 lines): Base procedural Tkinter pet with vector canvas drawing, autonomous state machine (`IDLE`, `WANDERING`, `DANCING`, `JUMPING`, `SLEEPING`, `EXCITED`), mouse proximity tracking, drag-and-drop, and right-click petting.
* `relax_pet.py` (300 lines): Divergent iteration that adds global background hotkey summon/dismiss (`Ctrl + Shift + B` via the `keyboard` library).
* `PROJECT_STATUS.md`: Full status breakdown and gap analysis.
* `desktop_pet_ARCHAEOLOGY.md`: Detailed retrospective archaeology report.

### Critical Deficiencies of the Current Prototype:
1. **Code Fragmentation**: Two redundant scripts (`pet.py` and `relax_pet.py`) instead of a single cohesive architecture.
2. **Platform & Transparency Brittleness**: Windows-specific `-transparentcolor 'black'` means any black elements in the pet become transparent holes, and macOS/Linux render an ugly black bounding box.
3. **No Non-Admin Hotkeys**: `keyboard` library hooks low-level OS drivers, requiring administrator/root privileges on many machines.
4. **Zero Headless Evals / Tests**: If animation or state transition logic breaks, there are no tests to catch it.
5. **No Settings or Persistence**: Pet color, size, speed, hotkeys, and stats are hardcoded in source variables.
6. **No Real-World Utility**: It is purely an autonomous distraction; it lacks productivity integration (e.g. Pomodoro focus timers, posture/hydration reminders, circadian bedtime).

---

## 2. Product Vision: The Modern "Living" Desk Companion

We are building a charming, non-intrusive, procedural desktop companion that feels genuinely alive and serves as a delightful productivity buddy:

* **Life-like Kinematics & Physics**:
  * Gravity, acceleration, velocity damping, and procedural squash-and-stretch when landing from jumps or drops.
  * Screen boundary awareness: Pet perches on top of the Windows taskbar, climbs screen edges, or walks along the bottom.
* **Living Needs & Circadian Rhythm**:
  * Stats: `Energy` (0–100), `Happiness` (0–100), `Curiosity` (0–100).
  * Pet falls asleep automatically at night (e.g., after 23:00) or when idle for long periods.
  * Pet gets curious when mouse activity is high, and sleeps peacefully when mouse is still.
* **Productivity & Wellness Companion**:
  * **Pomodoro / Focus Mode**: Pet puts on tiny glasses/study hat and sits quietly during 25-minute focus blocks.
  * **Wellness Speech Bubbles**: Procedural speech bubble pops up with gentle reminders: *"Time to drink some water!"*, *"Stretch your shoulders!"*, *"20-20-20 eye break!"*.
* **System Integration**:
  * Clean system tray icon (`pystray`) with right-click menu: Settings, Change Skin/Color, Focus Mode, Mute Sounds, Sleep, Exit.
  * `config.json` support with live hot-reloading (user can change colors or hotkey without restarting).
  * Fallback to Tkinter-native / PyHook global hotkeys that don't trigger antivirus or require admin privileges.

---

## 3. The Target Modular Architecture

Refactor the monolithic script into a clean, decoupled package:

```
desktop_pet/
├── config.json               # User preferences (colors, hotkeys, reminders, scale)
├── main.py                   # Application entry point & loop runner
├── core/
│   ├── engine.py             # Main controller coordinating FSM, physics, and window
│   ├── fsm.py                # Finite State Machine (IDLE, WANDERING, SLEEPING, FOCUS, etc.)
│   ├── physics.py            # Coordinate math, velocity, gravity, collisions, screen bounds
│   └── stats.py              # Energy, happiness, focus timer, reminder schedules
├── ui/
│   ├── window.py             # Transparent frameless Tkinter overlay window
│   ├── canvas_renderer.py    # Procedural vector drawing (eyes, body squash, speech bubbles)
│   ├── tray.py               # System tray icon and menu (pystray)
│   └── bubble.py             # Procedural speech bubble overlays
├── tests/
│   ├── conftest.py           # Headless mock Tkinter environment
│   ├── test_fsm.py           # State transition coverage and invariant verification
│   ├── test_physics.py       # Kinematics, bounce damping, taskbar clamping
│   ├── test_config.py        # Config schema validation, corruption recovery
│   └── test_stress.py        # 10,000-tick endurance, memory leak & CPU benchmark
└── build/                    # PyInstaller build specs and assets
```

---

## 4. The Validation & Eval-Driven Methodology

You must write and maintain an automated evaluation suite (`tests/`) before and alongside implementing features. Never rely exclusively on manual visual checking.

### Eval Suite 1: State Machine Invariants (`test_fsm.py`)
- **No Deadlock Invariant**: Simulate 5,000 state transitions; verify the pet never enters an unhandled state or hangs indefinitely.
- **Energy Depletion & Sleep Recovery**: Verify that after high physical activity (`DANCING`, `JUMPING`), energy decreases and guarantees a transition to `TIRED` or `SLEEPING`.
- **Interruption Guarantee**: When the user clicks or drags the pet, any autonomous state must instantly yield to `HELD` / `DRAGGED`.

### Eval Suite 2: Kinematics & Boundary Clamping (`test_physics.py`)
- **Desktop Clamping**: Test coordinates across single-monitor, dual-monitor, and negative coordinate setups (e.g., secondary monitor to the left). Verify the pet's bounding box is clamped to visible coordinates at all times.
- **Taskbar Perching**: Verify that downward gravity accelerates until `y == screen_height - taskbar_height - pet_height`, triggering a squash-and-stretch landing effect.
- **Drop Physics**: Releasing mouse drag at position `(x, y)` with drag velocity must compute trajectory arc until contact with bottom boundary.

### Eval Suite 3: Performance & Resource Benchmark (`test_stress.py`)
- **CPU Ceiling**: In headless loop simulation, tick calculations per frame must execute in < 2.0 milliseconds.
- **Zero Memory Growth**: Run a 50,000-tick simulation simulating 30 minutes of continuous runtime. Verify heap memory delta remains below 5MB (no canvas item leaks or uncollected closures).
- **Graceful Config Recovery**: Corrupt `config.json` with invalid JSON syntax. Verify the engine loads default fallbacks without crashing and writes a warning log.

---

## 5. Step-by-Step Execution Plan

### Step 1: Establish Architecture & Test Harness
1. Create the modular directory structure (`core/`, `ui/`, `tests/`).
2. Write `tests/conftest.py` providing a headless mock for `tkinter.Tk` and `tkinter.Canvas` so tests run cleanly in headless CI/CD and terminal environments.
3. Write initial baseline tests in `tests/test_fsm.py` and `tests/test_physics.py`.

### Step 2: Unify & Decouple Core Logic
1. Implement `core/fsm.py` with explicit state classes or enum transitions.
2. Implement `core/physics.py` with smooth acceleration, gravity, velocity clamping, and multi-monitor bounds.
3. Implement `core/stats.py` tracking energy, Pomodoro focus mode, and hydration intervals.
4. Implement `config.json` with automatic fallback creation if missing.

### Step 3: Modernize UI & Rendering
1. Build `ui/canvas_renderer.py`:
   - Keep vector procedural rendering (resolution-independent, zero image asset dependencies).
   - Add dynamic expressions: happy eyes `^ _ ^`, sleepy eyes `- _ -`, surprised eyes `o _ O`, study glasses for focus mode.
   - Implement procedural speech bubbles with auto-fading timers.
2. Build `ui/tray.py`:
   - Add system tray integration using `pystray` (or fallback Tkinter context menu if `pystray` is uninstalled).
   - Menu items: Open Settings, Toggle Focus Mode, Force Sleep, Change Color, Exit.
3. Build non-intrusive global hotkey handling:
   - Use `pynput` or graceful fallback hotkey binding that does not require OS root/admin permissions.

### Step 4: Run Evals & Fix Failures
1. Run `pytest tests/` in the terminal.
2. Fix all assertion errors, state glitches, boundary overflows, and edge cases discovered by the evals.
3. Run the performance benchmark to verify minimal CPU consumption.

### Step 5: Final Packaging & Deliverables
1. Create a root `main.py` entry point.
2. Write a comprehensive, user-friendly `README.md` with:
   - What the pet does.
   - How to run with zero dependencies (`python main.py`).
   - Keyboard shortcuts and interactions table.
   - Configuration options.
3. Provide a `build.bat` / PyInstaller command to compile a single standalone `DesktopPet.exe`.
