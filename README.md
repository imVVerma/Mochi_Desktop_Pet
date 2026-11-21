# 🐾 Mochi Desktop Pet (Floppy Bunny)

> A delightful, lifelike, cute, and genuinely useful virtual desktop companion for Windows (macOS, Linux & Mobile coming soon!).

[![Release](https://img.shields.io/badge/Release-v1.0.0-FFB6C1?style=for-the-badge&logo=windows)](https://github.com/imVVerma/Mochi_Desktop_Pet/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20(Cross--Platform%20Ready)-blue?style=for-the-badge)](https://github.com/imVVerma/Mochi_Desktop_Pet/blob/main/ROADMAP.md)

---

## 📥 1-Click Download (No Python or Terminal Required!)

| Platform | Download Link | Quick Start |
| :--- | :--- | :--- |
| 🪟 **Windows** | [⬇️ **Download DesktopPet.exe**](https://github.com/imVVerma/Mochi_Desktop_Pet/releases/latest/download/DesktopPet.exe) | 1. Double-click `DesktopPet.exe` to run!<br>2. Press **`Alt + Q`** to summon or dismiss Mochi anytime. |
| 🍏 **macOS** | *In development (Qt/Cocoa PAL)* | See [Roadmap](ROADMAP.md) |
| 🐧 **Linux** | *In development (AppImage)* | See [Roadmap](ROADMAP.md) |
| 📱 **Mobile** | *In development (Android Bubble / iOS Dynamic Island)* | See [Wispr Flow Mobile Model](ROADMAP.md) |

---

## ✨ What Makes Mochi Special?

* **🐰 Lifelike Floppy Bunny Aesthetics:**
  * **Dynamic Ear Physics**: Soft bunny ears sway and trail with momentum, droop when sleepy, perk up straight when excited, and flutter during jumps.
  * **Layered 3D Vector Depth**: Soft cream belly patch, fluffy cotton tail, twitchy whiskers, stepped walking paws, and anime sparkle eyes with pupil mouse tracking.
* **📍 Cozy Taskbar Corner Roosting:**
  * When you are busy working, Mochi gently hops across the bottom of your screen and perches in the **bottom-right corner** above your taskbar clock without getting in your way.
* **🎨 Zero-Code In-App Wardrobe & Personalization:**
  * Right-click Mochi to open the visual **Preferences & Wardrobe dialog**: rename your pet, choose pastel colors, record custom hotkeys, and adjust timers with live hot-reloading!
* **🔍 Windows Search Bar Integration:**
  * Press the Windows key, type your pet's name (e.g. `Mochi`), and press Enter to launch or toggle!
* **🎓 Pomodoro & Wellness Assistant:**
  * Puts on reading glasses for 25-minute Pomodoro study sprints, plus gentle speech bubbles reminding you to hydrate, stretch, and take 20-20-20 eye rests.
* **⚡ Ultra-Lightweight & Non-Admin:**
  * Pure procedural vector graphics (zero bulky sprite sheets), < 0.2% CPU when resting, and strictly user-mode Win32 hotkeys (no admin rights or kernel drivers needed).

---

## 🎮 How to Play & Controls

### Mouse Interactions
* **Grab & Drag**: `Left Click + Drag` Mochi anywhere across your monitors.
* **Toss & Fling**: Drag and release with speed to throw Mochi in a parabolic physics arc! Mochi shows dizzy spiral eyes `(@ _ @)` and squashes upon landing.
* **Pet / Cheer Up**: `Right Click` Mochi -> **✨ Cheer Up / Pet** (or double-click) to shower hearts and boost happiness!

### Global Keyboard Shortcuts
| Hotkey | Action | Description |
| :--- | :--- | :--- |
| **`Alt + Q`** | **Summon / Dismiss** | Toggles Mochi: if on-screen, hides to tray; if in tray, pops up right where you are! *(Customizable in Wardrobe)* |
| **`Ctrl + Shift + F`** | **Focus Mode** | Starts or pauses a 25-minute Pomodoro study sprint with tiny wireframe glasses. |
| **`Ctrl + Shift + P`** | **Pet Cheer-Up** | Instant happiness boost from anywhere on your PC. |
| **`Ctrl + Shift + B`** | **Backup Hotkey** | Permanent fallback hotkey for summoning/dismissing. |

---

## 🌸 Customization (Zero JSON Editing)

Right-click Mochi and select **`⚙️ Preferences & Wardrobe...`** to open the built-in customization suite:

1. **Appearance & Name**:
   * Change your companion's name (e.g. *Koko*, *BunnyHop*, *Fluffy*).
   * **Automatic Windows Search Sync**: Renaming updates your Windows Start Menu shortcut so searching your pet's new name finds it immediately!
   * Pick from pastel swatches (*Blossom Pink, Mint Sage, Sky Blue, Lavender, Buttercup, Peach Sorbet, White*) or a full custom color wheel with live avatar preview.
   * Adjust Mochi's size scale from 70% to 150%.
2. **Interactive Hotkey Recorder**:
   * Click **Record New Hotkey ⏺️**, press any key combo (e.g. `Alt+Q`, `Ctrl+Space`, `Alt+Z`), and it auto-saves!
3. **Habits & Timers**:
   * Adjust Pomodoro sprint and break lengths.
   * Adjust the corner docking inactivity delay (5s to 60s).
   * Customize circadian bedtime and morning wake-up hours.

---

## 🛠️ For Developers & Modders

### Running from Source
```bash
# 1. Clone the repository
git clone https://github.com/imVVerma/Mochi_Desktop_Pet.git
cd Mochi_Desktop_Pet

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Desktop Pet
python main.py
```

### Running the Test Suite
```bash
python -m pytest
```
*All 29 unit tests cover configuration recovery, state transitions, physics bounds, global hotkeys, platform abstraction layer (PAL), and GUI dialog actions.*

### Building the Standalone Executable
```bash
# Automated one-click build script
build\build.bat
```
The compiled binary will be placed at `dist/DesktopPet.exe`.

### Creating Windows Search Shortcuts
```bash
python build\install_shortcut.py
```
Installs shortcuts into your Start Menu and Desktop, and flushes the Windows Explorer shell cache.

---

## 📁 Clean Repository Structure

```
Mochi_Desktop_Pet/
├── .github/workflows/       # GitHub Actions CI/CD (automated Windows executable release)
├── build/                   # Icon generator and Windows shortcut installer scripts
├── core/                    # Engine, Physics kinematics, FSM, Hotkeys, and Config manager
│   └── pal/                 # Platform Abstraction Layer (DisplayMetrics, IPC, Window Transparency)
├── dist/                    # Standalone zero-install DesktopPet.exe and local config
├── mobile/                  # Mobile companion (Android Floating Service & Flutter companion)
│   ├── android_overlay/     # Android SYSTEM_ALERT_WINDOW floating pet service
│   └── flutter_companion/   # Cross-platform Flutter interactive companion
├── tests/                   # 29 automated unit tests (100% green test suite)
├── ui/                      # Tkinter canvas renderer, Window overlay, Tray, and Settings Dialog
├── main.py                  # Single-instance application entry point
├── config.json              # Application configuration
├── requirements.txt         # Python dependencies
└── ROADMAP.md               # Cross-platform & Mobile Companion Architecture Roadmap
```

---

## 🗺️ Roadmap & Future Features

We are actively expanding Mochi into a cross-platform companion:
* **macOS & Linux**: Platform Abstraction Layer (PAL) with PySide6/Qt for unified native window transparency.
* **Mobile Companion (Wispr Flow model)**:
  * **Android**: Floating Pet Bubble (`SYSTEM_ALERT_WINDOW`) overlaying all mobile apps.
  * **iOS**: Dynamic Island & Live Activities (`ActivityKit`) for iPhone 14 Pro/15/16.
  * **Cozy Sanctuary App**: Cross-platform Flutter mini-game (feeding, petting, haptics, focus room).

Read the detailed architecture in **[ROADMAP.md](ROADMAP.md)**!

---

## 📄 License

MIT License. Free to use, customize, and share! 💖
