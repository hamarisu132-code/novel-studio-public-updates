@echo off
setlocal
cd /d "%~dp0"
py -m pip install pyinstaller
if errorlevel 1 goto fail
py -m PyInstaller --noconfirm --clean --onefile --console --name NOVEL_STUDIO_UPDATER updater.py
if errorlevel 1 goto fail
echo Built: dist\NOVEL_STUDIO_UPDATER.exe
pause
exit /b 0
:fail
echo Build failed.
pause
exit /b 1
