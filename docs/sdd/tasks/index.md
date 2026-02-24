# タスク計画: SpeakDrop

> このドキュメントはAIエージェント（Claude Code等）が実装を行うことを前提としています。
> **不明な情報が1つでもある場合は、実装前に必ず確認を取ってください。**

---

## 情報の明確性チェック（全体）

### ユーザーから明示された情報

- [x] 実装対象のディレクトリ構造: `/Users/tsk/Sync/git/SpeakDrop/`
- [x] 使用するパッケージマネージャー: uv
- [x] テストフレームワーク: pytest + pytest-mock + pytest-cov
- [x] リンター/フォーマッター: ruff + mypy (strict)
- [x] 開発方式: TDD（テスト駆動開発）
- [x] Python バージョン: 3.11以上
- [x] 実装言語: Python
- [x] ターゲット環境: macOS 13以降（Apple Silicon）

### 不明/要確認の情報（全体）

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| pyobjcのmypy対応 | `ignore_missing_imports` 設定が必要な可能性あり | [ ] TASK-001実装後に確認 |
| pynput "alt_r" キー名 | macOS実機で確認が必要 | [ ] TASK-007実装後に実機テスト |
| ollama ライブラリのタイムアウト指定方法 | バージョンにより異なる可能性あり | [ ] TASK-005実装時に確認 |

---

## 進捗サマリ

| フェーズ | 完了 | 進行中 | 未着手 | ブロック | 詳細リンク |
|---------|------|--------|--------|----------|-----------|
| Phase 1: 基盤構築 | 1 | 0 | 0 | 0 | [詳細](phase-1/) @phase-1/ |
| Phase 2: コアモジュール（TDD） | 1 | 0 | 7 | 0 | [詳細](phase-2/) @phase-2/ |
| Phase 3: 統合・エントリーポイント | 0 | 0 | 2 | 0 | [詳細](phase-3/) @phase-3/ |
| Phase 4: 品質保証 | 0 | 0 | 1 | 0 | [詳細](phase-4/) @phase-4/ |

---

## タスク一覧

### Phase 1: 基盤構築
*推定期間: 20分（AIエージェント作業時間）*

| タスクID | タイトル | ステータス | 依存 | 見積 | 詳細リンク |
|----------|---------|-----------|------|------|-----------|
| TASK-001 | プロジェクトセットアップ | `DONE` | - | 20min | [詳細](phase-1/TASK-001.md) @phase-1/TASK-001.md |

### Phase 2: コアモジュール（TDD）
*推定期間: 160分（AIエージェント作業時間）。TASK-002〜009は並列実行可能*

| タスクID | タイトル | ステータス | 依存 | 見積 | 詳細リンク |
|----------|---------|-----------|------|------|-----------|
| TASK-002 | Config モジュール（TDD） | `TODO` | TASK-001 | 25min | [詳細](phase-2/TASK-002.md) @phase-2/TASK-002.md |
| TASK-003 | AudioRecorder モジュール（TDD） | `TODO` | TASK-001 | 30min | [詳細](phase-2/TASK-003.md) @phase-2/TASK-003.md |
| TASK-004 | Transcriber モジュール（TDD） | `TODO` | TASK-001 | 30min | [詳細](phase-2/TASK-004.md) @phase-2/TASK-004.md |
| TASK-005 | TextProcessor モジュール（TDD） | `DONE` | TASK-001 | 25min | [詳細](phase-2/TASK-005.md) @phase-2/TASK-005.md |
| TASK-006 | ClipboardInserter モジュール（TDD） | `IN_PROGRESS` | TASK-001 | 35min | [詳細](phase-2/TASK-006.md) @phase-2/TASK-006.md |
| TASK-007 | HotkeyListener モジュール（TDD） | `IN_PROGRESS` | TASK-001 | 30min | [詳細](phase-2/TASK-007.md) @phase-2/TASK-007.md |
| TASK-008 | PermissionChecker モジュール（TDD） | `TODO` | TASK-001 | 25min | [詳細](phase-2/TASK-008.md) @phase-2/TASK-008.md |
| TASK-009 | Icons モジュール | `TODO` | TASK-001 | 15min | [詳細](phase-2/TASK-009.md) @phase-2/TASK-009.md |

### Phase 3: 統合・エントリーポイント
*推定期間: 70分（AIエージェント作業時間）。TASK-010の後にTASK-011*

| タスクID | タイトル | ステータス | 依存 | 見積 | 詳細リンク |
|----------|---------|-----------|------|------|-----------|
| TASK-010 | SpeakDropApp（app.py） | `TODO` | TASK-002〜009 | 60min | [詳細](phase-3/TASK-010.md) @phase-3/TASK-010.md |
| TASK-011 | エントリーポイント（__main__.py） | `TODO` | TASK-010 | 10min | [詳細](phase-3/TASK-011.md) @phase-3/TASK-011.md |

