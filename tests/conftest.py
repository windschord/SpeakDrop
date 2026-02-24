"""pytest 設定ファイル。

テスト全体で共有するフィクスチャや設定を定義する。
test_app.py がモジュールレベルで numpy をモック化するため、
conftest でテスト収集開始前に実際の numpy を sys.modules に登録しておく。
"""

import sys

# test_app.py より先に numpy を sys.modules に登録することで、
# test_app.py の sys.modules.setdefault("numpy", MagicMock()) が
# 実際の numpy を上書きしないことを保証する。
import numpy  # noqa: F401

# numpy が正規モジュールとして登録されていることを確認
assert sys.modules.get("numpy") is not None
assert not hasattr(sys.modules["numpy"], "_mock_name"), (
    "numpy が MagicMock に置き換えられています。conftest.py のロード順を確認してください。"
)
