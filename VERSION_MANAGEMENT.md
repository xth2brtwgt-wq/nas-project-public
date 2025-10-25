# バージョン管理について

## 📋 概要

Meeting Minutes BYCアプリケーションのバージョン情報は、`config/version.py`で一元管理されています。

## 🗂️ ファイル構成

```
meeting-minutes-byc/
├── config/
│   └── version.py          # バージョン情報の一元管理
├── app.py                  # メインアプリケーション
├── utils/
│   ├── email_sender.py     # メール送信ユーティリティ
│   └── markdown_generator.py # Markdown生成ユーティリティ
└── README.md               # プロジェクトドキュメント
```

## 🔧 バージョン情報の管理

### config/version.py

```python
# アプリケーション情報
APP_NAME = "Meeting Minutes BYC"
APP_VERSION = "1.0.2"
APP_DESCRIPTION = "音声文字起こし・議事録生成アプリケーション"

# バージョン履歴
VERSION_HISTORY = {
    "1.0.0": "初回リリース",
    "1.0.1": "UI改善とバグ修正 - 結果画面の不要な文言削除、WebSocket接続ステータス削除、進捗バーテストボタン削除、メール件名・本文の修正、システムバージョン表示追加",
    "1.0.2": "カスタム辞書機能の追加 - 音声文字起こし精度向上のための辞書管理システム、専門用語・固有名詞の誤認識防止機能"
}
```

### 各ファイルでの使用方法

```python
# バージョン情報をインポート
from config.version import APP_NAME, APP_VERSION

# 使用例
print(f"{APP_NAME} v{APP_VERSION}")
```

## 📝 バージョンアップ手順

1. **config/version.pyを更新**
   ```python
   APP_VERSION = "1.0.2"  # 新しいバージョン番号
   ```

2. **VERSION_HISTORYに追加**
   ```python
   VERSION_HISTORY = {
       "1.0.0": "初回リリース",
       "1.0.1": "UI改善とバグ修正...",
       "1.0.2": "新機能追加..."  # 新しいエントリ
   }
   ```

3. **ドキュメントの更新**
   - README.md
   - PROJECT_STRUCTURE.md
   - TEST_RESULTS.md

4. **Gitコミット**
   ```bash
   git add -A
   git commit -m "v1.0.2: 新機能追加"
   git push origin main
   ```

## ✅ メリット

- **一元管理**: バージョン情報が1箇所に集約
- **保守性向上**: バージョン変更時の修正箇所が明確
- **一貫性確保**: 全ファイルで同じバージョン情報を使用
- **履歴管理**: バージョン履歴を追跡可能

## 🔍 確認方法

### アプリケーション内での確認
```python
from config.version import get_version_info, get_version_string

# バージョン情報を取得
version_info = get_version_info()
print(version_info)  # {'name': 'Meeting Minutes BYC', 'version': '1.0.2', 'description': '...'}

# バージョン文字列を取得
version_string = get_version_string()
print(version_string)  # Meeting Minutes BYC v1.0.2
```

### コマンドラインでの確認
```bash
cd meeting-minutes-byc
python3 -c "from config.version import get_version_string; print(get_version_string())"
```

## 📚 関連ファイル

- `config/version.py` - バージョン情報の定義
- `app.py` - メインアプリケーション
- `utils/email_sender.py` - メール送信ユーティリティ
- `utils/markdown_generator.py` - Markdown生成ユーティリティ
- `README.md` - プロジェクトドキュメント
- `PROJECT_STRUCTURE.md` - プロジェクト構造ドキュメント
- `TEST_RESULTS.md` - テスト結果ドキュメント
