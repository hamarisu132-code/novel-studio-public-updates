NOVEL STUDIO 0.4 updater foundation
===================================
This is an updater foundation, NOT a working automatic update service.
No GitHub release URL has been configured, so no update can be fetched yet.

1. On Windows, build NOVEL STUDIO with BUILD_EXE_WINDOWS.bat.
2. Build updater with BUILD_UPDATER_WINDOWS.bat.
3. Keep NOVEL_STUDIO_UPDATER.exe OUTSIDE the NOVEL_STUDIO application folder,
   alongside the NOVEL_STUDIO folder. This is essential: the updater replaces
   the app folder while running.
4. Put update_config.json INSIDE the installed NOVEL_STUDIO folder.
5. After a release repository is set up, configure manifest_url with the HTTPS
   URL of the JSON manifest, and publish ZIP releases and their SHA256 hashes.
6. Close NOVEL STUDIO, then run the updater, and confirm the prompts.

IMPORTANT: This updater currently has a console confirmation UI, not an in-app
update button. It downloads ONLY after explicit confirmation. It does not upload
manuscripts. LocalAppData/NovelStudio is never modified by the updater.
Previous app binaries remain in a .previous folder after a successful update.
To roll back, close the app and rename the current app folder aside, then rename
.previous back to the original folder name. Database migrations may require a
separate restore; keep regular backups before any update.

Before publishing releases: review URL trust policy and sign release manifests.
A SHA256 in an unsigned remote manifest does not protect against compromise of
that manifest's publisher. Windows build/runtime remains unverified here.
