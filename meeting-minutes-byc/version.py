"""
バージョン情報
"""

__version__ = "1.2.0"
__version_info__ = (1, 2, 0)
__build_date__ = "2025-10-23"
__author__ = "Yoshi"
__description__ = "プロジェクト説明"

# バージョン履歴
VERSION_HISTORY = [
    {
        "version": "1.2.0",
        "date": "2025-10-23",
        "changes": [
                "Fix Safari m4a file support: Add audio/x-m4a MIME type support",
                "Docker Compose env_file設定の統一 - meeting-minutes-bycとnas-dashboardのenv_file設定を.envに統一",
                "resolve: マージコンフリクト解決 - .envファイル削除、.gitignore統合",
                "完全復元と安定化 - バックアップからの完全復元、メール送信・Notion登録機能の修正、WebSocket接続の安定化、履歴機能の復旧、環境設定の最適化、フォルダ構造の整理",
                "Remove .env from Git tracking"
        ]
    },
    {
        "version": "1.1.1",
        "date": "2025-10-23",
        "changes": [
                "Fix Safari m4a file support: Add audio/x-m4a MIME type support",
                "Docker Compose env_file設定の統一 - meeting-minutes-bycとnas-dashboardのenv_file設定を.envに統一",
                "resolve: マージコンフリクト解決 - .envファイル削除、.gitignore統合",
                "完全復元と安定化 - バックアップからの完全復元、メール送信・Notion登録機能の修正、WebSocket接続の安定化、履歴機能の復旧、環境設定の最適化、フォルダ構造の整理",
                "Remove .env from Git tracking"
        ]
    },
    {
        "version": "1.1.0",
        "date": "2025-10-22",
        "changes": [
                "Fix Safari m4a file support: Add audio/x-m4a MIME type support",
                "Docker Compose env_file設定の統一 - meeting-minutes-bycとnas-dashboardのenv_file設定を.envに統一",
                "resolve: マージコンフリクト解決 - .envファイル削除、.gitignore統合",
                "完全復元と安定化 - バックアップからの完全復元、メール送信・Notion登録機能の修正、WebSocket接続の安定化、履歴機能の復旧、環境設定の最適化、フォルダ構造の整理",
                "Remove .env from Git tracking"
        ]
    },
    {
        "version": "1.0.0",
        "date": "2025-10-20",
        "changes": [
            "初期バージョン",
            "自動バージョン管理機能を追加"
        ]
    }
]
