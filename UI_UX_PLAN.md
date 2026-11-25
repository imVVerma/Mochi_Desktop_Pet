# UI/UX Direction: Windows and Android

This plan keeps Mochi recognizable across platforms while giving each app controls suited to its screen and use.

## Shared visual language

- **Base surfaces:** warm cream (`#F7F5F0`) and white cards.
- **Primary action:** lavender (`#6C5CE7`), already used by the Android character selector and overlay action.
- **Character accents:** soft rose, peach, and sage for expressive details and secondary actions.
- **Typography and shape:** clear system fonts, readable labels, rounded cards, light shadows, and selection states that use both color and an icon or label.
- **Motion rule:** keep idle animation slow and low contrast; reserve larger movement and particles for deliberate interaction. Honor the platform's reduced-motion preference where available.

The Android Material theme now uses the existing lavender action color as its seed. Windows can retain its softer pink character palette while sharing the same cream, lavender, and muted accent family.

## Windows desktop app (`DesktopPet.exe`)

### Product feel

Treat the pet as a quiet desktop resident. The character should be visible at rest without competing with the user's work. Keep controls close at hand through the tray menu, context menu, and hotkeys.

### UI work

1. Keep the settings dialog's preview and the running pet state clearly distinct. The preview is local to the dialog until **Save & Apply**.
2. Simplify the context menu into interaction, focus/sleep, appearance, settings, and quit groups. Keep the current hotkey visible beside summon/dismiss.
3. Make the wardrobe's selected outfit and color obvious through a border plus a check or selected label.
4. Review the idle color behavior. A selected fur color should remain stable at rest; mood changes can use small, gradual shifts when auto-adapt is enabled.

### Motion

- Idle: slow breathing, occasional blink, and low-amplitude ear sway.
- Drag: ears trail the movement; release settles with a short squash and rebound.
- Pet: brief heart/sparkle response and a happy ear perk.
- Focus: a glasses adjustment and restrained focus cue on start; calm resting pose during the sprint.
- Dock: a short settling motion when Mochi reaches the taskbar corner.

## Android companion APK

### Product feel

Use the sanctuary as the home for care and customization, and the overlay as a compact companion that stays out of the way. The overlay should remain visually simpler than the in-app character.

### UI work

1. Keep the primary overlay status and summon/dismiss action prominent and consistent.
2. Reserve a predictable hero area for the character so dragging it cannot cover dashboard actions or stats. Keep drag-and-snap behavior in the system overlay.
3. Show happiness and energy as bounded values; show focus minutes as a number or against an explicit daily goal.
4. Make the focus session a clear start, pause/resume, completion flow. Persist an in-progress session if it should survive app process death.
5. Explain the overlay permission at the point of need and show whether Mochi became active after returning from Android settings.

### Motion

- Sanctuary idle: breathing, blinking, and gentle tail/ear motion.
- Pet: small bounce, brief hearts, and a short speech bubble.
- Treat: a quick anticipation hop followed by a happy reaction.
- Focus: calm glasses cue on start and a subtle completion celebration.
- Overlay: face-only blink and short interaction reactions; avoid constant particles and large movement.
- Drag: keep the existing edge docking and haptic tick; use a soft settle when the pet snaps to an edge.

## Implementation order

1. **Behavior and clarity:** focus lifecycle and accurate stat display are implemented; permission follow-through still needs review.
2. **Layout:** the in-app pet is confined to a dedicated hero area, and the dashboard scrolls when space is short. Larger text and speech-bubble clipping still need device review.
3. **Visual consistency:** apply the shared palette, selection, spacing, and card styles across the settings dialog and sanctuary.
4. **Motion polish:** add interaction-specific animation after layout and state transitions are stable.

## Implemented milestones

- Android focus now counts down for 25 minutes, supports pause/resume, and records only on completion. The active countdown is currently in memory and will not survive process termination.
- Android focus minutes display as a value instead of a progress bar without a defined goal.
- The Windows settings subtitle now states that the avatar is a preview and that **Save & Apply** updates the running pet.
- The Android sanctuary now reserves a bounded hero area for the character; dragging and edge snapping stay inside it, and the rest of the screen scrolls when needed.
- Petting, feeding, and completing a focus session play a short bounce reaction.

See `diary.md` for the session log and edited-file list.
