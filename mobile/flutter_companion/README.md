# Mochi Companion for Android

The Flutter app is the companion's home screen and control panel. It lets you choose a character, customize its color and accessory, interact with it, and enable or dismiss the floating Android overlay.

## Current experience

- The sanctuary screen shows the active character, happiness, energy, and focus minutes for the day.
- The full-body character stays in a dedicated hero area; dragging and snapping are confined there so it cannot cover the dashboard controls. The screen scrolls on shorter displays.
- Pet and treat actions update the companion's state through the Android method channel.
- Petting, feeding, and completed focus sessions trigger a short bounce reaction.
- The focus action starts a 25-minute countdown. It can be paused and resumed; focus minutes are recorded only when the countdown completes.
- Character and wardrobe selections are shared with the native overlay service.
- The overlay permission prompt explains why Android asks for display-over-other-apps access.

The focus countdown currently lives in the Flutter app process. If Android closes the app process before the countdown completes, that in-progress session is not restored. Completed focus minutes are stored by the native stats manager.

## Build and run

```bash
flutter pub get
flutter run
```

Build a release APK with:

```bash
flutter build apk --release
```

For smaller per-device release packages, use `flutter build apk --release --split-per-abi`. The resulting APKs are written under `build/app/outputs/flutter-apk/`.

## Main UI files

- `lib/main.dart` — sanctuary screen, overlay controls, wardrobe, interactions, and focus countdown.
- `lib/pet_state.dart` — app-side companion state and color conversion.
- `lib/pet_painter.dart` — full-body character rendering and idle animation.
- `android/app/src/main/kotlin/com/mochi/companion/` — overlay service, touch handling, and persisted companion stats.
