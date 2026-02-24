# リリース手順・バージョニングルール

## バージョニング規則

SpeakDrop は [Semantic Versioning (semver)](https://semver.org/lang/ja/) に従います。

```
vMAJOR.MINOR.PATCH[-PRE_RELEASE.N]
```

| フィールド | 変更タイミング |
|----------|-------------|
| `MAJOR` | 後方互換性のない変更（破壊的変更） |
| `MINOR` | 後方互換性を保った機能追加 |
| `PATCH` | バグ修正のみ |
| `-PRE_RELEASE.N` | プレリリース版の連番（例: `-pre.1`, `-beta.2`, `-rc.1`） |

### タグ名の例

| タグ | 種別 |
|-----|------|
| `v1.0.0` | 安定版リリース |
| `v1.0.0-pre.1` | プレリリース |
| `v1.0.0-beta.1` | ベータリリース |
| `v1.0.0-rc.1` | リリース候補 |
| `v0.1.0-pre.1` | 初期プレリリース |

> プレリリースの判定条件: タグ名に `-` が含まれる場合（GitHub Actions の `contains(github.ref_name, '-')` を使用）

---

## GitHub Actions リリースワークフロー

### トリガー条件

`v` で始まるタグを push したとき自動実行されます。

```bash
# タグを作成して push するだけでビルドが走る
git tag v1.0.0
git push origin v1.0.0
```

`.github/workflows/release.yml` が実行するステップ:

1. コードをチェックアウト
2. uv 0.5.5 をインストール
3. Python 3.11 をセットアップ
4. 依存関係を `uv sync` でインストール
5. PyInstaller 6.11.0 を追加インストール
6. macOS `.app` バンドルをビルド（`MACOSX_DEPLOYMENT_TARGET=13.0`）
7. `LSUIElement=true` を Info.plist に設定（メニューバーアプリ化）
8. `.zip` にアーカイブ（ファイル名: `SpeakDrop-{TAG}.zip`）
9. GitHub Releases ページを作成・アップロード

### 実行環境

| 項目 | 値 |
|-----|---|
| ランナー | `macos-14`（Apple Silicon M1） |
| Python | 3.11.x（uv 管理） |
| PyInstaller | 6.11.0（固定） |
| ターゲット OS | macOS 13.0 以降 |

---

## リリース作成手順

### 安定版リリース

```bash
# 1. main ブランチが最新であることを確認
git checkout main
git pull origin main

# 2. タグを付けて push
git tag v1.0.0
git push origin v1.0.0
```

### プレリリース

```bash
git tag v1.0.0-pre.1
git push origin v1.0.0-pre.1
```

### 注意事項

- タグ名に `/` が含まれる場合、ファイル名内では `-` に自動変換される
- ワークフロー完了後、GitHub Releases ページに `SpeakDrop-{TAG}.zip` が公開される
- プレリリースは GitHub 上で「Pre-release」マークが付く

---

## ビルド成果物

| ファイル | 内容 |
|--------|------|
| `SpeakDrop-{TAG}.zip` | `SpeakDrop.app` を含む ZIP アーカイブ |

`SpeakDrop.app` は macOS 13.0 以降の Apple Silicon Mac で動作します。Intel Mac（x86_64）では動作しません（`macos-14` ランナーは arm64 のみ）。

---

## 既知の問題・注意点

### PyInstaller デフォルトアイコンの欠如

PyInstaller 6.11.0 を uv でインストールした環境では、デフォルトアイコン（`icon-windowed.icns`）が欠如する場合があります。
ワークフローでは `--icon NONE` を指定して回避しています。

アプリにカスタムアイコンを設定する場合は、`.icns` ファイルを作成し `--icon assets/icon.icns` のように指定します。

### 未署名アプリの Gatekeeper 警告

署名なし・公証なしのため、初回起動時に Gatekeeper の警告が表示されます。
右クリック → 「開く」で起動できます。

---

## ローカルでのビルド確認

CI と同等の環境でローカルビルドをテストする手順:

```bash
# 依存関係の確認
uv sync
uv pip install "pyinstaller==6.11.0"

# ビルド
MACOSX_DEPLOYMENT_TARGET=13.0 uv run pyinstaller \
  --windowed \
  --icon NONE \
  --name "SpeakDrop" \
  --osx-bundle-identifier "com.speakdrop.app" \
  --collect-all "rumps" \
  --collect-all "pynput" \
  --collect-all "sounddevice" \
  --collect-all "faster_whisper" \
  --collect-all "ctranslate2" \
  --collect-all "ollama" \
  --collect-all "PyObjCTools" \
  --hidden-import "AppKit" \
  --hidden-import "Cocoa" \
  --hidden-import "Quartz" \
  --hidden-import "Quartz.CoreGraphics" \
  --hidden-import "AVFoundation" \
  speakdrop/__main__.py

# LSUIElement 設定
/usr/libexec/PlistBuddy -c "Add :LSUIElement bool true" dist/SpeakDrop.app/Contents/Info.plist 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Set :LSUIElement true" dist/SpeakDrop.app/Contents/Info.plist
```
