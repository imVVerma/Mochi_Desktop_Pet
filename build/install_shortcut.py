"""
Installer script to create Windows Start Menu, Desktop, and Startup shortcuts for Desktop Pet.
Enables Windows Search Bar integration (searching by pet name) and global hotkey triggering.
"""
import ctypes
import json
import os
import sys
import subprocess


def install_shortcuts(
    enable_startup: bool = True,
    custom_hotkey: str = None,
    pet_name: str = None,
    old_pet_name: str = None,
) -> None:
    ws = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    target_exe = os.path.join(ws, "dist", "DesktopPet.exe")
    icon_path = os.path.join(ws, "build", "icon.ico")
    config_file = os.path.join(ws, "config.json")

    # Read config if params not explicitly provided
    hotkey = custom_hotkey
    active_name = pet_name
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                if not hotkey:
                    hotkey = cfg.get("hotkeys", {}).get("toggle_visibility", "Alt+Q")
                if not active_name:
                    active_name = cfg.get("pet_name", "Mochi")
        except Exception:
            pass

    if not active_name:
        active_name = "Mochi"
    if not hotkey:
        hotkey = "Alt+Q"

    if not os.path.exists(target_exe):
        # Fallback to python runner if standalone exe not yet compiled
        target_exe = sys.executable

    appdata = os.environ.get("APPDATA", "")
    userprofile = os.environ.get("USERPROFILE", "")

    start_menu_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs")
    desktop_dir = os.path.join(userprofile, "Desktop")
    startup_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

    # Remove old shortcut name if pet was renamed
    if old_pet_name and old_pet_name.lower() != active_name.lower():
        old_shortcuts = [
            os.path.join(start_menu_dir, f"{old_pet_name} Desktop Pet.lnk"),
            os.path.join(desktop_dir, f"{old_pet_name} Desktop Pet.lnk"),
            os.path.join(startup_dir, f"{old_pet_name} Desktop Pet.lnk"),
            # Also check generic default
            os.path.join(start_menu_dir, "Mochi Desktop Pet.lnk"),
            os.path.join(desktop_dir, "Mochi Desktop Pet.lnk"),
            os.path.join(startup_dir, "Mochi Desktop Pet.lnk"),
        ]
        for old_lnk in old_shortcuts:
            try:
                if os.path.exists(old_lnk):
                    os.remove(old_lnk)
            except Exception:
                pass

    # Format hotkey for Windows Shell shortcut (Capitalized e.g. 'Alt+Q' or 'Ctrl+Shift+B')
    formatted_hotkey = ""
    if hotkey:
        formatted_hotkey = "+".join(p.capitalize() for p in hotkey.replace("+", " ").split())

    shortcut_filename = f"{active_name} Desktop Pet.lnk"

    shortcuts = [
        ("Start Menu", os.path.join(start_menu_dir, shortcut_filename), formatted_hotkey),
        ("Desktop", os.path.join(desktop_dir, shortcut_filename), ""),
    ]

    if enable_startup:
        shortcuts.append(("Startup", os.path.join(startup_dir, shortcut_filename), ""))

    vbs_commands = []
    vbs_commands.append('Set oWS = WScript.CreateObject("WScript.Shell")')

    for name, lnk_path, hk in shortcuts:
        os.makedirs(os.path.dirname(lnk_path), exist_ok=True)
        esc_lnk = lnk_path.replace('"', '""')
        esc_target = target_exe.replace('"', '""')
        esc_ws = ws.replace('"', '""')
        esc_icon = icon_path.replace('"', '""')

        vbs_commands.append(f'Set oLink = oWS.CreateShortcut("{esc_lnk}")')
        vbs_commands.append(f'oLink.TargetPath = "{esc_target}"')
        vbs_commands.append(f'oLink.WorkingDirectory = "{esc_ws}"')
        if os.path.exists(icon_path):
            vbs_commands.append(f'oLink.IconLocation = "{esc_icon}"')
        vbs_commands.append(f'oLink.Description = "{active_name} Desktop Pet - Virtual Desk Companion"')
        if hk:
            vbs_commands.append(f'oLink.Hotkey = "{hk}"')
        vbs_commands.append('oLink.Save')

    vbs_script = "\n".join(vbs_commands)
    temp_vbs = os.path.join(ws, "build", "_temp_shortcut.vbs")

    try:
        with open(temp_vbs, "w", encoding="utf-8") as f:
            f.write(vbs_script)

        res = subprocess.run(["cscript", "//nologo", temp_vbs], capture_output=True, text=True)
        if res.returncode == 0:
            # Flush Windows Shell shortcut cache
            if sys.platform == "win32":
                try:
                    # SHCNE_ALLEVENTS = 0x08000000, SHCNF_FLUSH = 0x1000
                    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x1000, None, None)
                except Exception:
                    pass
            return True
        else:
            return False
    finally:
        if os.path.exists(temp_vbs):
            os.remove(temp_vbs)


if __name__ == "__main__":
    enable_startup = "--no-startup" not in sys.argv
    custom_hk = None
    pet_name = None
    if "--hotkey" in sys.argv:
        idx = sys.argv.index("--hotkey")
        if idx + 1 < len(sys.argv):
            custom_hk = sys.argv[idx + 1]
    if "--name" in sys.argv:
        idx = sys.argv.index("--name")
        if idx + 1 < len(sys.argv):
            pet_name = sys.argv[idx + 1]

    ok = install_shortcuts(enable_startup=enable_startup, custom_hotkey=custom_hk, pet_name=pet_name)
    if ok:
        print("[SUCCESS] Windows shortcuts updated successfully.")
