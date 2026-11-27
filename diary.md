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

---

## Session 11: Windows and Android Distribution Assets (Nov 25, 2026)
**Focus:** Refresh the checked-in Windows binary, stage the versioned APK, and publish matching release assets.

* **Windows:** Replaced `dist/DesktopPet.exe` with the fresh preview build containing the visible settings-preview label.
* **Android:** Copied the successfully built version 1.0.1 / version code 2002 APK to `dist/mobile/MochiCompanion.apk` for the release upload.
* **GitHub release automation:** Extended the tag workflow to set up Java and Flutter, build the release APK, and attach it beside the Windows EXE. Updated the root README badge and release version note.
* **Release check follow-up:** The first GitHub run failed because the hosted Windows runner reported a 360px taskbar height from mismatched DPI coordinate spaces. Capped the PAL estimate at 120px so an implausible work-area difference cannot move the pet too far from the desktop edge.
* **Files edited:** `.github/workflows/release.yml`, `README.md`, `dist/DesktopPet.exe`, `dist/mobile/MochiCompanion.apk`, and `diary.md`.
* **Verification:** The APK was installed on the connected device. The first GitHub Actions run had 28 passing and 1 failing test; after the taskbar-height bound fix, all 29 tests passed. The v1.0.1 release published `DesktopPet.exe`, `MochiCompanion.apk`, and `config.json` successfully.

---

## Session 12: APK Technical Audit Remediation & Release Productionizing (Nov 25, 2026)
**Focus:** Address all findings from the comprehensive APK technical audit (lines 155+), covering circadian decay correctness, adaptive launcher icons, mood-reactive overlay visuals, monochrome notifications, release keystore signing, and ABI-split lean distribution.

* **Decay Math & State Mutation (P0):**
  * Removed side-effecting `applyCircadianDecay()` call from `PetStatsManager.toMap()`, ensuring read operations are pure.
  * Replaced total timestamp reset in decay logic with exact elapsed-time tracking (`val msConsumed = (decayPoints.toDouble() / 3.0 * 3600000.0).toLong()`), preserving sub-20-minute fractional decay intervals across repeated polls.
  * Updated `MainActivity.kt` to explicitly apply circadian decay when Flutter queries `getPetStats`.
* **Adaptive Launcher Icon (P0):**
  * Implemented official Android adaptive icon structure (`res/mipmap-anydpi-v26/ic_launcher.xml` and `ic_launcher_round.xml`) with separated background (`#FFF8E7`) and foreground vector (`ic_launcher_foreground.xml`).
  * Mochi's facial features and ears are positioned strictly within the 66dp safe zone (72dp inner boundary of the 108dp canvas), eliminating squircle/circle double-masking artifacts on modern Android launchers (API 26+).
* **Overlay Mood Visuals (P1):**
  * Enhanced `PetOverlayView.kt` with dynamic mood-reactive rendering responding to `happiness` and `energy`:
    * Breathing cycle dynamically scales between 1900ms (high energy/happy) and 3400ms (tired/sleepy).
    * Low energy (<30) adds sleepy eye arcs and ear droop; low happiness (<40) adds a subtle sweat/worry droplet and reduces blush opacity.
  * Synchronized mood state across care actions (petting, feeding, playing) and initial launch in `FloatingPetService.kt`.
* **Monochrome Notification Drawables (P1):**
  * Replaced Android stock system icons (`android.R.drawable.ic_dialog_info` and `android.R.drawable.ic_menu_close_clear_cancel`) with custom vector drawables `ic_notification_paw.xml` and `ic_notification_sleep.xml`.
  * Complies with Android status bar monochrome icon styling guidelines.
* **Release Keystore & Build Architecture (P2):**
  * Generated dedicated release keystore `mobile/flutter_companion/android/app/mochi-release.jks` with SHA-256 fingerprinting.
  * Configured `build.gradle.kts` with official `signingConfigs.release` reading environment variables or keystore file with graceful debug fallback.
  * Bumped Flutter project version to `1.0.2+2003`.
  * Updated `.github/workflows/release.yml` to build `--split-per-abi` release APKs (~17 MB per ABI vs 45 MB fat universal APK).
