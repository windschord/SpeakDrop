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
