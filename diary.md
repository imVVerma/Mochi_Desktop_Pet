# 📖 Development Diary: Desktop & Mobile Pet Companion

A living development log of every session, design decision, architectural pivot, and milestone achieved across the Windows Desktop Pet and Android Flutter Companion ecosystem.

---

## 📅 Session 1: Genesis & Windows Core Engine (Nov 15–18, 2024)
**Focus:** Prototyping the desktop pet, window physics, and Windows shell ergonomics.

* **Highlights & Achievements:**
  * Created the foundational Floppy Bunny desktop pet utilizing Python 3 and PyQt6.
  * Implemented procedural vector animation loop: idle breathing rhythm, eye blinking intervals, and loafing relaxation states.
  * Engineered DPI-aware taskbar docking so Mochi docks cleanly in the bottom-right corner of the primary display without clipping behind the Windows taskbar.
  * Added auto-docking physics: Mochi automatically loafs in the corner after inactivity and wakes up when clicked.
  * Built Windows Search bar integration, single-key `Shift+Tab` IPC toggle, and global customizable 2-key hotkeys.
  * Added Windows Shell startup shortcut creation and bundled a Windows system tray icon via `pystray`.

---

## 📅 Session 2: Wardrobe Customization & Live Avatar Previews (Nov 19–20, 2024)
**Focus:** Player expression, settings GUI, and CI/CD distribution.

* **Highlights & Achievements:**
  * Built an in-app Preferences & Wardrobe GUI dialog featuring an interactive hotkey recorder and color palette picker.
  * Implemented a live animated avatar preview inside the Wardrobe modal so users can test fur colors and hotkeys in real time.
  * Added automated Windows Search title synchronization.
  * Created GitHub Actions CI/CD release workflow (`.github/workflows/build.yml`) to automatically compile and release standalone zero-install Windows binaries (`DesktopPet.exe`).

---

## 📅 Session 3: Wearable Accessories, Habits Tracker & Cross-Platform PAL (Nov 21–22, 2024)
**Focus:** Wearables, habit streaks, and architecting multi-platform expansion.

* **Highlights & Achievements:**
  * Introduced 6 wearable accessories with custom procedural renderers:
    1. 👑 Royal Golden Crown with ruby accent.
    2. 🎀 Silk Ribbon Bow.
    3. 🌸 Sakura Cherry Blossom with pollen center.
    4. 👓 Smart Academic Glasses.
    5. 🎩 Gentleman's Top Hat with crimson band.
    6. 🧣 Cozy Winter Scarf.
  * Enhanced taskbar-clock docking so Mochi sits comfortably above the Windows system clock without obscuring tray icons.
  * Built an interactive Habits Tracker featuring streak cards and daily check-ins.
  * Designed the Platform Abstraction Layer (PAL) decoupling pet logic from OS-specific rendering engines to prepare for mobile expansion.

---

## 📅 Session 4: Flutter Companion & Native Android Overlay (Nov 23–24, 2024)
**Focus:** Mobile companion app and Android floating screen overlay.

* **Highlights & Achievements:**
  * Established `mobile/flutter_companion/` using Flutter 3.x and Material 3.
  * Developed native Android Kotlin runner (`android/app/src/main/kotlin/com/mochi/companion/`).
  * Created `FloatingPetService` (Android foreground service) utilizing `WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY` (`SYSTEM_ALERT_WINDOW`).
  * Bridged Flutter dashboard and native Android overlay via `MethodChannel` (`com.mochi.companion/overlay`).
  * Implemented touch handling with dragging, edge snapping, single-tap petting, and double-tap treat feeding.

---

## 📅 Session 5: APK Review, Size Optimization & State Unification (Nov 24–25, 2024)
**Focus:** Addressing external technical review, unifying state, and slashing APK binary footprint.

* **Highlights & Achievements:**
  * Reviewed audit points from `APK file analysis.md`.
  * **Unified State:** Built `PetStatsManager.kt` as the single source of truth for happiness, energy, focus minutes, wardrobe, screen coordinates, and circadian decay across app reboots.
  * **Squash & Stretch Physics:** Added dynamic `OvershootInterpolator` scale physics on petting, feeding, and dragging.
  * **Dramatic Size Reduction (148.6 MB → 16.8 MB):**
    * *Ahead-Of-Time (AOT) Machine Code Compilation:* Stripped out JIT compiler and debug runtime using `--release`.
    * *Architecture-Specific ABI Splitting:* Used `--split-per-abi` to package dedicated `arm64-v8a` native binaries.
    * *Engine & Diagnostic Layer Pruning:* Removed widget inspector trees, debug asserts, and diagnostic symbol tables.
    * *Procedural Rendering:* Eliminated heavy sprite sheets and video files in favor of lightweight vector math.

---

## 📅 Session 6: App Launcher Icon & Dynamic Text Wrapping (Nov 25, 2024)
**Focus:** Visual identity and UI robustness across high font scaling and native canvas bounds.

* **Highlights & Achievements:**
  * **Custom Mochi Launcher Icon:** Created `build/generate_android_icons.py` and generated high-resolution pastel Mochi icons across all Android densities (`mdpi`, `hdpi`, `xhdpi`, `xxhdpi`, `xxxhdpi`), replacing default Flutter launcher assets.
  * **Native Overlay Text Overflow Fix:** Replaced single-line `canvas.drawText` with Android `StaticLayout`, allowing multi-line text wrapping with dynamic bubble padding and height.
  * **Overlay Headroom Expansion:** Increased overlay window dimensions to `145dp × 160dp` in `FloatingPetService.kt` to prevent tall ears or long messages from clipping.
  * **Companion UI Overflow Fix:** Wrapped speech bubbles in `ConstrainedBox(maxWidth: 220)` and action buttons in `FittedBox(fit: BoxFit.scaleDown)` to gracefully accommodate accessibility font sizes.

---

## 📅 Session 7: Multi-Character Sprite Engine & Full-Body vs Face-Only Architecture (Nov 25, 2024 — Current)
**Focus:** Multi-character roster, app/overlay rendering bifurcation, and extensible AI sprite pipeline.

* **Context & Inspiration:**
  * Studied the open-source community pet registry [`awesome-codex-pet`](https://github.com/legeling/awesome-codex-pet.git), adopting its modular pet manifest and grid convention philosophy.
* **Architectural Decisions:**
  * **App Dashboard = Full-Body Mode:** The in-app sanctuary displays the full character body (ears, head, chubby torso, paws, animated tail, and accessories) for rich, immersive interaction.
  * **Floating Overlay = Face-Only Mode:** The floating system overlay displays only the character's compact circular head/face badge with distinct ears, facial expressions, and headwear. This keeps the on-screen pet sleek, unobtrusive, and non-distracting during web browsing or messaging.
  * **Character Roster:**
    1. 🐰 **Mochi (Floppy Bunny):** Droopy ears with momentum, pink inner pads, blush cheeks, cotton-ball tail.
    2. 🐱 **Luna (Neko Kitty):** Pointy triangular ears with pink lining, whisker lines on cheeks, curled tail, `:3` smile.
    3. 🐶 **Kiko (Shiba Doggo):** Perky golden ears, white eyebrow crests, snout with cute tongue blep, curled ringlet tail.
    4. 🐼 **Bao (Chubby Panda):** Round dark ears, iconic black eye patches, white chubby head, dark torso vest, stubby tail.
  * **AI / Photo Upload Extensibility:** Established `SpriteCharacterModel` specification to allow future users to upload any photo, clipart, or drawing and have an LLM convert it into full-body and face-badge sprite configurations.
  * **Living Diary:** Initialized this `diary.md` to permanently document all past and future development phases.
