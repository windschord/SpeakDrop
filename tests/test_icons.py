"""Icons モジュールのテスト。"""

from speakdrop import icons


def test_icon_idle_is_string() -> None:
    """ICON_IDLEが文字列である。"""
    assert isinstance(icons.ICON_TEXTS["IDLE"], str)


def test_icon_recording_is_string() -> None:
    """ICON_RECORDINGが文字列である。"""
    assert isinstance(icons.ICON_TEXTS["RECORDING"], str)


def test_icon_processing_is_string() -> None:
    """ICON_PROCESSINGが文字列である。"""
    assert isinstance(icons.ICON_TEXTS["PROCESSING"], str)


def test_icons_have_different_values() -> None:
    """各ICONが異なる値を持つ。"""
    values = list(icons.ICON_TEXTS.values())
    assert len(values) == len(set(values)), "各アイコンは異なる値を持つ必要がある"


def test_status_idle_is_correct() -> None:
    """STATUS_IDLEが「待機中」である。"""
    assert icons.STATUS_IDLE == "待機中"


def test_status_recording_is_nonempty_string() -> None:
    """STATUS_RECORDINGが空でない文字列である。"""
    assert isinstance(icons.STATUS_RECORDING, str)
    assert len(icons.STATUS_RECORDING) > 0


def test_icon_texts_has_three_states() -> None:
    """ICON_TEXTSが3状態を持つ。"""
    assert "IDLE" in icons.ICON_TEXTS
    assert "RECORDING" in icons.ICON_TEXTS
    assert "PROCESSING" in icons.ICON_TEXTS


def test_get_icon_title_returns_idle_for_unknown_state() -> None:
    """未知の状態ではIDLEアイコンを返す。"""

    class FakeState:
        name = "UNKNOWN"

    result = icons.get_icon_title(FakeState())
    assert result == icons.ICON_TEXTS["IDLE"]


def test_get_icon_title_returns_correct_icon_for_each_state() -> None:
    """各状態に対応するアイコンを返す。"""

    class FakeState:
        def __init__(self, name: str) -> None:
            self.name = name

    for state_name, expected_icon in icons.ICON_TEXTS.items():
        result = icons.get_icon_title(FakeState(state_name))
        assert result == expected_icon, f"{state_name} のアイコンが一致しない"
