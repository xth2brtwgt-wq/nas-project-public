"""
Amazon Purchase Analytics System - バージョン管理
"""
from datetime import datetime

# バージョン情報
VERSION = "1.0.1"
VERSION_NAME = "初期リリース版"
RELEASE_DATE = "2025-10-21"
BUILD_NUMBER = 1

# 機能リスト
FEATURES = [
    "Amazon CSV購入履歴の自動取り込み",
    "Gemini AI による自動カテゴリ分類",
    "購買パターン分析（衝動買い検出）",
    "定期購入候補の提案",
    "月次インサイト生成（節約アドバイス）",
    "カテゴリ別支出グラフ",
    "月別推移グラフ",
    "CSV エクスポート機能",
    "レスポンシブWebダッシュボード",
    "ドラッグ&ドロップファイルアップロード",
]

# バージョン履歴
VERSION_HISTORY = [
    {
        "version": "1.0.1",
        "date": "2025-11-07",
        "changes": [
            "fix: ESLintエラーを修正（confirmをwindow.confirmに変更）"
        ]
    },
    {
        "version": "1.0.0",
        "date": "2025-10-21",
        "name": "初期リリース版",
        "build": 1,
        "changes": [
            "CSV自動取り込み機能（Retail.OrderHistory.3.csv対応）",
            "PostgreSQL + Redisデータベース統合",
            "Gemini AI自動カテゴリ分類機能",
            "衝動買いパターン検出",
            "定期購入候補の提案",
            "月次インサイト生成（AIアドバイス）",
            "カテゴリ別・月別グラフ生成",
            "レポートCSVエクスポート",
            "Webダッシュボード（Chart.js統合）",
            "Docker Compose構成",
        ]
    }
]

# システム情報
SYSTEM_INFO = {
    "name": "Amazon Purchase Analytics System",
    "description": "Amazon購入履歴分析システム",
    "author": "Yoshi",
    "license": "MIT",
    "repository": "nas-project/amazon-analytics",
}


def get_version_info():
    """バージョン情報を取得"""
    return {
        "version": VERSION,
        "version_name": VERSION_NAME,
        "release_date": RELEASE_DATE,
        "build_number": BUILD_NUMBER,
        "features": FEATURES,
        "system": SYSTEM_INFO,
    }


def get_version_history():
    """バージョン履歴を取得"""
    return VERSION_HISTORY


def get_full_version():
    """完全なバージョン文字列を取得"""
    return f"{VERSION} (Build {BUILD_NUMBER})"


def increment_version(part="patch"):
    """
    バージョンを自動インクリメント
    
    Args:
        part: "major", "minor", "patch" のいずれか
    """
    global VERSION, BUILD_NUMBER, RELEASE_DATE
    
    major, minor, patch = map(int, VERSION.split("."))
    
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    
    VERSION = f"{major}.{minor}.{patch}"
    BUILD_NUMBER += 1
    RELEASE_DATE = datetime.now().strftime("%Y-%m-%d")
    
    return VERSION


def add_version_history(version_name, changes):
    """
    バージョン履歴に新しいエントリを追加
    
    Args:
        version_name: バージョン名
        changes: 変更内容のリスト
    """
    global VERSION_HISTORY
    
    new_entry = {
        "version": VERSION,
        "date": RELEASE_DATE,
        "name": version_name,
        "build": BUILD_NUMBER,
        "changes": changes,
    }
    
    VERSION_HISTORY.insert(0, new_entry)
    return new_entry


# エイリアス
__version__ = VERSION
__author__ = SYSTEM_INFO["author"]
__description__ = SYSTEM_INFO["description"]


if __name__ == "__main__":
    # バージョン情報を表示
    print(f"=== {SYSTEM_INFO['name']} ===")
    print(f"Version: {get_full_version()}")
    print(f"Release: {RELEASE_DATE}")
    print(f"Author: {__author__}")
    print()
    print("Features:")
    for feature in FEATURES:
        print(f"  - {feature}")
