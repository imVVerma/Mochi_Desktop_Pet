"""
Installer script to create Windows Start Menu, Desktop, and Startup shortcuts for Mochi Desktop Pet.
Enables Windows Search Bar integration (searching 'Mochi') and global hotkey triggering.
"""
import ctypes
import json
import os
import sys
import subprocess


def install_shortcuts(enable_startup: bool = True, custom_hotkey: str = None) -> None:
    ws = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    target_exe = os.path.join(ws, "dist", "DesktopPet.exe")
    icon_path = os.path.join(ws, "build", "icon.ico")
    config_file = os.path.join(ws, "config.json")

    # Read hotkey from config if not explicitly provided
    hotkey = custom_hotkey
    if not hotkey and os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                hotkey = cfg.get("hotkeys", {}).get("toggle_visibility", "Alt+Q")
        except Exception:
            hotkey = "Alt+Q"

    if not os.path.exists(target_exe):
        print(f"[ERROR] Target binary not found at: {target_exe}")
        sys.exit(1)

    appdata = os.environ.get("APPDATA", "")
    userprofile = os.environ.get("USERPROFILE", "")

    start_menu_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs")
    desktop_dir = os.path.join(userprofile, "Desktop")
    startup_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

    # Format hotkey for Windows Shell shortcut (Capitalized e.g. 'Alt+Q' or 'Ctrl+Shift+B')
    formatted_hotkey = ""
    if hotkey:
        formatted_hotkey = "+".join(p.capitalize() for p in hotkey.replace("+", " ").split())

    shortcuts = [
        ("Start Menu", os.path.join(start_menu_dir, "Mochi Desktop Pet.lnk"), formatted_hotkey),
        ("Desktop", os.path.join(desktop_dir, "Mochi Desktop Pet.lnk"), ""),
    ]

    if enable_startup:
        shortcuts.append(("Startup", os.path.join(startup_dir, "Mochi Desktop Pet.lnk"), ""))

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
        vbs_commands.append('oLink.Description = "Mochi Desktop Pet - Virtual Desk Companion"')
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
            print("[SUCCESS] Installed shortcuts for Mochi Desktop Pet:")
            for name, lnk_path, hk in shortcuts:
                hk_info = f" (Hotkey: {hk})" if hk else ""
                print(f"  - {name}: {lnk_path}{hk_info}")
            print("\nYou can now press the Win key, search 'Mochi', and launch directly!")
            if formatted_hotkey:
                print(f"Global in-app & shortcut hotkey '{formatted_hotkey}' is configured.")

            # Flush Windows Shell shortcut cache
            if sys.platform == "win32":
                try:
                    # SHCNE_ALLEVENTS = 0x08000000, SHCNF_FLUSH = 0x1000
                    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x1000, None, None)
                    print("Refreshed Windows Shell shortcut table.")
                except Exception:
                    pass
        else:
            print(f"[ERROR] Failed creating shortcuts: {res.stderr}")
    finally:
        if os.path.exists(temp_vbs):
            os.remove(temp_vbs)


if __name__ == "__main__":
    enable_startup = "--no-startup" not in sys.argv
    custom_hk = None
    if "--hotkey" in sys.argv:
        idx = sys.argv.index("--hotkey")
        if idx + 1 < len(sys.argv):
            custom_hk = sys.argv[idx + 1]
    install_shortcuts(enable_startup=enable_startup, custom_hotkey=custom_hk)
