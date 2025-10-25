"""
アプリケーションバージョン管理
"""

# バージョン情報
VERSION = "1.0.0"
VERSION_NAME = "初期リリース版"
RELEASE_DATE = "2025-10-19"

# 機能リスト
FEATURES = [
    "Google Cloud Vision API による高精度OCR",
    "Gemini AI による自動要約・分類",
    "動的カテゴリ生成（13種類の固定カテゴリ + 柔軟な自動生成）",
    "個別マークダウンエクスポート（ZIP）",
    "元ファイル一括ダウンロード（ZIP）",
    "AI統合要約機能",
    "ドラッグ&ドロップファイルアップロード",
    "日本語対応UI",
]

# バージョン履歴
VERSION_HISTORY = [
    {
        "version": "1.0.0",
        "date": "2025-10-19",
        "name": "初期リリース版",
        "changes": [
            "基本的なドキュメント処理機能の実装",
            "OCR処理（Google Cloud Vision API）",
            "AI要約・分類（Gemini 2.5 Flash）",
            "動的カテゴリ生成機能",
            "マークダウンエクスポート機能",
            "統合要約機能",
            "ファイル一括ダウンロード機能",
        ]
    }
]


def get_version_info():
    """バージョン情報を取得"""
    return {
        "version": VERSION,
        "version_name": VERSION_NAME,
        "release_date": RELEASE_DATE,
        "features": FEATURES
    }


def get_version_history():
    """バージョン履歴を取得"""
    return VERSION_HISTORY

