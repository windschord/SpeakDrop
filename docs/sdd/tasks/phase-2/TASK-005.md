# TASK-005: TextProcessor モジュール（TDD）

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**TextProcessor モジュール** をTDD方式で実装してください。

### 実装の目標

Ollama LLMを使って句読点挿入・話し言葉整形を行うモジュールを実装します。
Ollama未起動時は元テキストをそのまま返すフォールバック機能を実装します。
TDD原則に従い、`ollama` クライアントはpytest-mockでモックします。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/tests/test_text_processor.py` | テストファイル（先行作成） |
| 変更 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/text_processor.py` | TextProcessor モジュール本実装 |

---

## 技術的コンテキスト

### 使用技術

- 言語: Python 3.11+
- テストフレームワーク: pytest + pytest-mock
- Ollamaクライアント: ollama Python ライブラリ

### 参照すべきファイル

- `@/Users/tsk/Sync/git/SpeakDrop/speakdrop/text_processor.py` - 現在のスタブ

### 関連する設計書

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/design/design.md` の「TextProcessor」セクション（行287-317）

### 関連する要件

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/requirements/stories/US-002.md` - テキスト後処理

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [ ] `tests/test_text_processor.py` が作成されている（テストが5件以上）
- [ ] `speakdrop/text_processor.py` が実装されている
- [ ] `TextProcessor.OLLAMA_HOST == "http://localhost:11434"`（NFR-005）
- [ ] `TextProcessor.MODEL == "qwen2.5:7b"`
- [ ] 正常ケース: Ollamaが返したテキストを返す（REQ-007, REQ-008）
- [ ] フォールバック: Ollama未起動時は元テキストを返す（REQ-009）
- [ ] タイムアウト: 5秒（NFR-002対応）
- [ ] SYSTEM_PROMPT が設計書の内容通りに定義されている
- [ ] `uv run pytest tests/test_text_processor.py -v` で全テストパス
- [ ] `uv run ruff check speakdrop/text_processor.py tests/test_text_processor.py` でエラー0件
- [ ] `uv run mypy speakdrop/text_processor.py` でエラー0件

---

## 実装手順

### ステップ1: テストを先に作成（TDD）

`/Users/tsk/Sync/git/SpeakDrop/tests/test_text_processor.py` を作成してください：

```python
"""TextProcessor モジュールのテスト。"""
from unittest.mock import MagicMock, patch

import pytest

from speakdrop.text_processor import TextProcessor


class TestTextProcessorConstants:
    """TextProcessor の定数テスト。"""

    def test_ollama_host(self) -> None:
        """OLLAMA_HOST が localhost を指すこと（NFR-005）。"""
        assert TextProcessor.OLLAMA_HOST == "http://localhost:11434"

    def test_model(self) -> None:
        """MODEL が 'qwen2.5:7b' であること。"""
        assert TextProcessor.MODEL == "qwen2.5:7b"


class TestTextProcessorProcess:
    """TextProcessor.process() のテスト。"""

    @patch("speakdrop.text_processor.ollama")
    def test_process_returns_processed_text(self, mock_ollama: MagicMock) -> None:
        """Ollama が正常に応答した場合、処理済みテキストを返すこと（REQ-007,008）。"""
        mock_response = MagicMock()
        mock_response.message.content = "こんにちは、世界。"
        mock_ollama.chat.return_value = mock_response

        processor = TextProcessor()
        result = processor.process("こんにちは世界")

        assert result == "こんにちは、世界。"

    @patch("speakdrop.text_processor.ollama")
    def test_process_calls_ollama_with_correct_model(
        self, mock_ollama: MagicMock
    ) -> None:
        """Ollama に正しいモデルを指定して呼び出すこと。"""
        mock_response = MagicMock()
        mock_response.message.content = "テスト。"
        mock_ollama.chat.return_value = mock_response

        processor = TextProcessor()
        processor.process("テスト")

        call_kwargs = mock_ollama.chat.call_args.kwargs
        assert call_kwargs["model"] == "qwen2.5:7b"

    @patch("speakdrop.text_processor.ollama")
    def test_process_fallback_on_connection_error(
        self, mock_ollama: MagicMock
    ) -> None:
        """Ollama 未起動時（接続エラー）は元テキストを返すこと（REQ-009）。"""
        mock_ollama.chat.side_effect = Exception("Connection refused")

        processor = TextProcessor()
        result = processor.process("こんにちは")

        assert result == "こんにちは"

    @patch("speakdrop.text_processor.ollama")
    def test_process_fallback_on_response_error(self, mock_ollama: MagicMock) -> None:
        """Ollama がエラーを返した場合も元テキストを返すこと（REQ-009）。"""
        mock_ollama.ResponseError = Exception
        mock_ollama.chat.side_effect = mock_ollama.ResponseError("Model not found")

        processor = TextProcessor()
        result = processor.process("テスト入力")

        assert result == "テスト入力"

    @patch("speakdrop.text_processor.ollama")
    def test_process_includes_system_prompt(self, mock_ollama: MagicMock) -> None:
        """Ollama 呼び出し時にシステムプロンプトが含まれること。"""
        mock_response = MagicMock()
        mock_response.message.content = "テスト。"
        mock_ollama.chat.return_value = mock_response

        processor = TextProcessor()
        processor.process("テスト")

        call_kwargs = mock_ollama.chat.call_args.kwargs
        messages = call_kwargs["messages"]
        system_messages = [m for m in messages if m.get("role") == "system"]
        assert len(system_messages) == 1
        assert "句読点" in system_messages[0]["content"]
```

