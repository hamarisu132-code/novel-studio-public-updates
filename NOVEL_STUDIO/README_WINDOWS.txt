NOVEL STUDIO - Windows EXE build edition (0.3 preview)

1. Unzip this package to a normal folder, e.g. Desktop\NovelStudioBuild.
2. Install Python 3.11+ on Windows if needed (with py launcher).
3. Double-click BUILD_EXE_WINDOWS.bat. Internet is needed for the first dependency installation.
4. Run dist\NOVEL_STUDIO\NOVEL_STUDIO.exe.
5. Close the app window to stop its local HTTP server. No PowerShell window is required when running the EXE.

Data: %LOCALAPPDATA%\NovelStudio\novel_studio.db
Daily database backup: %LOCALAPPDATA%\NovelStudio\backups\

Migration: When no destination DB exists, the app tries to copy an existing database from a data folder next to the EXE or build source. Copy the old v0.2 data folder next to the new EXE folder (or beside desktop.py) before first launch. Keep an independent copy of the old folder. Migration is non-destructive; original DB remains unchanged.

Note: This is a Windows build-ready source package, NOT a prebuilt EXE. PyInstaller Windows builds must be performed on Windows. Windows execution and pywebview UI have not been tested here. Existing v0.2 editor/API functionality is retained; full history/trash/import/AI features from the roadmap are not yet implemented.

Security: The HTTP server binds only to 127.0.0.1 with a random available port. This is for single-user desktop use, not multi-user/network deployment. Other processes running under the same PC account may access the local service.
