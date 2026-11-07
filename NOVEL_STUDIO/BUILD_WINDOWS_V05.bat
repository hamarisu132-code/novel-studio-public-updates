@echo off
setlocal
cd /d "%~dp0"
echo [NOVEL STUDIO] Build Windows app and standalone updater
py -m pip install pyinstaller pywebview
if errorlevel 1 goto fail
py -m PyInstaller --noconfirm --clean --windowed --onedir --name NOVEL_STUDIO --add-data "static;static" --add-data "version.json;." desktop.py
if errorlevel 1 goto fail
py -m PyInstaller --noconfirm --clean --console --onefile --name NOVEL_STUDIO_UPDATER --distpath "dist\LAUNCHER" --workpath "build\updater" --specpath "build\updater" updater.py
if errorlevel 1 goto fail
if not exist "dist\LAUNCHER\NOVEL_STUDIO" mkdir "dist\LAUNCHER\NOVEL_STUDIO"
xcopy /E /I /Y "dist\NOVEL_STUDIO\*" "dist\LAUNCHER\NOVEL_STUDIO\" >nul
copy /Y "OPEN_NOVEL_STUDIO.bat" "dist\LAUNCHER\OPEN_NOVEL_STUDIO.bat" >nul
echo.
echo SUCCESS: dist\LAUNCHER\OPEN_NOVEL_STUDIO.bat
echo Updater: dist\LAUNCHER\NOVEL_STUDIO_UPDATER.exe
echo Keep the entire LAUNCHER folder together.
pause
exit /b 0
:fail
echo BUILD FAILED
pause
exit /b 1
