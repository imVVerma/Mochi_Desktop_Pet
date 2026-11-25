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

---

## Session 8: UI/UX Review and Focus Timer Correction (Nov 25, 2026)
**Focus:** Separate Windows and Android UX, fix misleading focus-session behavior, and align the documentation with the current implementation.

* **Windows `.exe`:** Clarified in the preferences header that the avatar is a preview and changes apply to Mochi only after **Save & Apply**. This prevents the dialog preview from implying that the running pet has already changed.
* **Android APK:** Replaced the focus action's immediate credit with a 25-minute countdown that can be paused and resumed. Focus minutes are now recorded only after completion. The screen reports paused and completed states, and focus minutes display as a value instead of a misleading full progress bar.
* **Android visual consistency:** Set the Material theme seed to the lavender accent already used by the character selector and primary overlay action.
* **Documentation:** Replaced the default Flutter README with a product-specific guide, documented the focus timer's process-lifetime limitation, described the current mobile focus flow in the root README, and added a platform-separated UI/UX direction and implementation order.
* **Review notes for follow-up:** The desktop renderer's normal idle color cycle can compete with a user-selected fur color; the in-app avatar overlap was addressed in Session 9; and a running focus countdown is not restored if Android kills the app process. These remain separate follow-up items.
* **Files edited:** `mobile/flutter_companion/lib/main.dart`, `mobile/flutter_companion/README.md`, `ui/settings_dialog.py`, `README.md`, `UI_UX_PLAN.md`, and `diary.md`.
* **Verification:** No test suite or build was run in this session.

---

## Session 9: Android Sanctuary Layout and Interaction Motion (Nov 25, 2026)
**Focus:** Keep the in-app companion clear of dashboard controls and add restrained feedback animations.

* **Android layout:** Replaced the full-screen floating avatar placement with a dedicated hero area in the sanctuary flow. Pet dragging and edge snapping are bounded to this region, while the page scrolls when the available height is short.
* **Interaction motion:** Added a short bounce reaction when petting, feeding, and completing a focus session. The existing idle breathing and blink loop remains the ambient motion.
* **Documentation:** Updated the Android and root READMEs and marked the completed work in `UI_UX_PLAN.md`.
* **Files edited:** `mobile/flutter_companion/lib/main.dart`, `mobile/flutter_companion/README.md`, `README.md`, `UI_UX_PLAN.md`, and `diary.md`.
* **Verification:** Dart formatting completed. No test suite or APK build was run in this session.

---

## Session 10: Test Build Versioning and Windows Preview Visibility (Nov 25, 2026)
**Focus:** Make the updated APK install over the user's existing Android build and make the Windows preview notice easier to find.

* **Android APK:** The user's device reported installed version code `2001` while the generated APK was `1`. Bumped the Flutter version to `1.0.1+2002` and successfully built a release APK at `mobile/flutter_companion/build/app/outputs/flutter-apk/app-release.apk` (45.0 MB).
* **Windows EXE:** Changed the settings subtitle to bold lavender `PREVIEW • Save & Apply updates Mochi`. A normal build could not replace the existing `dist/DesktopPet.exe` because Windows denied access to that file, even after an elevated retry. Built a separate updated executable at `build/desktop_preview/dist/DesktopPet-Preview.exe` so the existing binary is preserved.
* **Build script:** Added error checks to `build/build.bat`; it now exits on icon or PyInstaller failure instead of printing a false success message.
* **Documentation:** Corrected the Android release APK path and documented the current version code and install command.
* **Files edited:** `mobile/flutter_companion/pubspec.yaml`, `mobile/flutter_companion/README.md`, `ui/settings_dialog.py`, `build/build.bat`, `README.md`, and `diary.md`.
* **Verification:** Release APK and separate Windows preview EXE built successfully. Installed the release APK to the connected Android device via ADB. Standard EXE replacement failed with `PermissionError` on `dist/DesktopPet.exe`; the alternate preview EXE is available for review. No automated test suite was run.
