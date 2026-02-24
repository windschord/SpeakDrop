"""ClipboardInserter モジュールのテスト。"""

import sys
from unittest.mock import MagicMock, patch


# pyobjc は macOS 専用のため、テスト用にモジュールをモック化
# 実際のビルドなしにインポートできるようにする
def _setup_pyobjc_mocks() -> None:
    """pyobjc モジュールをシステムモジュールにモック登録する。"""
    mock_cocoa = MagicMock()
    mock_quartz = MagicMock()
    mock_appkit = MagicMock()

    sys.modules.setdefault("AppKit", mock_appkit)
    sys.modules.setdefault("Cocoa", mock_cocoa)
    sys.modules.setdefault("Quartz", mock_quartz)
    sys.modules.setdefault("Quartz.CoreGraphics", mock_quartz)


_setup_pyobjc_mocks()

from speakdrop.clipboard_inserter import ClipboardInserter  # noqa: E402


class TestClipboardInserterConstants:
    """ClipboardInserter の定数テスト。"""

    def test_paste_delay(self) -> None:
        """PASTE_DELAY が 0.05 であること。"""
        assert ClipboardInserter.PASTE_DELAY == 0.05

    def test_restore_delay(self) -> None:
        """RESTORE_DELAY が 0.1 であること。"""
        assert ClipboardInserter.RESTORE_DELAY == 0.1


class TestClipboardInserterInsert:
    """ClipboardInserter.insert() のテスト。"""

    def _make_mock_pb(self, has_items: bool = True) -> MagicMock:
        """テスト用のNSPasteboardモックを作成する。"""
        mock_pb = MagicMock()
        if has_items:
            mock_item = MagicMock()
            mock_item.types.return_value = ["public.utf8-plain-text"]
            mock_item.dataForType_.return_value = MagicMock()
            mock_pb.pasteboardItems.return_value = [mock_item]
        else:
            mock_pb.pasteboardItems.return_value = []
        return mock_pb

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_saves_clipboard_before_insert(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """insert() 前にクリップボード内容を退避すること（REQ-006）。"""
        mock_pb = self._make_mock_pb(has_items=True)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb

        inserter = ClipboardInserter()
        inserter.insert("新しいテキスト")

        # pasteboardItems() でアイテム一覧を取得したことを確認
        mock_pb.pasteboardItems.assert_called()

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_sets_text_to_clipboard(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """insert() でテキストをクリップボードにセットすること（REQ-005）。"""
        mock_pb = self._make_mock_pb(has_items=False)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb

        inserter = ClipboardInserter()
        inserter.insert("挿入するテキスト")

        mock_pb.setString_forType_.assert_called()
        call_args = mock_pb.setString_forType_.call_args_list
        texts = [str(c.args[0]) for c in call_args]
        assert "挿入するテキスト" in texts

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_sends_cmd_v(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """insert() でCmd+Vキーストロークを送信すること（REQ-005）。"""
        mock_pb = self._make_mock_pb(has_items=False)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb

        inserter = ClipboardInserter()
        inserter.insert("テスト")

        assert mock_post.call_count >= 2  # key down + key up

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_restores_clipboard_after_insert(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """insert() 後にクリップボード内容を復元すること（REQ-006）。"""
        mock_pb = self._make_mock_pb(has_items=True)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb

        inserter = ClipboardInserter()
        inserter.insert("新しいテキスト")

        # 全アイテムを writeObjects_ で復元したことを確認
        mock_pb.writeObjects_.assert_called_once()

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_restores_clipboard_even_on_error(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """Cmd+V送信がエラーになっても、クリップボードを復元すること。"""
        mock_pb = self._make_mock_pb(has_items=True)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb
        mock_post.side_effect = Exception("CGEvent error")

        inserter = ClipboardInserter()
        inserter.insert("新しいテキスト")

        # エラーが起きても writeObjects_ で復元される
        mock_pb.writeObjects_.assert_called_once()

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_restores_empty_when_clipboard_was_empty(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """クリップボードが空だった場合、clearContents のみで復元しないこと。"""
        mock_pb = self._make_mock_pb(has_items=False)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb

        inserter = ClipboardInserter()
        inserter.insert("新しいテキスト")

        # アイテムがない場合は writeObjects_ を呼ばない
        mock_pb.writeObjects_.assert_not_called()
        # clearContents は呼ばれる
        mock_pb.clearContents.assert_called()
