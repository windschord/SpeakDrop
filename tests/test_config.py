"""Config モジュールのテスト。"""

import json
from pathlib import Path

from speakdrop.config import CONFIG_PATH, Config


class TestConfigDefaults:
    """Config デフォルト値のテスト。"""

    def test_default_hotkey(self) -> None:
        """デフォルトのホットキーは 'alt_r' であること。"""
        config = Config()
        assert config.hotkey == "alt_r"

    def test_default_model(self) -> None:
        """デフォルトのモデルは 'kotoba-tech/kotoba-whisper-v1.0' であること。"""
        config = Config()
        assert config.model == "kotoba-tech/kotoba-whisper-v1.0"

    def test_default_enabled(self) -> None:
        """デフォルトの enabled は True であること。"""
        config = Config()
        assert config.enabled is True

    def test_default_ollama_model(self) -> None:
        """デフォルトの ollama_model は 'qwen2.5:7b' であること。"""
        config = Config()
        assert config.ollama_model == "qwen2.5:7b"

    def test_config_path(self) -> None:
        """CONFIG_PATH が正しいパスを指すこと。"""
        expected = Path.home() / ".config" / "speakdrop" / "config.json"
        assert CONFIG_PATH == expected


class TestConfigLoad:
    """Config.load() のテスト。"""

    def test_load_returns_self(self, tmp_path: Path) -> None:
        """load() が Config インスタンス自身を返すこと。"""
        config = Config()
        result = config.load(config_path=tmp_path / "config.json")
        assert result is config

    def test_load_from_existing_file(self, tmp_path: Path) -> None:
        """設定ファイルが存在する場合に正しく読み込むこと。"""
        config_file = tmp_path / "config.json"
        config_data = {
            "hotkey": "ctrl_r",
            "model": "small",
            "enabled": False,
            "ollama_model": "qwen2.5:3b",
        }
        config_file.write_text(json.dumps(config_data))

        config = Config()
        config.load(config_path=config_file)

        assert config.hotkey == "ctrl_r"
        assert config.model == "small"
        assert config.enabled is False
        assert config.ollama_model == "qwen2.5:3b"

    def test_load_nonexistent_file_uses_defaults(self, tmp_path: Path) -> None:
        """設定ファイルが存在しない場合はデフォルト値を維持すること。"""
        config = Config()
        config.load(config_path=tmp_path / "nonexistent.json")

        assert config.hotkey == "alt_r"
        assert config.model == "kotoba-tech/kotoba-whisper-v1.0"
        assert config.enabled is True
        assert config.ollama_model == "qwen2.5:7b"

    def test_load_partial_config(self, tmp_path: Path) -> None:
        """部分的な設定ファイルの場合、存在するキーのみ上書きすること。"""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"hotkey": "ctrl_r"}))

        config = Config()
        config.load(config_path=config_file)

        assert config.hotkey == "ctrl_r"
        assert config.model == "kotoba-tech/kotoba-whisper-v1.0"  # デフォルト維持


class TestConfigSave:
    """Config.save() のテスト。"""

    def test_save_creates_file(self, tmp_path: Path) -> None:
        """save() がJSONファイルを作成すること。"""
        config_file = tmp_path / "config.json"
        config = Config(hotkey="ctrl_r", model="small", enabled=False)
        config.save(config_path=config_file)

        assert config_file.exists()

    def test_save_correct_json_content(self, tmp_path: Path) -> None:
        """save() が正しいJSON内容を書き込むこと。"""
        config_file = tmp_path / "config.json"
        config = Config(hotkey="ctrl_r", model="small", enabled=False, ollama_model="gemma3:4b")
        config.save(config_path=config_file)

        saved = json.loads(config_file.read_text())
        assert saved["hotkey"] == "ctrl_r"
        assert saved["model"] == "small"
        assert saved["enabled"] is False
        assert saved["ollama_model"] == "gemma3:4b"

    def test_save_creates_parent_directory(self, tmp_path: Path) -> None:
        """save() が親ディレクトリが存在しない場合でも作成して保存すること。"""
        config_file = tmp_path / "nested" / "dir" / "config.json"
        config = Config()
        config.save(config_path=config_file)

        assert config_file.exists()

    def test_roundtrip(self, tmp_path: Path) -> None:
        """save() してから load() すると同じ値になること。"""
        config_file = tmp_path / "config.json"
        original = Config(hotkey="shift_r", model="medium", enabled=False, ollama_model="gemma3:4b")
        original.save(config_path=config_file)

        loaded = Config()
        loaded.load(config_path=config_file)

        assert loaded.hotkey == original.hotkey
        assert loaded.model == original.model
        assert loaded.enabled == original.enabled
        assert loaded.ollama_model == original.ollama_model