* **UI/UX Roadmap Preview & Documentation (P2):**
  * Updated `mobile/flutter_companion/lib/main.dart` to clarify the Character Forge feature card as a "✨ Roadmap Preview: AI Character Forge" with transparent notes on the planned secure proxy architecture.
  * Fixed typo in `UI_UX_PLAN.md` (removed stray `"some "`).
* **Files edited:**
  * `mobile/flutter_companion/android/app/src/main/kotlin/com/mochi/companion/PetStatsManager.kt`
  * `mobile/flutter_companion/android/app/src/main/kotlin/com/mochi/companion/MainActivity.kt`
  * `mobile/flutter_companion/android/app/src/main/kotlin/com/mochi/companion/PetOverlayView.kt`
  * `mobile/flutter_companion/android/app/src/main/kotlin/com/mochi/companion/FloatingPetService.kt`
  * `mobile/flutter_companion/android/app/src/main/res/values/colors.xml`
  * `mobile/flutter_companion/android/app/src/main/res/drawable/ic_launcher_foreground.xml`
  * `mobile/flutter_companion/android/app/src/main/res/drawable/ic_notification_paw.xml`
  * `mobile/flutter_companion/android/app/src/main/res/drawable/ic_notification_sleep.xml`
  * `mobile/flutter_companion/android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml`
  * `mobile/flutter_companion/android/app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml`
  * `mobile/flutter_companion/android/app/src/main/AndroidManifest.xml`
  * `mobile/flutter_companion/android/app/build.gradle.kts`
  * `mobile/flutter_companion/pubspec.yaml`
  * `mobile/flutter_companion/lib/main.dart`
  * `.github/workflows/release.yml`
  * `UI_UX_PLAN.md`
  * `.gitignore`
  * `diary.md`
* **Verification:**
  * Flutter unit tests passed (3/3).
  * Python test suite passed (29/29).
  * Built release APK with `--split-per-abi` (`app-arm64-v8a-release.apk` - 17.0 MB) signed with official keystore.
  * Staged artifact to `dist/mobile/MochiCompanion.apk`.

---

## Session 13: Desktop Pet Proportional Scaling & Clipping Prevention (Nov 27, 2026)
**Focus:** Fix clipping and cropping of Mochi in `DesktopPet.exe` across different user scales, outfits, and animation states.

* **Proportional Scaling in `CanvasRenderer`:**
  * Diagnosed root cause: `PetEngine` adjusted window and canvas dimensions based on `scale` (e.g., `scale = 0.7` shrunk the canvas to 98x98), but `CanvasRenderer.draw()` used fixed hardcoded pixel offsets designed for a 140px canvas. At 70% scale or during hopping/squashing/accessories, feet, ear tips, and hats were clipped outside the canvas borders.
  * Introduced uniform scale factor `s = max(0.4, min(self.width / 140.0, self.height / 140.0))` across all drawn elements (body, belly, tail, ears, paws/feet, whiskers, blush, eyes, pupils, nose, mouth, accessories, and particles).
* **Safe Margins & Headroom:**
  * Rebalanced base proportions to provide >=8px top headroom and >=15px bottom/side padding inside the canvas at 1.0x scale.
  * Tall accessories (Gentleman Top Hat, Royal Crown) and perked ear states now fit comfortably without touching the canvas edge.
* **Speech Bubble Boundary Clamping:**
  * Updated `SpeechBubble.draw()` in `ui/bubble.py` to scale font, padding, and tail with `s` and clamp positioning within canvas bounds (`[4, width - 4]` and `[3, height - 3]`), preventing speech bubbles from clipping off-screen.
