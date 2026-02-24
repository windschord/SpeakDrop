"""tests/test_main.py - __main__.py のテスト。"""

from unittest.mock import MagicMock, patch

from speakdrop.__main__ import main


class TestMain:
    """main() 関数のテスト。"""

    def test_main_initializes_speakdrop_app(self) -> None:
        """main() が SpeakDropApp を初期化することを確認する。"""
        with patch("speakdrop.__main__.SpeakDropApp") as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app

            main()

            mock_app_class.assert_called_once()

    def test_main_calls_check_permissions(self) -> None:
        """main() が check_permissions() を呼ぶことを確認する。"""
        with patch("speakdrop.__main__.SpeakDropApp") as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app

            main()

            mock_app.check_permissions.assert_called_once()

    def test_main_calls_run(self) -> None:
        """main() が run() を呼ぶことを確認する。"""
        with patch("speakdrop.__main__.SpeakDropApp") as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app

            main()

            mock_app.run.assert_called_once()
