"""macOS権限確認モジュール。

マイク権限（AVFoundation）とアクセシビリティ権限（ApplicationServices）を確認する。
権限不足の場合はユーザーに案内する（REQ-021, REQ-022）。
"""
from AVFoundation import (
    AVCaptureDevice,
    AVMediaTypeAudio,
)
from ApplicationServices import AXIsProcessTrustedWithOptions

# AVAuthorizationStatus 定数（pyobjc が提供するが、テスト安定性のため数値で定義）
# https://developer.apple.com/documentation/avfoundation/avauthorizationstatus
_AV_AUTH_STATUS_NOT_DETERMINED = 0  # 未確認
_AV_AUTH_STATUS_AUTHORIZED = 3  # 許可済み


class PermissionChecker:
    """macOS システム権限の確認・要求クラス。"""

    def check_microphone(self) -> bool:
        """マイク権限を確認する（REQ-021）。

        権限が未確認の場合は権限要求ダイアログを表示する。

        Returns:
            権限が付与されている場合は True、それ以外は False
        """
        status = AVCaptureDevice.authorizationStatusForMediaType_(AVMediaTypeAudio)

        if status == _AV_AUTH_STATUS_AUTHORIZED:
            return True

        if status == _AV_AUTH_STATUS_NOT_DETERMINED:
            # 権限要求ダイアログを表示（非同期）
            AVCaptureDevice.requestAccessForMediaType_completionHandler_(
                AVMediaTypeAudio,
                lambda granted: None,
            )

        return False

    def check_accessibility(self) -> bool:
        """アクセシビリティ権限を確認する（REQ-022）。

        AXIsProcessTrustedWithOptions() API で権限を確認する。

        Returns:
            権限が付与されている場合は True、それ以外は False
        """
        # prompt=True でシステム環境設定への案内を表示
        result = AXIsProcessTrustedWithOptions({"AXTrustedCheckOptionPrompt": True})
        return bool(result)
