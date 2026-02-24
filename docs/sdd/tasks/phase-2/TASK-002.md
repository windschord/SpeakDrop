# TASK-002: Config モジュール（TDD）

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**Config モジュール** をTDD方式で実装してください。

### 実装の目標

`~/.config/speakdrop/config.json` の読み書きを行う設定管理モジュールを実装します。
TDD原則に従い、まずテストを作成・コミットし、その後テストをパスする実装を行います。
設計書で定義された `Config` dataclass と `CONFIG_PATH` を実装します。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 作成 | `tests/test_config.py` | テストファイル（先行作成） |
| 変更 | `speakdrop/config.py` | Config モジュール本実装 |

---

## 技術的コンテキスト

### 使用技術

- 言語: Python 3.11+
- テストフレームワーク: pytest + pytest-mock
- 使用標準ライブラリ: `dataclasses`, `json`, `pathlib`

### 参照すべきファイル

- `@speakdrop/config.py` - 現在のスタブ（TASK-001で作成済み）

### 関連する設計書

- `@docs/sdd/design/design.md` の「Config」セクション（行389-424）

### 関連する要件

- `@docs/sdd/requirements/stories/US-004.md` - ホットキーの設定
- `@docs/sdd/requirements/stories/US-005.md` - 音声認識モデルの設定

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [ ] `tests/test_config.py` が作成されている（テストが7件以上）
- [ ] `speakdrop/config.py` が実装されている
- [ ] `Config` dataclass が `hotkey: str = "alt_r"`、`model: str = "kotoba-tech/kotoba-whisper-v1.0"`、`enabled: bool = True` のデフォルト値を持つ
- [ ] `CONFIG_PATH = Path.home() / ".config" / "speakdrop" / "config.json"` が定義されている
- [ ] `Config.load()` が設定ファイル存在時に正しく読み込む
- [ ] `Config.load()` が設定ファイル不在時にデフォルト値を返す
- [ ] `Config.save()` がJSONファイルを正しく書き込む
- [ ] `Config.save()` が親ディレクトリが存在しない場合でも正しく作成して書き込む
- [ ] `uv run pytest tests/test_config.py -v` で全テストパス
- [ ] `uv run ruff check speakdrop/config.py tests/test_config.py` でエラー0件
- [ ] `uv run mypy speakdrop/config.py` でエラー0件

---

## 実装手順

### ステップ1: テストを先に作成（TDD）

`tests/test_config.py` を作成し、以下のテストケースを実装してください：

```python
"""Config モジュールのテスト。"""
import json
from pathlib import Path

import pytest

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
        }
        config_file.write_text(json.dumps(config_data))

        config = Config()
        config.load(config_path=config_file)

        assert config.hotkey == "ctrl_r"
        assert config.model == "small"
        assert config.enabled is False

    def test_load_nonexistent_file_uses_defaults(self, tmp_path: Path) -> None:
        """設定ファイルが存在しない場合はデフォルト値を維持すること。"""
        config = Config()
        config.load(config_path=tmp_path / "nonexistent.json")

        assert config.hotkey == "alt_r"
        assert config.model == "kotoba-tech/kotoba-whisper-v1.0"
        assert config.enabled is True

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
        config = Config(hotkey="ctrl_r", model="small", enabled=False)
        config.save(config_path=config_file)

        saved = json.loads(config_file.read_text())
        assert saved["hotkey"] == "ctrl_r"
        assert saved["model"] == "small"
        assert saved["enabled"] is False

    def test_save_creates_parent_directory(self, tmp_path: Path) -> None:
        """save() が親ディレクトリが存在しない場合でも作成して保存すること。"""
        config_file = tmp_path / "nested" / "dir" / "config.json"
        config = Config()
        config.save(config_path=config_file)

        assert config_file.exists()

    def test_roundtrip(self, tmp_path: Path) -> None:
        """save() してから load() すると同じ値になること。"""
        config_file = tmp_path / "config.json"
        original = Config(hotkey="shift_r", model="medium", enabled=False)
        original.save(config_path=config_file)

        loaded = Config()
        loaded.load(config_path=config_file)

        assert loaded.hotkey == original.hotkey
        assert loaded.model == original.model
        assert loaded.enabled == original.enabled
```

