# SpeakDrop

macOS向けのローカル完結型音声入力アプリケーション。メニューバーに常駐し、ホットキーを押している間だけ録音する「プッシュトーク」方式で動作します。

## 特徴

- **完全ローカル処理** — 音声認識・テキスト後処理のすべてをローカル環境で実行。音声データが外部に送信されません
- **日本語特化モデル** — [kotoba-whisper-v1.0](https://huggingface.co/kotoba-tech/kotoba-whisper-v1.0) による高精度な日本語音声認識
- **テキスト後処理** — Ollama LLM（qwen2.5:7b）が句読点挿入・話し言葉整形を自動実行
- **シームレスな挿入** — 認識結果をアクティブなアプリにクリップボード経由で自動挿入

## 動作要件

| 項目 | 要件 |
|------|------|
| OS | macOS 13 以降 |
| CPU | Apple Silicon（M1以上）推奨、Intel Mac も対応 |
| Python | 3.11 以上 |
| 権限 | マイクアクセス・アクセシビリティ |

### 外部ソフトウェア

テキスト後処理を使用する場合は [Ollama](https://ollama.com) が必要です。未起動の場合は認識結果をそのまま挿入します。

```bash
# Ollama インストール後にモデルを取得
ollama pull qwen2.5:7b
```

## インストール

```bash
git clone https://github.com/windschord/SpeakDrop.git
cd SpeakDrop
uv sync
```

## 使い方

### 起動

```bash
uv run speakdrop
# または
uv run python -m speakdrop
```

### 音声入力

1. メニューバーに **🎤** アイコンが表示されます
2. 右Optionキーを**押し続ける** → **🔴** に変わり録音開始
3. 日本語で話す
4. 右Optionキーを**離す** → **⏳** に変わり処理開始
5. 認識・後処理が完了すると、アクティブなアプリにテキストが挿入されます

### メニューバーアイコン

| アイコン | 状態 |
|---------|------|
| 🎤 | 待機中 |
| 🔴 | 録音中 |
| ⏳ | 処理中（認識・後処理・挿入） |

### メニュー

メニューバーアイコンをクリックするとメニューが開きます。

- **音声入力 ON/OFF** — 音声入力機能の有効/無効を切り替え
- **設定...** — 音声認識モデルを変更
- **終了** — アプリを終了

## 設定

設定ファイル: `~/.config/speakdrop/config.json`

| 項目 | デフォルト | 説明 |
|------|-----------|------|
| `hotkey` | `"alt_r"` | プッシュトークキー（右Optionキー） |
| `model` | `"kotoba-tech/kotoba-whisper-v1.0"` | 音声認識モデル |
| `enabled` | `true` | 音声入力の有効/無効 |

### 利用可能なモデル

| モデル | サイズ | 用途 |
|--------|--------|------|
| `kotoba-tech/kotoba-whisper-v1.0` | 約4GB | デフォルト・日本語精度最優先 |
| `large-v3` | 約4GB | 多言語対応 |
| `medium` | 約2GB | メモリ節約 |
| `small` | 約1GB | 超軽量 |

モデルは初回使用時に自動でダウンロードされます。

## macOS 権限の設定

### マイクアクセス

初回起動時に権限要求ダイアログが表示されます。許可されない場合:

**システム設定** → **プライバシーとセキュリティ** → **マイク** → SpeakDrop をオン

### アクセシビリティ

グローバルホットキー監視とテキスト挿入に必要です。

**システム設定** → **プライバシーとセキュリティ** → **アクセシビリティ** → SpeakDrop をオン

権限が不足している場合、音声入力機能は自動的に無効化されます。

## 開発

### セットアップ

```bash
uv sync --dev
```

### テスト

```bash
uv run pytest tests/ -v --cov=speakdrop
```

### コード品質チェック

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy speakdrop/
```

## アーキテクチャ

```text
SpeakDrop/
├── speakdrop/
│   ├── app.py               # メインアプリ（rumps.App）・状態管理
│   ├── audio_recorder.py    # 音声録音（sounddevice、16kHz/Mono）
│   ├── transcriber.py       # 音声認識（faster-whisper、遅延ロード）
│   ├── text_processor.py    # テキスト後処理（Ollama、タイムアウト5秒）
│   ├── clipboard_inserter.py # クリップボード操作・Cmd+V送信（pyobjc）
│   ├── hotkey_listener.py   # グローバルホットキー監視（pynput）
│   ├── config.py            # 設定管理（~/.config/speakdrop/config.json）
│   ├── permissions.py       # macOS権限確認（AVFoundation）
│   └── icons.py             # メニューバーアイコン定数
└── tests/                   # テストスイート（101件、カバレッジ92%）
```

## ライセンス

MIT
