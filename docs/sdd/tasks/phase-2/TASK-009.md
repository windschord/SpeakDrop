# TASK-009: Icons モジュール

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**Icons モジュール（メニューバーアイコン生成）** を実装してください。

### 実装の目標

AppState（IDLE/RECORDING/PROCESSING）に対応したメニューバーアイコンを動的生成する `icons.py` を実装します。
NSImage（pyobjc）を使ってテキストベースのアイコンを描画します。
このモジュールにはTDDを適用しますが、NSImageのモックが複雑なため、基本的な動作確認テストに留めます。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 変更 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/icons.py` | Icons モジュール本実装 |

---

## 技術的コンテキスト

### 使用技術

- 言語: Python 3.11+
- アイコン生成: pyobjc-framework-Cocoa（NSImage、NSGraphicsContext）
- 状態管理: AppState enum（app.py に定義）

### 参照すべきファイル

- `@/Users/tsk/Sync/git/SpeakDrop/speakdrop/icons.py` - 現在のスタブ
- `@/Users/tsk/Sync/git/SpeakDrop/speakdrop/app.py` - AppState enum の定義場所（TASK-010で実装）

### 関連する設計書

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/design/design.md` の「Icons」セクション（行452-471）

### 関連する要件

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/requirements/stories/US-001.md` の REQ-003, REQ-004
- NFR-007: アイコン状態変化を200ms以内に反映

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [ ] `speakdrop/icons.py` が実装されている
- [ ] `ICON_TEXTS` 辞書が3状態（IDLE/RECORDING/PROCESSING）のアイコン文字列を持つ
- [ ] `create_text_icon(text: str, size: int = 22) -> NSImage` 関数が実装されている
- [ ] `get_icon_title(state: "AppState") -> str` 関数が実装されている
- [ ] `uv run ruff check speakdrop/icons.py` でエラー0件
- [ ] `uv run mypy speakdrop/icons.py` でエラー0件

---

## 実装手順

### ステップ1: Icons モジュールを実装

`/Users/tsk/Sync/git/SpeakDrop/speakdrop/icons.py` を実装してください。

**設計方針の選択**:

rumps ではメニューバーのアイコンに画像（NSImage）またはタイトル文字列を使用できます。
NSImage の動的生成は pyobjc の深い知識が必要なため、**まずタイトル文字列方式**で実装し、後でアイコン画像方式に移行可能な構造にしてください。

```python
"""メニューバーアイコン生成モジュール。

AppState に対応するメニューバーアイコン（または文字列タイトル）を提供する。
NFR-007: 状態変化を 200ms 以内に反映するため、事前生成またはシンプルな文字列を使用。
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from speakdrop.app import AppState


# 状態別のアイコン文字列（タイトル方式）
ICON_TEXTS: dict[str, str] = {
    "IDLE": "🎤",        # 待機中
    "RECORDING": "🔴",  # 録音中
    "PROCESSING": "⏳",  # 処理中
}


def get_icon_title(state: "AppState") -> str:
    """AppState に対応するメニューバーアイコン文字列を返す。

    Args:
        state: 現在のアプリケーション状態

    Returns:
        メニューバーに表示する文字列（絵文字）
    """
    return ICON_TEXTS.get(state.name, "🎤")
```

**注意**: rumps の `App` クラスには `title` プロパティがあり、メニューバーに文字列を表示できます。
画像アイコンが必要な場合は `App.icon` プロパティに `NSImage` を設定しますが、
このタスクではシンプルな文字列（絵文字）方式を採用してください。

### ステップ2: 品質チェック

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run ruff check speakdrop/icons.py
uv run mypy speakdrop/icons.py
```

### ステップ3: コミット

```
feat: icons.py - メニューバーアイコン生成モジュール実装（状態別絵文字）
```

---

## 実装の詳細仕様

### ICON_TEXTS 辞書

```python
ICON_TEXTS = {
    "IDLE": "🎤",        # 待機中（マイクアイコン）
    "RECORDING": "🔴",  # 録音中（赤丸）
    "PROCESSING": "⏳",  # 処理中（砂時計）
}
```

### 入出力仕様

**`get_icon_title(state: AppState) -> str`:**
- 入力: AppState enum値
- 出力: メニューバーに表示する文字列（str）
- `state.name` を使って辞書を参照

### AppState との連携

`icons.py` は `app.py` の `AppState` に依存します。
循環インポートを避けるため `TYPE_CHECKING` ガードを使用してください：

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from speakdrop.app import AppState
```

実行時は `state.name`（文字列）で辞書を参照するため、実際のimportは不要です。

---

## 注意事項

- 絵文字はmacOS 13以降で標準サポートされているため、そのまま使用可能
- NFR-007（200ms以内）を満たすため、アイコン生成はシンプルに保つこと
- `TYPE_CHECKING` ガードで循環インポートを防ぐこと
- 将来NSImage方式に移行しやすいよう、関数インターフェースを維持すること

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-009 |
| **ステータス** | `DONE` |
| **推定工数** | 15分 |
| **依存関係** | [TASK-001](../phase-1/TASK-001.md) @../phase-1/TASK-001.md |
| **対応要件** | REQ-003, REQ-004, NFR-007 |
| **対応設計** | Icons セクション（設計書行452-471） |

---

## 情報の明確性チェック

### 明示された情報

- [x] 3状態のアイコン: IDLE/RECORDING/PROCESSING
- [x] 実装方針: 絵文字文字列（シンプル方式）
- [x] NFR-007: 200ms以内の状態変化反映

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| NSImage方式の必要性 | 文字列（絵文字）方式で要件を満たせると判断 | [x] 要件はアイコン変化のみ。文字列で十分 |

---

## 作業ログ（実装時に記入）

### 2026-02-24
- **作業内容**: TDDでicons.pyを実装。テスト9件作成→失敗確認→実装→全パス
- **発生した問題**: app.pyのスタブにAppStateがないためmypy TYPE_CHECKINGでエラー
- **解決方法**: TYPE_CHECKINGの代わりにProtocol(_HasName)を使用して疎結合化
- **コミットハッシュ**: dd751d9
