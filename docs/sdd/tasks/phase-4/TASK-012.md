# TASK-012: 結合テスト・品質チェック

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**結合テストの実行と品質基準の充足** を確認してください。

### 実装の目標

全モジュールが実装された状態で、ruff lint/format、mypy型チェック、pytest --cov を実行します。
テストカバレッジ80%未満の場合はテストを追加して80%以上にします（NFR-010）。
全品質基準をパスさせます（NFR-009）。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 確認/修正 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/*.py` | 品質基準違反の修正 |
| 確認/追加 | `/Users/tsk/Sync/git/SpeakDrop/tests/*.py` | カバレッジ不足時のテスト追加 |

---

## 技術的コンテキスト

### 使用技術

- コード品質: ruff + mypy (strict)
- テスト: pytest + pytest-cov
- カバレッジ目標: 80%以上（NFR-010）

### 参照すべきファイル

すべてのモジュールとテストファイル:
- `@/Users/tsk/Sync/git/SpeakDrop/speakdrop/` - 全実装ファイル
- `@/Users/tsk/Sync/git/SpeakDrop/tests/` - 全テストファイル
- `@/Users/tsk/Sync/git/SpeakDrop/pyproject.toml` - 品質ツール設定

### 関連する設計書

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/design/design.md` の「テスト戦略」セクション（行580-608）
- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/design/design.md` の「CI/CD設計」セクション（行611-634）

### 関連する要件

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/requirements/nfr/maintainability.md` - NFR-009, NFR-010

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [x] `uv run ruff check .` でエラー0件（NFR-009）
- [x] `uv run ruff format --check .` で差分なし（NFR-009）
- [x] `uv run mypy .` でエラー0件（NFR-009）
- [x] `uv run pytest --cov=speakdrop --cov-report=term-missing` でカバレッジ92.39%（目標80%以上、NFR-010）
- [x] `uv run pytest --cov=speakdrop --cov-fail-under=80` が成功
- [x] 全98テストがパスする

---

## 実装手順

### ステップ1: ruff チェック・修正

```bash
cd /Users/tsk/Sync/git/SpeakDrop

# Lint チェック
uv run ruff check .

# 自動修正可能な問題を修正
uv run ruff check --fix .

# フォーマットチェック
uv run ruff format --check .

# フォーマット適用
uv run ruff format .
```

エラーが残る場合は手動で修正してください。

### ステップ2: mypy 型チェック

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run mypy .
```

型エラーがある場合は修正してください。よくある修正パターン：
- 型アノテーションが不足している場合: 型ヒントを追加
- `Any` 型の使用: 適切な型に変更するか `# type: ignore[assignment]` で抑制
- `Optional` の使用: `X | None` 形式に変更（Python 3.11+）

### ステップ3: pytest とカバレッジ確認

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run pytest --cov=speakdrop --cov-report=term-missing -v
```

カバレッジが80%未満の場合は、カバレッジレポートで未カバーの行を確認し、テストを追加してください。

**カバレッジが不足しやすい箇所**:
- `AudioRecorder._audio_callback()` のエラーパス
- `Transcriber.transcribe()` の空セグメント処理
- `TextProcessor.process()` のタイムアウト処理
- `HotkeyListener._get_key_name()` のフォールバック
- `SpeakDropApp.process_audio()` のエラー処理（ただし `app.py` はカバレッジ対象に含まれる）

### ステップ4: カバレッジ80%以上を確認

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run pytest --cov=speakdrop --cov-fail-under=80
```

### ステップ5: 最終品質確認コミット

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest --cov=speakdrop --cov-fail-under=80
```

全チェック通過後にコミット：

```
test: 結合テスト・品質チェック完了（ruff/mypy/pytest-cov 80%以上、NFR-009/010）
```

---

## 実装の詳細仕様

### 品質ゲート（設計書 CI/CD設計より）

| 項目 | 基準値 | 採用ツール |
|------|--------|-----------|
| テストカバレッジ | 80%以上 | pytest-cov |
| Linter | エラー0件 | ruff check |
| フォーマット | 差分なし | ruff format --check |
| 型チェック | エラー0件 | mypy (strict mode) |

### カバレッジ対象

- `speakdrop/` 以下の全ファイル
- ただし `speakdrop/__main__.py` は除外（pyproject.toml の omit 設定）

### よくあるカバレッジ向上のためのテスト追加パターン

**AudioRecorder のロック処理テスト**:
```python
def test_audio_callback_thread_safe():
    """_audio_callback が並列呼び出しでもデータを失わないこと。"""
```

**TextProcessor のタイムアウトテスト**:
```python
def test_process_fallback_on_timeout():
    """タイムアウト時に元テキストを返すこと。"""
```

---

## 注意事項

- ruff check の自動修正（`--fix`）を使っても残るエラーは手動で対処すること
- mypy strict モードでは `Any` の使用が制限される。`# type: ignore` は最小限にすること
- pyobjcのモジュールはmypy が認識できない場合がある。`ignore_missing_imports = true` を設定するか、型スタブを確認すること
- カバレッジは `speakdrop/__main__.py` を除いた80%以上を目標とする

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-012 |
| **ステータス** | `DONE` |
| **推定工数** | 40分 |
| **依存関係** | TASK-002〜011 すべて完了後 |
| **対応要件** | NFR-009, NFR-010 |
| **対応設計** | CI/CD設計セクション（設計書行611-634） |

---

## 情報の明確性チェック

### 明示された情報

- [x] カバレッジ目標: 80%以上（NFR-010）
- [x] 品質ツール: ruff + mypy（NFR-009）
- [x] カバレッジ除外: speakdrop/__main__.py

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| pyobjcのmypy対応 | ignore_missing_imports が必要な可能性あり | [ ] TASK-001実装後にmypy設定を確認 |

---

## 作業ログ（実装時に記入）

### 2026-02-24
- **作業内容**: ruff lint/format、mypy型チェック、pytest-covを実行し品質基準を充足
- **発生した問題**:
  1. test_app.py に未使用インポート（threading, call, numpy）と F821（未定義名 SpeakDropApp）
  2. test_icons.py に不要な type: ignore コメント
  3. test_app.py のモジュールレベル sys.modules モックが numpy を汚染し、test_audio_recorder.py の 3 テストが失敗
- **解決方法**:
  1. 未使用インポート削除、型アノテーションを Any に変更
  2. type: ignore コメント削除（mypy が FakeState を _HasName 互換と正しく認識するため）
  3. tests/conftest.py を新規作成し、テスト収集前に numpy を先行ロードして setdefault による上書きを防止
- **コミットハッシュ**: 48c14a4
