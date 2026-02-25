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
    DEFAULT_MODEL: str = "qwen2.5:7b"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        """TextProcessor を初期化する。

        Args:
            model: 使用する Ollama モデル名（デフォルト: DEFAULT_MODEL）
        """
        self._model = model
        self._client = ollama.Client(host=self.OLLAMA_HOST, timeout=5.0)

    def process(self, text: str) -> str:
        """テキストを後処理して返す。

        Ollama が起動していない場合は元のテキストをそのまま返す（REQ-009）。

        Args:
            text: 処理対象テキスト

        Returns:
            処理済みテキスト。Ollama 未起動時は入力テキストそのまま。
        """
        try:
            response = self._client.chat(
                model=self._model,
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