### Phase 4: 品質保証
*推定期間: 40分（AIエージェント作業時間）*

| タスクID | タイトル | ステータス | 依存 | 見積 | 詳細リンク |
|----------|---------|-----------|------|------|-----------|
| TASK-012 | 結合テスト・品質チェック | `TODO` | TASK-002〜011 | 40min | [詳細](phase-4/TASK-012.md) @phase-4/TASK-012.md |

---

## 並列実行グループ

エージェントチームで並列実行する際の参考情報です。

### グループ A: 基盤構築（単独・先行実行）

| タスク | 対象ファイル | 依存 |
|--------|-------------|------|
| TASK-001 | `pyproject.toml`, `speakdrop/*.py`（スタブ）, `tests/__init__.py` | なし |

### グループ B: コアモジュール（グループA完了後・全8タスクが並列実行可能）

| タスク | 対象ファイル | 依存 |
|--------|-------------|------|
| TASK-002 | `speakdrop/config.py`, `tests/test_config.py` | TASK-001 |
| TASK-003 | `speakdrop/audio_recorder.py`, `tests/test_audio_recorder.py` | TASK-001 |
| TASK-004 | `speakdrop/transcriber.py`, `tests/test_transcriber.py` | TASK-001 |
| TASK-005 | `speakdrop/text_processor.py`, `tests/test_text_processor.py` | TASK-001 |
| TASK-006 | `speakdrop/clipboard_inserter.py`, `tests/test_clipboard_inserter.py` | TASK-001 |
| TASK-007 | `speakdrop/hotkey_listener.py`, `tests/test_hotkey_listener.py` | TASK-001 |
| TASK-008 | `speakdrop/permissions.py`, `tests/test_permissions.py` | TASK-001 |
| TASK-009 | `speakdrop/icons.py` | TASK-001 |

### グループ C: 統合（グループB完了後・順次実行）

| タスク | 対象ファイル | 依存 |
|--------|-------------|------|
| TASK-010 | `speakdrop/app.py` | TASK-002〜009 |
| TASK-011 | `speakdrop/__main__.py` | TASK-010 |

### グループ D: 品質保証（グループC完了後）

| タスク | 対象ファイル | 依存 |
|--------|-------------|------|
| TASK-012 | `speakdrop/*.py`, `tests/*.py`（修正のみ） | TASK-002〜011 |

---

## タスクステータスの凡例

- `TODO` - 未着手
- `IN_PROGRESS` - 作業中
- `BLOCKED` - 依存関係や問題によりブロック中
- `REVIEW` - レビュー待ち
- `DONE` - 完了

---

## 逆順レビュー結果（タスク → 設計 → 要件）

### タスク → 設計 整合性チェック

| 設計要素 | 対応タスク | 状態 |
|---------|-----------|------|
| `Config` dataclass | TASK-002 | 対応済 |
| `AudioRecorder` クラス | TASK-003 | 対応済 |
| `Transcriber` クラス | TASK-004 | 対応済 |
| `TextProcessor` クラス | TASK-005 | 対応済 |
| `ClipboardInserter` クラス | TASK-006 | 対応済 |
| `HotkeyListener` クラス | TASK-007 | 対応済 |
| `PermissionChecker` クラス | TASK-008 | 対応済 |
| `Icons` / `get_icon_title()` | TASK-009 | 対応済 |
| `AppState` enum + `SpeakDropApp` | TASK-010 | 対応済 |
| `__main__.py` エントリーポイント | TASK-011 | 対応済 |
| `pyproject.toml` + ディレクトリ構造 | TASK-001 | 対応済 |
| ruff + mypy + pytest-cov | TASK-001, TASK-012 | 対応済 |

### 設計 → 要件 カバレッジチェック

