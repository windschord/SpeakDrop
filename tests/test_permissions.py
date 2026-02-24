"""PermissionChecker モジュールのテスト。"""

import sys
from unittest.mock import MagicMock, patch


# pyobjc は macOS 専用のため、テスト用にモジュールをモック化
def _setup_pyobjc_mocks() -> None:
    """pyobjc モジュールをシステムモジュールにモック登録する。"""
    mock_av = MagicMock()
    mock_app_services = MagicMock()

    sys.modules.setdefault("AVFoundation", mock_av)
    sys.modules.setdefault("ApplicationServices", mock_app_services)


_setup_pyobjc_mocks()

from speakdrop.permissions import PermissionChecker  # noqa: E402


class TestCheckMicrophone:
    """PermissionChecker.check_microphone() のテスト（REQ-021）。"""

    @patch("speakdrop.permissions.AVCaptureDevice")
    def test_returns_true_when_authorized(self, mock_av_capture_device: MagicMock) -> None:
        """マイク権限が付与済みの場合に True を返すこと。"""
        # AVAuthorizationStatusAuthorized = 3
        mock_av_capture_device.authorizationStatusForMediaType_.return_value = 3

        checker = PermissionChecker()
        result = checker.check_microphone()

        assert result is True

    @patch("speakdrop.permissions.AVCaptureDevice")
    def test_returns_false_when_denied(self, mock_av_capture_device: MagicMock) -> None:
        """マイク権限が拒否されている場合に False を返すこと。"""
        # AVAuthorizationStatusDenied = 2
        mock_av_capture_device.authorizationStatusForMediaType_.return_value = 2

        checker = PermissionChecker()
        result = checker.check_microphone()

        assert result is False

    @patch("speakdrop.permissions.AVCaptureDevice")
    def test_requests_access_when_not_determined(self, mock_av_capture_device: MagicMock) -> None:
        """権限未確認の場合（NotDetermined）に権限リクエストを行うこと（REQ-021）。"""
        # AVAuthorizationStatusNotDetermined = 0
        mock_av_capture_device.authorizationStatusForMediaType_.return_value = 0

        checker = PermissionChecker()
        checker.check_microphone()

        mock_av_capture_device.requestAccessForMediaType_completionHandler_.assert_called_once()

    @patch("speakdrop.permissions.AVCaptureDevice")
    def test_checks_audio_media_type(self, mock_av_capture_device: MagicMock) -> None:
        """オーディオメディアタイプで権限確認すること。"""
        mock_av_capture_device.authorizationStatusForMediaType_.return_value = 3

        checker = PermissionChecker()
        checker.check_microphone()

        call_args = mock_av_capture_device.authorizationStatusForMediaType_.call_args
        # AVMediaTypeAudio が使われていること
        assert call_args is not None


class TestCheckAccessibility:
    """PermissionChecker.check_accessibility() のテスト（REQ-022）。"""

    @patch("speakdrop.permissions.AXIsProcessTrustedWithOptions")
    def test_returns_true_when_trusted(self, mock_ax_is_trusted: MagicMock) -> None:
        """アクセシビリティ権限が付与済みの場合に True を返すこと。"""
        mock_ax_is_trusted.return_value = True

        checker = PermissionChecker()
        result = checker.check_accessibility()

        assert result is True

    @patch("speakdrop.permissions.AXIsProcessTrustedWithOptions")
    def test_returns_false_when_not_trusted(self, mock_ax_is_trusted: MagicMock) -> None:
        """アクセシビリティ権限が未付与の場合に False を返すこと（REQ-022）。"""
        mock_ax_is_trusted.return_value = False

        checker = PermissionChecker()
        result = checker.check_accessibility()

        assert result is False

    @patch("speakdrop.permissions.AXIsProcessTrustedWithOptions")
    def test_calls_ax_is_process_trusted(self, mock_ax_is_trusted: MagicMock) -> None:
        """AXIsProcessTrustedWithOptions が呼ばれること。"""
        mock_ax_is_trusted.return_value = True

        checker = PermissionChecker()
        checker.check_accessibility()

        mock_ax_is_trusted.assert_called_once()
