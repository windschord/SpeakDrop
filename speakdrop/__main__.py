"""SpeakDrop エントリーポイント。

コマンド:
    uv run speakdrop
    python -m speakdrop
"""

from speakdrop.app import SpeakDropApp


def main() -> None:
    """SpeakDrop アプリケーションを起動する。

    起動シーケンス:
    1. SpeakDropApp を初期化（権限チェックを含む）
    2. rumps のイベントループを開始
    """
    app = SpeakDropApp()
    app.run()


if __name__ == "__main__":
    main()
