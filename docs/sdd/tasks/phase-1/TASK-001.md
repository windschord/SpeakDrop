# TASK-001: プロジェクトセットアップ

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**SpeakDropプロジェクトの基盤セットアップ** を実装してください。

### 実装の目標

`pyproject.toml`（uv管理）を作成し、全依存パッケージを定義します。
Pythonパッケージとして動作する `speakdrop/` ディレクトリ構造と `tests/` ディレクトリを作成します。
空のモジュールファイル（`__init__.py`、各モジュールのスタブ）を配置し、後続タスクが実装できる状態にします。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/pyproject.toml` | プロジェクト設定・依存関係定義 |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/__init__.py` | パッケージ初期化（空ファイル） |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/__main__.py` | エントリーポイントスタブ |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/app.py` | メインアプリスタブ |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/audio_recorder.py` | 音声録音スタブ |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/transcriber.py` | 音声認識スタブ |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/text_processor.py` | テキスト後処理スタブ |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/clipboard_inserter.py` | クリップボードスタブ |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/hotkey_listener.py` | ホットキースタブ |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/config.py` | 設定スタブ |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/permissions.py` | 権限チェックスタブ |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/icons.py` | アイコン生成スタブ |
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/tests/__init__.py` | テストパッケージ初期化 |

---

## 技術的コンテキスト

### 使用技術

- 言語: Python 3.11+
- パッケージ管理: uv
- コード品質: ruff + mypy (strict)
- テストフレームワーク: pytest + pytest-mock + pytest-cov

### 関連する設計書

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/design/design.md` の「プロジェクト構成」セクション（行111-140）
- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/design/design.md` の「pyproject.toml 設計」セクション（行638-686）

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [ ] `/Users/tsk/Sync/git/SpeakDrop/pyproject.toml` が設計書仕様通りに作成されている
- [ ] `speakdrop/` ディレクトリ以下に全10モジュールファイルが存在する
- [ ] `tests/__init__.py` が存在する
- [ ] `uv sync` が正常に完了する（依存解決できる）
- [ ] `uv run python -m speakdrop` が構文エラーなく動作する（スタブ段階でも可）
- [ ] `uv run ruff check .` でエラー0件
- [ ] `uv run mypy .` でエラー0件（スタブファイルはpass文のみでよい）

---

## 実装手順

### ステップ1: pyproject.toml を作成

設計書（`/Users/tsk/Sync/git/SpeakDrop/docs/sdd/design/design.md` 行638-686）に記載の仕様通り `pyproject.toml` を作成してください。

```toml
[project]
name = "speakdrop"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "rumps>=0.4.0",
    "pynput>=1.7.0",
    "sounddevice>=0.4.0",
    "faster-whisper>=1.0.0",
    "numpy>=1.24.0",
    "ollama>=0.3.0",
    "pyobjc-framework-Cocoa>=10.0",
    "pyobjc-framework-Quartz>=10.0",
    "pyobjc-framework-AVFoundation>=10.0",
]

[project.scripts]
speakdrop = "speakdrop.__main__:main"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-mock>=3.12.0",
    "pytest-cov>=4.0.0",
    "mypy>=1.0.0",
    "ruff>=0.4.0",
]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
source = ["speakdrop"]
omit = ["speakdrop/__main__.py"]

[tool.coverage.report]
fail_under = 80
```

### ステップ2: ディレクトリ構造とスタブファイルの作成

1. `speakdrop/__init__.py` - 空ファイル（`# SpeakDrop package` のコメントのみ）
2. 各スタブファイルはクラス定義と `pass` のみ（型ヒントのimportも含める）
3. `tests/__init__.py` - 空ファイル

### ステップ3: uv sync の実行

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv sync
```

### ステップ4: 品質チェック

```bash
uv run ruff check .
uv run mypy .
```

### ステップ5: コミット

```
chore: プロジェクトセットアップ（pyproject.toml・ディレクトリ構造）
```

---

## 実装の詳細仕様

### スタブファイルの形式

各モジュールのスタブは以下の形式で作成してください：

```python
"""モジュールの説明（docstring）。"""
# 将来の実装でimportされる型ヒントのみを記載


class ClassName:
    """クラスの説明。"""

    pass
```

### __main__.py スタブ

```python
"""SpeakDrop エントリーポイント。"""


def main() -> None:
    """アプリケーションを起動する。"""
    pass


if __name__ == "__main__":
    main()
```

### 入出力仕様

**入力:** なし（プロジェクト初期化）

**出力:** 動作可能なプロジェクト基盤

---

## 注意事項

- スタブファイルは将来の実装の「型」として機能するため、設計書のクラス名・メソッド名と完全に一致させること
- `pyproject.toml` のバージョン指定は設計書記載の値をそのまま使用すること
- mypy strict モードに準拠するため、型ヒントのない関数定義は避けること

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-001 |
| **ステータス** | `IN_PROGRESS` |
| **推定工数** | 20分 |
| **依存関係** | なし |
| **対応要件** | NFR-009, NFR-010 |
| **対応設計** | pyproject.toml 設計セクション |

---

## 情報の明確性チェック

### 明示された情報

- [x] パッケージ管理: uv
- [x] 依存パッケージとバージョン: 設計書に明記
- [x] コード品質ツール: ruff + mypy (strict)
- [x] テストフレームワーク: pytest + pytest-mock + pytest-cov
- [x] ディレクトリ構造: 設計書に明記

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| なし | - | - |

---

## 作業ログ（実装時に記入）

### YYYY-MM-DD
- **作業内容**:
- **発生した問題**:
- **解決方法**:
- **コミットハッシュ**:
