@echo off
echo ===================================================
echo   Desktop Pet: Standalone Executable Build Script
echo ===================================================

cd /d "%~dp0\.."

echo [1/3] Generating application icon...
.venv\Scripts\python.exe build\generate_icon.py
if errorlevel 1 (
    echo [ERROR] Icon generation failed.
    exit /b 1
)

echo [2/3] Compiling standalone executable with PyInstaller...
.venv\Scripts\pyinstaller.exe --noconsole --onefile ^
    --name "DesktopPet" ^
    --icon "build\icon.ico" ^
    --add-data "config.json;." ^
    --hidden-import "PIL" ^
    --hidden-import "pystray" ^
    --hidden-import "pystray._win32" ^
    --clean ^
    main.py
if errorlevel 1 (
    echo [ERROR] PyInstaller failed. Close any running DesktopPet.exe and try again.
    exit /b 1
)
if not exist "dist\DesktopPet.exe" (
    echo [ERROR] Build completed without producing dist\DesktopPet.exe.
    exit /b 1
)

echo [3/3] Build finished! Executable available at dist\DesktopPet.exe
echo ===================================================