テストを実行して失敗を確認：

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run pytest tests/test_text_processor.py -v
```

コミット：

```
test: test_text_processor.py - TextProcessor モジュールのTDDテスト追加
```

### ステップ2: TextProcessor モジュールを実装

`/Users/tsk/Sync/git/SpeakDrop/speakdrop/text_processor.py` を実装してください：

```python
"""テキスト後処理モジュール。

Ollama LLM を使って句読点挿入・話し言葉整形を行う。
Ollama が未起動の場合は元テキストをそのまま返す（REQ-009）。
"""
import ollama


SYSTEM_PROMPT = """あなたは日本語テキストの校正を行うアシスタントです。
以下のルールに従ってテキストを整形してください：
1. 適切な位置に句読点（。、！？）を挿入する
2. 話し言葉を書き言葉に変換する（例: 〜だけど → 〜ですが）
3. テキストの意味や内容は変更しない
4. 整形後のテキストのみを出力する（説明文は不要）"""


class TextProcessor:
    """Ollama LLM によるテキスト後処理クラス（NFR-005: ローカル処理）。"""

    OLLAMA_HOST: str = "http://localhost:11434"  # NFR-005: ローカル固定
    MODEL: str = "qwen2.5:7b"

    def process(self, text: str) -> str:
        """テキストを後処理して返す。

        Ollama が起動していない場合は元のテキストをそのまま返す（REQ-009）。

        Args:
            text: 処理対象テキスト

        Returns:
            処理済みテキスト。Ollama 未起動時は入力テキストそのまま。
        """
        try:
            response = ollama.chat(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                options={"num_predict": 512},
            )
            return str(response.message.content)
        except Exception:
            # REQ-009: Ollama 未起動・エラー時はフォールバック
            return text
```

**注意**: タイムアウトの実装方法について。`ollama` Python ライブラリのバージョンによってタイムアウト指定方法が異なります。ライブラリのドキュメントを確認し、`timeout=5` または `Client(host=..., timeout=5)` の形式で5秒タイムアウトを設定してください。

### ステップ3: テストがパスすることを確認

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run pytest tests/test_text_processor.py -v
uv run ruff check speakdrop/text_processor.py tests/test_text_processor.py
uv run mypy speakdrop/text_processor.py
```

### ステップ4: コミット

```
feat: text_processor.py - TextProcessor 実装（Ollama後処理・フォールバック、REQ-007/008/009）
```

---

## 実装の詳細仕様

### SYSTEM_PROMPT

```python
SYSTEM_PROMPT = """あなたは日本語テキストの校正を行うアシスタントです。
以下のルールに従ってテキストを整形してください：
1. 適切な位置に句読点（。、！？）を挿入する
2. 話し言葉を書き言葉に変換する（例: 〜だけど → 〜ですが）
3. テキストの意味や内容は変更しない
4. 整形後のテキストのみを出力する（説明文は不要）"""
```

### 入出力仕様

**`TextProcessor.process(text: str) -> str`:**
- 入力: 認識テキスト（str）
- 出力: 処理済みテキスト（str）
- Ollama正常時: LLMが処理したテキスト
- Ollama異常時: 入力テキストをそのまま返す（REQ-009）

### エラー処理

- 接続エラー（ConnectionError）: 元テキストを返す（REQ-009）
- ollama.ResponseError: 元テキストを返す（REQ-009）
- タイムアウト: 元テキストを返す（REQ-009）
- 全ての例外をキャッチしてフォールバック（設計書の方針）

---

## 注意事項

- `import ollama` をモジュールレベルでインポートすること（テストでモック可能にするため）
- テストでは `@patch("speakdrop.text_processor.ollama")` でモックすること
- OLLAMA_HOST は固定値であり、設定変更不可（NFR-005: ローカル処理の徹底）
- 例外処理は広く（`except Exception`）キャッチして確実にフォールバックすること
- タイムアウト設定は ollama ライブラリのバージョンを確認して適切に実装すること

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-005 |
| **ステータス** | `DONE` |
| **推定工数** | 25分 |
| **依存関係** | [TASK-001](../phase-1/TASK-001.md) @../phase-1/TASK-001.md |
| **対応要件** | REQ-007, REQ-008, REQ-009, NFR-002, NFR-005 |
| **対応設計** | TextProcessor セクション（設計書行287-317） |

---

## 情報の明確性チェック

### 明示された情報

- [x] Ollama エンドポイント: http://localhost:11434 (固定, NFR-005)
- [x] モデル: qwen2.5:7b
- [x] タイムアウト: 5秒（設計書行316）
- [x] フォールバック動作: 元テキストをそのまま返す（REQ-009）
- [x] SYSTEM_PROMPT の内容: 設計書行306-311に明記

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| ollama ライブラリのタイムアウト指定方法 | バージョンにより異なる可能性あり | [ ] 実装時にライブラリドキュメント確認が必要 |

---

## 作業ログ（実装時に記入）

### 2026-02-24
- **作業内容**: TDD方式でTextProcessorモジュールを実装。テスト7件を先行作成し、全パスを確認。
- **発生した問題**: テストファイルに不要な `import pytest` があり、ruffエラーが発生した。
- **解決方法**: 不要なインポートを削除。
- **コミットハッシュ**: fd11ec1
