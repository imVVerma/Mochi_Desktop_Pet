@echo off
echo ===================================================
echo   Desktop Pet: Standalone Executable Build Script
echo ===================================================

cd /d "%~dp0\.."

echo [1/3] Generating application icon...
.venv\Scripts\python.exe build\generate_icon.py

echo [2/3] Compiling standalone executable with PyInstaller...
.venv\Scripts\pyinstaller.exe --noconsole --onefile ^
    --name "DesktopPet" ^
    --icon "build\icon.ico" ^
    --add-data "config.json;." ^
    --hidden-import "PIL" ^
    --hidden-import "pystray" ^
    --clean ^
    main.py

echo [3/3] Build finished! Executable available at dist\DesktopPet.exe
echo ===================================================
pause
