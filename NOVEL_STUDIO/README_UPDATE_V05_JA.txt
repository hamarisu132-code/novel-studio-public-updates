NOVEL STUDIO v0.5.0 - Windows updater prototype

目的: 一度アップデータをEXE化すれば、次回以降は公開GitHub Releasesの
完成済みWindowsアプリZIPをダウンロードして入れ替えます。

最初の1回（Windows）:
1. BUILD_WINDOWS_V05.bat を実行する。
2. dist/LAUNCHER フォルダ全体を安全な場所へコピーする。
3. OPEN_NOVEL_STUDIO.bat でアプリを起動する。
4. 更新時はアプリを閉じ、NOVEL_STUDIO_UPDATER.exe を起動する。

重要:
- 自動更新はまだアプリ内ボタンではなく、別EXEを手動起動する試験版です。
- 最新Releaseに NOVEL_STUDIO_Windows.zip がない場合は更新されません。
- 現在のアプリは v0.5.0 なので、更新試験には v0.5.1 以降のReleaseが必要です。
- Release ZIPには NOVEL_STUDIO.exe と _internal/ を直下に入れてください。
- GitHub Actionsを使うには、このプロジェクトのソースコードと
  .github/workflows/windows-release.yml を公開リポジトリに配置する必要があります。
  公開リポジトリにコードを置くと誰でも閲覧できます。非公開の原稿は含めないでください。
- 原稿DBは %LOCALAPPDATA%/NovelStudio/novel_studio.db に保存され、
  更新処理はこのフォルダを変更しません。
- 更新後の旧アプリは NOVEL_STUDIO.previous として残ります。
  次の更新前には別の場所に移動して保管してください。
- GitHub releaseのSHA256 digestはダウンロード破損の検出です。
  ソフトウェア発行者の本人確認や署名検証の代替ではありません。
- Windows実機での更新試験は未実施。必ず最初はテスト環境で確認してください。
