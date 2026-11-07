@echo off
setlocal
cd /d "%~dp0"
echo [NOVEL STUDIO] Windows EXE build
where py >nul 2>nul
if errorlevel 1 (
 echo Python launcher not found. Install Python 3.11 or newer.
 pause
 exit /b 1
)
py -m pip install --upgrade pyinstaller pywebview
if errorlevel 1 goto fail
py -m PyInstaller --noconfirm --clean --windowed --onedir --name NOVEL_STUDIO --add-data "static;static" --hidden-import webview.platforms.edgechromium desktop.py
if errorlevel 1 goto fail
echo.
echo Build complete: dist\NOVEL_STUDIO\NOVEL_STUDIO.exe
echo Keep the entire dist\NOVEL_STUDIO folder together.
pause
exit /b 0
:fail
echo Build failed. Review the error messages above.
pause
exit /b 1