| 要件ID | 対応タスク | 状態 |
|--------|-----------|------|
| REQ-001 | TASK-007, TASK-010 | 対応済 |
| REQ-002 | TASK-003, TASK-004, TASK-007, TASK-010 | 対応済 |
| REQ-003 | TASK-009, TASK-010 | 対応済 |
| REQ-004 | TASK-009, TASK-010 | 対応済 |
| REQ-005 | TASK-006 | 対応済 |
| REQ-006 | TASK-006 | 対応済 |
| REQ-007 | TASK-005 | 対応済 |
| REQ-008 | TASK-005 | 対応済 |
| REQ-009 | TASK-005 | 対応済 |
| REQ-010 | TASK-010, TASK-011 | 対応済 |
| REQ-011 | TASK-010 | 対応済（rumps標準動作） |
| REQ-012 | TASK-010 | 対応済 |
| REQ-013 | TASK-010 | 対応済 |
| REQ-014 | TASK-010 | 対応済 |
| REQ-015 | TASK-007 | 対応済 |
| REQ-016 | TASK-002 | 対応済 |
| REQ-017 | TASK-002 | 対応済 |
| REQ-018 | TASK-004, TASK-010 | 対応済 |
| REQ-019 | TASK-004 | 対応済 |
| REQ-020 | TASK-010 | 対応済（TASK-004との統合時） |
| REQ-021 | TASK-008 | 対応済 |
| REQ-022 | TASK-008 | 対応済 |
| NFR-001 | TASK-004 | 対応済（int8量子化・MPS） |
| NFR-002 | TASK-005 | 対応済（5秒タイムアウト） |
| NFR-003 | TASK-004 | 対応済（遅延ロード） |
| NFR-004 | TASK-003 | 対応済（16kHz/Mono/int16） |
| NFR-005 | TASK-005 | 対応済（localhost固定） |
| NFR-006 | TASK-003 | 対応済（バッファクリア） |
| NFR-007 | TASK-009, TASK-010 | 対応済（同期アイコン更新） |
| NFR-008 | TASK-001 | 対応済（Python 3.11+・pyobjc） |
| NFR-009 | TASK-001, TASK-012 | 対応済 |
| NFR-010 | TASK-012 | 対応済（80%以上目標） |

### 不整合・過不足の確認

不整合・実装漏れ: **なし**

スコープ外機能の混入: **なし**（リアルタイムストリーミング・話者分離等は実装対象外）

---

## リスクと軽減策

| リスク | 影響度 | 発生確率 | 軽減策 |
|--------|--------|----------|--------|
| pyobjc の API が実行環境で動作しない | 高 | 中 | TASK-006, TASK-008実装後に実機テストを実施 |
| pynput の "alt_r" キー名がmacOSで正しくない | 中 | 中 | TASK-007実装後に実機確認。必要なら pynput.keyboard.Key.alt_r を使用 |
| faster-whisper の Apple Silicon MPS 対応 | 中 | 低 | "auto" で CPU フォールバックが機能する設計 |
| ollama ライブラリのタイムアウト仕様 | 中 | 中 | TASK-005実装時にライブラリドキュメントを確認 |
| rumps.Window の設定ダイアログ実装 | 中 | 低 | TASK-010で実装。rumps APIを確認して調整 |
| mypy が pyobjc モジュールを認識できない | 低 | 高 | pyproject.toml に `ignore_missing_imports = true` を設定 |

---

## ドキュメント構成

```
docs/sdd/tasks/
├── index.md                       # このファイル（目次）
├── phase-1/
│   └── TASK-001.md                # プロジェクトセットアップ
├── phase-2/
│   ├── TASK-002.md                # Config モジュール（TDD）
│   ├── TASK-003.md                # AudioRecorder モジュール（TDD）
│   ├── TASK-004.md                # Transcriber モジュール（TDD）
│   ├── TASK-005.md                # TextProcessor モジュール（TDD）
│   ├── TASK-006.md                # ClipboardInserter モジュール（TDD）
│   ├── TASK-007.md                # HotkeyListener モジュール（TDD）
│   ├── TASK-008.md                # PermissionChecker モジュール（TDD）
│   └── TASK-009.md                # Icons モジュール
├── phase-3/
│   ├── TASK-010.md                # SpeakDropApp（app.py）
│   └── TASK-011.md                # エントリーポイント（__main__.py）
└── phase-4/
    └── TASK-012.md                # 結合テスト・品質チェック
```

---

## 備考

### TDDの進め方

各TDDタスク（TASK-002〜008）は以下のサイクルで実行してください：

1. テストファイルを作成（タスクに記載のテストコードをそのまま使用可）
2. `uv run pytest [テストファイル] -v` を実行して全テストの失敗を確認
3. テストをコミット（`test: ...`）
4. 実装ファイルを実装
5. `uv run pytest [テストファイル] -v` を実行して全テストのパスを確認
6. `uv run ruff check` + `uv run mypy` で品質確認
7. 実装をコミット（`feat: ...`）

### 推定総工数

| フェーズ | 推定工数 |
|---------|--------|
| Phase 1 | 20分 |
| Phase 2（順次） | 160分 |
| Phase 2（並列・8エージェント） | 35分 |
| Phase 3 | 70分 |
| Phase 4 | 40分 |
| **合計（順次）** | **290分** |
| **合計（並列活用）** | **165分** |
