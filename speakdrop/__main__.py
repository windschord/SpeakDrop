"""SpeakDrop エントリーポイント。

コマンド:
    uv run speakdrop
    python -m speakdrop
"""

from speakdrop.app import SpeakDropApp


def main() -> None:
    """SpeakDrop アプリケーションを起動する。

    起動シーケンス:
    1. SpeakDropApp を初期化
    2. 権限チェック（失敗してもアプリ自体は起動する）
    3. rumps のイベントループを開始
    """
    app = SpeakDropApp()
    # 権限チェック（失敗してもアプリ自体は起動する）
    app.check_permissions()
    app.run()


if __name__ == "__main__":
    main()
