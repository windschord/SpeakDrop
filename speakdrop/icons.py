"""メニューバーアイコン生成モジュール。

AppState に対応するメニューバーアイコン（または文字列タイトル）を提供する。
NFR-007: 状態変化を 200ms 以内に反映するため、シンプルな文字列定数を使用。
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class _HasName(Protocol):
    """name 属性を持つオブジェクトのプロトコル（AppState 互換）。"""

    @property
    def name(self) -> str:
        """状態名を返す。"""
        ...


# 状態別のアイコン文字列（タイトル方式）
ICON_TEXTS: dict[str, str] = {
    "IDLE": "🎤",  # 待機中（マイクアイコン）
    "RECORDING": "🔴",  # 録音中（赤丸）
    "PROCESSING": "⏳",  # 処理中（砂時計）
}

# 状態別の説明テキスト（メニューに表示される）
STATUS_IDLE = "待機中"
STATUS_RECORDING = "録音中..."
STATUS_PROCESSING = "処理中..."
STATUS_DISABLED = "無効"


def get_icon_title(state: _HasName) -> str:
    """AppState に対応するメニューバーアイコン文字列を返す。

    Args:
        state: name 属性を持つ状態オブジェクト（AppState 互換）

    Returns:
        メニューバーに表示する文字列（絵文字）
    """
    return ICON_TEXTS.get(state.name, ICON_TEXTS["IDLE"])
