# 🐾 Mochi Desktop Pet (Floppy Bunny)

> A delightful, lifelike, cute, and genuinely useful virtual desktop and mobile companion for **Windows** and **Android** (macOS & iOS coming soon!).

[![Release](https://img.shields.io/badge/Release-v1.0.0-FFB6C1?style=for-the-badge&logo=windows)](https://github.com/imVVerma/Mochi_Desktop_Pet/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Flutter](https://img.shields.io/badge/Flutter-3.50+-02569B?style=for-the-badge&logo=flutter)](https://flutter.dev)
[![Platform](https://img.shields.io/badge/Platforms-Windows%20%7C%20Android-green?style=for-the-badge)](https://github.com/imVVerma/Mochi_Desktop_Pet)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

---

## 📥 Instant Downloads (No Coding or Terminal Required!)

| Platform | Download | Quick Start |
| :--- | :--- | :--- |
| 🪟 **Windows** | [⬇️ **Download DesktopPet.exe**](https://github.com/imVVerma/Mochi_Desktop_Pet/releases/latest/download/DesktopPet.exe) | 1. Double-click `DesktopPet.exe` to run!<br>2. Press **`Alt + Q`** to summon or dismiss Mochi anytime.<br>3. Right-click Mochi to customize outfits, colors, and hotkeys. |
| 📱 **Android** | [⬇️ **Download MochiCompanion.apk**](https://github.com/imVVerma/Mochi_Desktop_Pet/releases/latest/download/MochiCompanion.apk) | 1. Install `MochiCompanion.apk` on your Android phone.<br>2. Tap **`✨ Float Over Other Apps`** to summon Mochi over your screen (WhatsApp, YouTube, etc.)! |
| 🍏 **macOS** | *In development (Qt/Cocoa PAL)* | See [Cross-Platform Roadmap](ROADMAP.md) |
| 🐧 **Linux** | *In development (AppImage)* | See [Cross-Platform Roadmap](ROADMAP.md) |
| 🍎 **iOS** | *In development (Live Activities)* | See [Cross-Platform Roadmap](ROADMAP.md) |

---

## ✨ Features

### 🐰 Lifelike Procedural Floppy Bunny
* **Dynamic Ear Momentum**: Soft bunny ears sway with movement, flutter during jumps, droop when sleepy, and perk up when excited.
* **Procedural Vector Rendering**: Zero pixelated sprite sheets. Renders smoothly at any monitor scale or phone resolution.
* **Interactive Facial Expressions**: Blushing cheeks, gentle breathing animations, and sparkle eyes that track your mouse cursor.

### 📍 Snug Taskbar-Clock Docking
* Mochi gently hops across your desktop and **perches in the bottom-right corner**, resting snugly directly above your system clock and date without getting in the way of your work.
* Stationing invariant ensures Mochi stays securely anchored until you drag or summon him.

### 👗 Wardrobe Suite & 6 Wearable Outfits
* **Outfits & Accessories**:
  * `👑 Royal Crown` — Golden mini-crown with sparkling ruby jewel.
  * `🎀 Silk Ribbon` — Pastel ear bow with fluttering ribbons.
  * `🌸 Sakura Flower` — Delicate cherry blossom bloom with gold center.
  * `👓 Smart Glasses` — Round wireframe study glasses.
  * `🎩 Top Hat` — Dapper black top hat with silk band.
  * `🧣 Cozy Scarf` — Knitted pastel winter scarf.
  * `🐾 Natural` — Classic accessory-free bunny.
* **Instant Outfits Menu**: Right-click Mochi anytime -> **`👗 Outfits & Accessories`** to switch outfits on the fly without opening settings!

### 📱 Wispr Flow Mobile Model (Android Floating Overlay)
* Mochi breaks out of the app box! Using Android's `SYSTEM_ALERT_WINDOW`, Mochi floats seamlessly over **all apps** (WhatsApp, Chrome, YouTube, Instagram, and Home screen).
* **Tactile Haptic Feedback**: Feel soft ticks when picking up or placing Mochi.
* **Magnetic Edge Docking**: Fling Mochi toward the edge and watch him smoothly dock to either margin.
* **Tap Reactions**: Tap Mochi while using any app to hear cute speech bubbles and cheer-ups.

### 🔍 Windows Search Bar Sync
* Press the **Windows Key**, type `Mochi` (or whatever custom name you give your pet in the wardrobe), and press **Enter** to instantly summon or dismiss your companion!

### 🎓 Pomodoro Focus & Digital Wellbeing
* **Study Mode**: Puts on study glasses for 25-minute Pomodoro sprints.
* **Wellness Reminders**: Subtle, non-intrusive bubbles reminding you to hydrate, blink, correct your posture, and take 20-20-20 eye breaks.

---

## 🎮 Controls & Interactions

### Windows Mouse & Hotkeys
* **Drag & Move**: `Left Click + Hold` to drag Mochi anywhere across single or multi-monitor setups.
* **Toss & Fling**: Drag and release with speed to throw Mochi in a parabolic physics arc! Mochi shows spiral eyes `(@ _ @)` and squashes softly on impact.
* **Pet / Cheer Up**: `Right Click` -> **✨ Cheer Up / Pet** (or double-click) to shower hearts and boost happiness.
* **Quick Outfits**: `Right Click` -> **👗 Outfits & Accessories**.
* **Global Keyboard Shortcuts**:
  | Shortcut | Action | Description |
  | :--- | :--- | :--- |
  | **`Alt + Q`** | **Summon / Dismiss** | Toggles Mochi on/off screen from any application. *(Fully customizable)* |
  | **`Ctrl + Shift + F`** | **Focus Mode** | Starts or pauses a 25-minute Pomodoro study sprint. |
  | **`Ctrl + Shift + P`** | **Pet Cheer-Up** | Instant happiness boost from anywhere on your PC. |
  | **`Ctrl + Shift + B`** | **Fallback Summon** | Permanent hardware-level backup toggle. |

### Mobile Touch Gestures
* **Drag**: Move Mochi around your phone screen.
* **Fling**: Flick toward either side to magnetically snap to the nearest margin.
* **Single Tap**: Trigger heart sparkles and supportive speech bubbles.
* **Float Toggle**: Tap **`✨ Float Over Other Apps`** inside the app to enable or dismiss the floating companion.

---

## 🌸 Visual Preferences Suite

Right-click Mochi and select **`⚙️ Preferences & Wardrobe...`** to access the zero-code customization dashboard:

1. **Identity & Name**: Rename your companion (updates Windows Start Menu search indexing in real time).
2. **Fur Palette**: Choose from curated pastel colors (*Vanilla Cream, Strawberry Milk, Cloud White, Mint Sage, Sky Blue, Lilac Mist*) or pick any custom hex color.
3. **Live Avatar Preview**: Displays your chosen fur color and selected outfit rendered together in real time.
4. **Interactive Hotkey Recorder**: Click `Record New Hotkey ⏺️` and press any combination to bind custom summon shortcuts.
5. **Habit & Focus Timers**: Adjust Pomodoro durations, break lengths, and circadian sleep schedules.

---

## 🛠️ Developer & Modder Guide

### 🪟 Windows Desktop Setup

```bash
# 1. Clone the repository
git clone https://github.com/imVVerma/Mochi_Desktop_Pet.git
cd Mochi_Desktop_Pet

# 2. Set up virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Desktop Pet
python main.py

# 5. Run test suite
pytest
```

#### Compiling Standalone `DesktopPet.exe`:
```bash
build\build.bat
```
The compiled, zero-dependency binary will be placed at `dist/DesktopPet.exe`.

---

### 📱 Android Mobile Setup (Flutter)

```bash
# 1. Navigate to mobile companion directory
cd mobile/flutter_companion

# 2. Get Flutter dependencies
flutter pub get

# 3. Run on connected Android phone
flutter run
```

#### Compiling Debug / Release APK:
```bash
flutter build apk --debug
```
The compiled APK will be located at `dist/mobile/MochiCompanion.apk` (and `build/app/outputs/flutter-apk/app-debug.apk`).

---

## 📁 Repository Structure

```
Mochi_Desktop_Pet/
├── .github/workflows/       # Automated CI/CD release workflow
├── build/                   # Build scripts, Windows shortcut installer, icon assets
│   ├── build.bat            # Automated PyInstaller build script
│   ├── generate_icon.py     # Procedural multi-resolution ICO generator
│   ├── icon.ico             # Desktop icon file
│   └── install_shortcut.py  # Windows Start Menu & Search integration script
├── core/                    # Core logic engine & platform abstraction
│   ├── pal/                 # Platform Abstraction Layer (Display, Window, IPC)
│   ├── config.py            # JSON configuration manager with fallback recovery
│   ├── engine.py            # Main application coordinator & game loop
│   ├── fsm.py               # Finite State Machine (Idle, Wandering, Corner, Focus)
│   ├── hotkeys.py           # Win32 RegisterHotKey global shortcut manager
│   ├── physics.py           # Kinematics engine (gravity, drag, fling, snug docking)
│   └── stats.py             # Circadian cycle, happiness, and energy tracker
├── dist/                    # Standalone production binaries
│   ├── DesktopPet.exe       # Zero-install Windows binary
│   └── config.json          # Default configuration
├── mobile/                  # Mobile Companion (Wispr Flow Architecture)
│   └── flutter_companion/   # Flutter cross-platform companion
│       ├── android/         # Android runner with native FloatingPetService.kt
│       ├── lib/             # Flutter UI, bunny painter, and pet state
│       └── pubspec.yaml     # Dependencies
├── tests/                   # 26 automated unit tests (100% green test suite)
├── ui/                      # Presentation layer
│   ├── canvas_renderer.py   # Procedural vector drawing & wearable accessories
│   ├── settings_dialog.py   # Modern Preferences & Wardrobe visual suite
│   ├── tray.py              # System tray integration & menu
│   └── window.py            # Frameless shaped transparent canvas window
├── config.json              # Active configuration file
├── main.py                  # Desktop application entry point
├── requirements.txt         # Python dependencies
├── ROADMAP.md               # Architectural roadmap for macOS, Linux, and iOS
└── README.md                # Project documentation
```

---

## 🗺️ What's Next?

* **macOS & Linux PAL**: Native frameless window transparency using PySide6/Qt.
* **Desktop ↔ Mobile Sync**: Sync happiness streaks, focus time, and outfits across PC and phone.
* **iOS Live Activities**: Dynamic Island companion on iPhone 14 Pro/15/16.

For full architectural details, see **[ROADMAP.md](ROADMAP.md)**.

---

## 📄 License

This project is open-source under the **MIT License**. Free to use, modify, and share! 💖
