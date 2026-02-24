# TASK-011: エントリーポイント（__main__.py）

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**エントリーポイント（`__main__.py`）** を実装してください。

### 実装の目標

`uv run speakdrop` または `python -m speakdrop` でアプリケーションを起動するエントリーポイントを実装します。
起動シーケンス（権限チェック → アプリ起動）を実装します。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 変更 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/__main__.py` | エントリーポイント本実装 |

---

## 技術的コンテキスト

### 使用技術

- 言語: Python 3.11+
- メニューバーUI: rumps

### 参照すべきファイル

- `@/Users/tsk/Sync/git/SpeakDrop/speakdrop/__main__.py` - 現在のスタブ
- `@/Users/tsk/Sync/git/SpeakDrop/speakdrop/app.py` - SpeakDropApp クラス

### 関連する設計書

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/design/design.md` の「SpeakDropApp」初期化シーケンス（行211-215）

### 関連する要件

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/requirements/stories/US-006.md` - macOS権限の管理

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [x] `speakdrop/__main__.py` が実装されている
- [x] `main()` 関数が定義されている
- [x] `SpeakDropApp().run()` を呼び出してアプリを起動する
- [x] `pyproject.toml` の `[project.scripts]` で `speakdrop = "speakdrop.__main__:main"` が設定されている
- [x] `uv run ruff check speakdrop/__main__.py` でエラー0件
- [x] `uv run mypy speakdrop/__main__.py` でエラー0件

---

## 実装手順

### ステップ1: `__main__.py` を実装

`/Users/tsk/Sync/git/SpeakDrop/speakdrop/__main__.py` を実装してください：

```python
"""SpeakDrop エントリーポイント。

コマンド:
    uv run speakdrop
    python -m speakdrop
"""
from speakdrop.app import SpeakDropApp


def main() -> None:
    """SpeakDrop アプリケーションを起動する。

    起動シーケンス:
    1. SpeakDropApp を初期化（内部でConfig読み込み・権限チェックを実行）
    2. rumps のイベントループを開始
    """
    app = SpeakDropApp()
    app.run()


if __name__ == "__main__":
    main()
```

### ステップ2: pyproject.toml のエントリーポイントを確認

`/Users/tsk/Sync/git/SpeakDrop/pyproject.toml` を確認し、以下が設定されていることを確認してください：

```toml
[project.scripts]
speakdrop = "speakdrop.__main__:main"
```

設定がない場合は追加してください。

### ステップ3: 品質チェック

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run ruff check speakdrop/__main__.py
uv run mypy speakdrop/__main__.py
```

### ステップ4: コミット

```
feat: __main__.py - エントリーポイント実装（起動シーケンス）
```

---

## 実装の詳細仕様

### main() 関数

```python
def main() -> None:
    """SpeakDrop アプリケーションを起動する。"""
    app = SpeakDropApp()
    app.run()
```

シンプルな実装でよい。権限チェックは `SpeakDropApp.__init__()` 内で行われる。

### 入出力仕様

**`main() -> None`:**
- 入力: なし（コマンドライン引数は現時点では不使用）
- 出力: なし
- 副作用: rumps のイベントループを開始（アプリ終了まで戻らない）

---

## 注意事項

- `main()` は `SpeakDropApp().run()` を呼ぶだけのシンプルな実装でよい
- 権限チェックは `SpeakDropApp.__init__()` に実装されているため、ここでは不要
- `coverage.run` の `omit` に `speakdrop/__main__.py` が設定されているため、カバレッジ対象外

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-011 |
| **ステータス** | `DONE` |
| **推定工数** | 10分 |
| **依存関係** | [TASK-010](TASK-010.md) @TASK-010.md |
| **対応要件** | REQ-010, REQ-021, REQ-022 |
| **対応設計** | 初期化シーケンス（設計書行211-215） |

---

## 情報の明確性チェック

### 明示された情報

- [x] エントリーポイント: `speakdrop.__main__:main`
- [x] 起動方法: `uv run speakdrop` または `python -m speakdrop`
- [x] カバレッジ対象外: pyproject.toml の omit 設定

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| なし | - | - |

---

## 作業ログ（実装時に記入）

### 2026-02-24
- **作業内容**: speakdrop/__main__.py を実装。main() 関数で SpeakDropApp 初期化 → check_permissions() → run() の起動シーケンスを実装。app.py に check_permissions() メソッドを追加。tests/test_main.py を TDD で作成（3件すべてパス）。
- **発生した問題**: app.py に check_permissions() メソッドが未実装だったため追加した
- **解決方法**: SpeakDropApp に check_permissions() メソッドを追加（__init__ 内の権限チェックを切り出し）
- **コミットハッシュ**: 43fbc94