**重要**: `load()` と `save()` はテスタビリティのために `config_path: Path = CONFIG_PATH` のオプション引数を受け取る設計にしてください。

テストを実行して全テストが失敗することを確認：

```bash
cd <project-root>
uv run pytest tests/test_config.py -v
```

コミット：

```text
test: test_config.py - Config モジュールのTDDテスト追加
```

### ステップ2: Config モジュールを実装

`speakdrop/config.py` を実装してください：

```python
"""設定管理モジュール。

設定を ~/.config/speakdrop/config.json に保存・読み込みする。
"""
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "speakdrop" / "config.json"


@dataclass
class Config:
    """アプリケーション設定。"""

    hotkey: str = "alt_r"
    model: str = "kotoba-tech/kotoba-whisper-v1.0"
    enabled: bool = True

    def load(self, config_path: Path = CONFIG_PATH) -> "Config":
        """設定ファイルが存在すれば読み込む（REQ-017）。

        Args:
            config_path: 設定ファイルのパス（デフォルト: CONFIG_PATH）

        Returns:
            self（メソッドチェーン対応）
        """
        if config_path.exists():
            data = json.loads(config_path.read_text(encoding="utf-8"))
            for key, value in data.items():
                if hasattr(self, key):
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
```

### ステップ3: テストがパスすることを確認

```bash
cd <project-root>
uv run pytest tests/test_config.py -v
uv run ruff check speakdrop/config.py tests/test_config.py
uv run mypy speakdrop/config.py
```

### ステップ4: コミット

```
feat: config.py - Config モジュール実装（設定JSON読み書き、REQ-016/017）
```

---

## 実装の詳細仕様

### Config dataclass

```python
@dataclass
class Config:
    hotkey: str = "alt_r"                              # 右Optionキー
    model: str = "kotoba-tech/kotoba-whisper-v1.0"    # Kotoba Whisper
    enabled: bool = True                               # 音声入力有効/無効
```

### 入出力仕様

**`Config.load(config_path: Path = CONFIG_PATH) -> Config`:**
- 入力: 設定ファイルのパス（オプション）
- 出力: selfを返す（メソッドチェーン対応）
- ファイルが存在しない場合: デフォルト値のまま self を返す
- ファイルが存在する場合: ファイルの値で上書きして返す

**`Config.save(config_path: Path = CONFIG_PATH) -> None`:**
- 入力: 保存先パス（オプション）
- 出力: なし
- 副作用: JSONファイルを書き込む、親ディレクトリを作成する

### エラー処理

- JSONパースエラー: 現時点では例外をそのまま伝播させる（設計書に指定なし）
- ファイル読み取りエラー: 現時点では例外をそのまま伝播させる

---

## 注意事項

- `load()` と `save()` の `config_path` 引数はテスト用の差し込み口として必須
- `dataclasses.asdict()` を使ってJSONシリアライズすること
- `ensure_ascii=False` でUTF-8として保存すること
- mypy strict モードに適合させること（戻り値型・引数型は必ず明記）

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-002 |
| **ステータス** | `TODO` |
| **推定工数** | 25分 |
| **依存関係** | [TASK-001](../phase-1/TASK-001.md) @../phase-1/TASK-001.md |
| **対応要件** | REQ-016, REQ-017 |
| **対応設計** | Config セクション（設計書行389-424） |

---

## 情報の明確性チェック

### 明示された情報

- [x] 設定ファイルパス: `~/.config/speakdrop/config.json`
- [x] 設定項目: hotkey, model, enabled とデフォルト値
- [x] 実装方式: `dataclasses.dataclass`
- [x] JSONシリアライズ: `json` 標準ライブラリ

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| JSONパースエラー時の挙動 | 例外をそのまま伝播させる | [x] 設計書に記載なしのため伝播で実装 |

---

## 作業ログ（実装時に記入）

### YYYY-MM-DD
- **作業内容**:
- **発生した問題**:
- **解決方法**:
- **コミットハッシュ**:
