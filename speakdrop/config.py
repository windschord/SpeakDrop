"""設定管理モジュール。

設定を ~/.config/speakdrop/config.json に保存・読み込みする。
"""

from dataclasses import asdict, dataclass, fields
import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "speakdrop" / "config.json"


@dataclass
class Config:
    """アプリケーション設定。"""

    hotkey: str = "alt_r"
    model: str = "kotoba-tech/kotoba-whisper-v1.0"
    enabled: bool = True
    ollama_model: str = "qwen2.5:7b"

    def load(self, config_path: Path = CONFIG_PATH) -> "Config":
        """設定ファイルが存在すれば読み込む（REQ-017）。

        Args:
            config_path: 設定ファイルのパス（デフォルト: CONFIG_PATH）

        Returns:
            self（メソッドチェーン対応）
        """
        if config_path.exists():
            try:
                data: object = json.loads(config_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return self
            if not isinstance(data, dict):
                return self
            # str と bool のみ対応（他の型を追加した場合はここも更新が必要）
            expected_types = {f.name: f.type for f in fields(self)}
            for key, value in data.items():
                expected = expected_types.get(key)
                if expected is str and isinstance(value, str):
                    setattr(self, key, value)
                elif expected is bool and isinstance(value, bool):
                    setattr(self, key, value)
        return self

    def save(self, config_path: Path = CONFIG_PATH) -> None:
        """設定をJSONファイルへ永続化（REQ-016）。

        Args:
            config_path: 保存先パス（デフォルト: CONFIG_PATH）
        """
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps(asdict(self), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
