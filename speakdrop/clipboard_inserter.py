"""クリップボード・テキスト挿入モジュール。

NSPasteboard でクリップボードを操作し、
CGEvent で Cmd+V キーストロークを送信してテキストを挿入する。
挿入前後にクリップボード内容を退避・復元する（REQ-006）。
"""

import logging
import time

from AppKit import NSPasteboardItem, NSPasteboardTypeString
from Cocoa import NSPasteboard
from Quartz.CoreGraphics import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    CGEventSetFlags,
    kCGEventFlagMaskCommand,
    kCGHIDEventTap,
)

_logger = logging.getLogger(__name__)

# 'v' キーのキーコード
_KEY_V = 0x09


class ClipboardInserter:
    """クリップボード経由でテキストを挿入するクラス。"""

    PASTE_DELAY: float = 0.05  # Cmd+V 送信前の待機時間（秒）
    RESTORE_DELAY: float = 0.1  # クリップボード復元前の待機時間（秒）

    def insert(self, text: str) -> None:
        """テキストをアクティブなアプリケーションに挿入する。

        手順:
        1. 既存クリップボード内容を退避（REQ-006）
        2. text をクリップボードにセット
        3. Cmd+V キーストロークを送信（REQ-005）
        4. 待機（RESTORE_DELAY）
        5. クリップボード内容を復元（REQ-006）

        Args:
            text: 挿入するテキスト
        """
        pb = NSPasteboard.generalPasteboard()

        # 1. 退避 - 全クリップボードアイテムの型とデータを保存（REQ-006）
        original_items: list[NSPasteboardItem] = []
        items = pb.pasteboardItems()
        if items:
            for item in items:
                cloned = NSPasteboardItem.new()
                for ptype in item.types():
                    data = item.dataForType_(ptype)
                    if data is not None:
                        cloned.setData_forType_(data, ptype)
                    else:
                        plist = item.propertyListForType_(ptype)
                        if plist is not None:
                            cloned.setPropertyList_forType_(plist, ptype)
                original_items.append(cloned)

        # 2. テキストをクリップボードにセット
        pb.clearContents()
        pb.setString_forType_(text, NSPasteboardTypeString)

        try:
            # 3. Cmd+V を送信
            time.sleep(self.PASTE_DELAY)
            self._send_cmd_v()
        except Exception as e:
            _logger.warning("Cmd+V 送信に失敗しました: %s", e)
        finally:
            # 4. 待機してから復元
            time.sleep(self.RESTORE_DELAY)
            # 5. 復元（REQ-006）
            pb.clearContents()
            if original_items:
                pb.writeObjects_(original_items)

    def _send_cmd_v(self) -> None:
        """Cmd+V キーストロークを送信する。"""
        # Key down
        event_down = CGEventCreateKeyboardEvent(None, _KEY_V, True)
        CGEventSetFlags(event_down, kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, event_down)

        # Key up
        event_up = CGEventCreateKeyboardEvent(None, _KEY_V, False)
        CGEventSetFlags(event_up, kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, event_up)
