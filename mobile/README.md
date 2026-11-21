# 📱 Mochi Mobile Companion (Wispr Flow Model)

> An omnipresent, floating virtual desk companion for mobile, inspired by the interaction model of **Wispr Flow**.

---

## 🌟 The Mobile Companion Paradigm

On mobile operating systems, applications typically run in isolated full-screen sandboxes. **Wispr Flow** pioneered a breakthrough interaction pattern by floating a persistent companion bubble directly on top of all active apps (WhatsApp, Instagram, browser, notes).

Mochi adopts this exact mobile model:

```
               [ Android Device Screen ]
+-------------------------------------------------------+
|  Status Bar (Time, Battery, Wi-Fi)                    |
+-------------------------------------------------------+
|                                                       |
|   Active App: WhatsApp / Gmail / Browser / Notes      |
|                                                       |
|            (\\(\\                                     |
|           ( - . -)   <-- Floating Mochi Companion     |
|           o_(")(")       • Draggable anywhere         |
|                          • Parabolic fling physics    |
|                          • Auto-snaps to screen edge  |
|                          • Speech bubble cheer-ups    |
|                                                       |
|   [ Keyboard / Input Area ]                           |
+-------------------------------------------------------+
```

---

## 🎯 Architecture & Platform Strategies

### 1. Android: Floating Pet Bubble (`SYSTEM_ALERT_WINDOW`)
* **Overlay Window**: Built on Android's `WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY`.
* **Touch & Fling Kinematics**:
  * **Drag & Move**: Touch and drag Mochi anywhere on screen.
  * **Toss & Fling**: Fling with high velocity; Mochi computes parabolic deceleration and squashes against screen boundaries.
  * **Edge Docking (Resting Mode)**: When left inactive, Mochi folds into a gentle half-circle tab against the closest phone edge (just like Wispr Flow's Flow Bubble).
  * **Haptic Feedback**: Gentle haptic ticks upon petting, dragging, or edge docking.
* **Cheer-Up Speech Bubbles**: Periodic reminders for hydration, posture checks, and Pomodoro sprint counters floating above active apps.

### 2. iOS: Dynamic Island & Live Activities (`ActivityKit`)
* Because iOS strictly forbids drawing over third-party applications, Mochi lives in Apple's **Dynamic Island** (iPhone 14 Pro, 15, 16 series) and on the **Lock Screen**!
* **Dynamic Island Compact View**: Mochi's cute sleeping or happy bunny face rests inside the pill while you browse other apps.
* **Dynamic Island Expanded View**: Long-pressing the island expands Mochi into an interactive widget with quick Pomodoro timers, petting cheer-up, and quotes.

---

## 📂 Project Organization

```
mobile/
├── android_overlay/                 # Native Android Floating Window implementation
│   ├── AndroidManifest.xml          # Declares SYSTEM_ALERT_WINDOW & Foreground Service
│   ├── FloatingPetService.kt        # Foreground service managing WindowManager overlay
│   ├── OverlayTouchListener.kt      # Touch drag, velocity tracking, and edge docking
│   ├── PetOverlayView.kt            # Custom hardware-accelerated Canvas drawing Mochi
│   └── PetStatsManager.kt           # Circadian rhythms, Pomodoro, and wellness state
└── flutter_companion/               # Cross-Platform Flutter companion (Android + iOS)
    ├── pubspec.yaml                 # Flutter project configuration
    ├── lib/
    │   ├── main.dart                # Mobile companion application entry point
    │   ├── bunny_painter.dart       # 120 FPS CustomPainter drawing procedural Floppy Bunny
    │   └── overlay_bridge.dart      # Platform Channel bridge to native overlay services
```
