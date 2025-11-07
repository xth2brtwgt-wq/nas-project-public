"""
YouTube to Notion Summarizer - バージョン情報管理
"""

# アプリケーション情報
APP_NAME = "YouTube to Notion Summarizer"
APP_VERSION = "1.2.0"
APP_DESCRIPTION = "YouTube動画要約・Notion自動投稿システム"

# バージョン履歴
VERSION_HISTORY = {
    "1.2.0": "feat: フロントエンドにブラックリストIP管理UIを追加",
    "1.1.0": "feat: 全画面で固定ヘッダーを実装、議事録画面のレイアウト改善",
    "1.0.0": "初回リリース - YouTube動画要約・Notion自動投稿機能"
}

def get_version_info():
    """バージョン情報を取得"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION
    }

def get_version_history():
    """バージョン履歴を取得"""
    return VERSION_HISTORY
