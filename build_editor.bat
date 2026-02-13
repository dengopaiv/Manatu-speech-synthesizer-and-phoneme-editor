@echo off
REM Build Phoneme Editor as standalone EXE
REM Requires: pip install pyinstaller

echo Building Phoneme Parameter Editor...

REM Check for PyInstaller
where pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Build the EXE
pyinstaller --onefile --windowed ^
    --name "PhonemeEditor" ^
    --add-data "speechPlayer.dll;." ^
    --add-data "presets;presets" ^
    --icon "NONE" ^
    phoneme_editor.py

echo.
echo Build complete! Check the 'dist' folder for PhonemeEditor.exe
echo.
pause