* **Dynamic Scale Resizing in `PetEngine`:**
  * Updated `apply_preferences()` in `core/engine.py` to dynamically resize the window, canvas, physics bounds, and renderer when the user adjusts the scale slider in Settings, eliminating the need for an app restart.
  * Scaled mouse hover interaction distance with pet scale.
* **Files edited:**
  * `ui/canvas_renderer.py`
  * `ui/bubble.py`
  * `core/engine.py`
  * `dist/DesktopPet.exe`
  * `diary.md`
* **Verification:**
  * Full Python test suite passed (29/29).
  * Successfully rebuilt standalone executable `dist/DesktopPet.exe` via PyInstaller (17.9 MB).

---

## Session 14: Modern "Warm & Cozy" Preferences & Wardrobe Redesign (Nov 27, 2026)
**Focus:** Redesign the desktop application's "Mochi — Wardrobe & Preferences" dialog with a contemporary warm & cozy aesthetic, replacing harsh black borders with soft rounded cards, refined Mochi avatar illustration, capsule chips, and interactive styling.

* **Warm & Cozy Aesthetic Architecture:**
  * Replaced stark `#F6F7FB` window background and harsh black borders (`relief=tk.SOLID, bd=1`) with soft warm off-white/beige (`#FAF7F2`) and subtle borders (`#EDE4D8`).
  * Converted the dense rectangular sections into gently rounded, soft-beige cards with generous internal padding.
* **Refined Mochi Avatar Illustration:**
  * Updated vector preview canvas with cream-yellow coat (`#FFF4D2`), fuzzy natural inner ears (`#FCE4C8`), smooth outlines (`#4A3B32`, width=2), golden sparkles (`✨`, `✦`), and pink knitted scarf (`🧣 Cozy Scarf`).
  * Formatted header typography with friendly dark-navy title (`#1B2A4A`), `"Cozy Companion"` badge, and violet-purple subtitle (`#7C3AED` `PREVIEW • Save & Apply updates Mochi`).
* **Contemporary Styled Tabs:**
  * Re-themed ttk Notebook tabs: `🎨 Wardrobe & Outfits`, `⌨️ Hotkeys & Search`, and `⏳ Habits & Focus`.
  * Active tab highlighted in warm caramel (`#DE9B61`) with white text and hourglass icon; inactive tabs in warm beige (`#EFE8DE`).
* **Interactive "Habits & Focus" Controls:**
  * **Taskbar Roosting:** Added duration badge (`#FFF2E5` / `#D97706`), custom slider, and capsule chips (`5s (Quick)` active in soft orange `#FF9F68`, `15s`, `30s`, `60s`).
  * **Pomodoro Focus Timer:** Added duration badge (`25 min work`), smooth slider, and capsule chips (`15 min`, `25 min (Standard)` active in soft orange, `45 min`, `60 min`).
  * **Circadian Rhythm:** Styled Bedtime (23:00) and Wake Time (07:00) pill inputs with clean spinbox steppers.
  * **Wellness Speech Bubbles:** Integrated soft checkbox with `💧 Hydration`, `👁️ Eye Rests`, and `🧘 Posture Check` chip labels.
* **Refined Action Buttons:**
  * Warm coral pill **"Save & Apply ✦"** button (`#FF7E67`) paired with clean white **"Cancel"** button.
* **Preview Verification Workflow:**
  * Generated high-fidelity AI visual mockup and interactive Generative UI HTML artifact (`mochi_preferences_mockup.html`).
  * Created `preview_settings.py` for headless screenshot capture and live desktop testing.
  * Previewed and user-confirmed prior to building release binary.
* **Files edited:**
  * `ui/settings_dialog.py`
  * `preview_settings.py`
  * `dist/DesktopPet.exe`
  * `dist/mochi_settings_redesign_preview.png`
  * `diary.md`
* **Verification:**
  * Unit test suite passed (`tests/test_settings_dialog.py` passed).
  * Full Python test suite passed (`29/29 passed` in 56.0s).
  * Successfully rebuilt standalone executable `dist/DesktopPet.exe` via PyInstaller (17.9 MB).
