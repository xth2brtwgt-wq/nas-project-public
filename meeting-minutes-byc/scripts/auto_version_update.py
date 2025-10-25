#!/usr/bin/env python3
"""
自動バージョンアップスクリプト
Gitコミット時に自動的にバージョンを更新する
"""

import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path

def get_current_version():
    """現在のバージョンを取得"""
    version_file = Path(__file__).parent.parent / "version.py"
    if not version_file.exists():
        return None
    
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # バージョン番号を抽出
    version_match = re.search(r'__version__ = "([^"]+)"', content)
    if version_match:
        return version_match.group(1)
    return None

def update_version(version_type="patch"):
    """バージョンを更新"""
    version_file = Path(__file__).parent.parent / "version.py"
    
    if not version_file.exists():
        print("❌ version.py が見つかりません")
        return False
    
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 現在のバージョンを取得
    version_match = re.search(r'__version__ = "([^"]+)"', content)
    if not version_match:
        print("❌ バージョン情報を取得できません")
        return False
    
    current_version = version_match.group(1)
    major, minor, patch = map(int, current_version.split('.'))
    
    # バージョンを更新
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    new_build_date = datetime.now().strftime("%Y-%m-%d")
    
    # バージョン情報を更新
    content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content)
    content = re.sub(r'__version_info__ = \([^)]+\)', f'__version_info__ = ({major}, {minor}, {patch})', content)
    content = re.sub(r'__build_date__ = "[^"]+"', f'__build_date__ = "{new_build_date}"', content)
    
    # バージョン履歴を更新
    new_history_entry = f'''    {{
        "version": "{new_version}",
        "date": "{new_build_date}",
        "changes": [
            "自動バージョンアップ: {version_type} バージョン更新",
            "ビルド日: {new_build_date}"
        ]
    }},'''
    
    # VERSION_HISTORYの最初に新しいエントリを追加
    history_pattern = r'(VERSION_HISTORY = \[\s*)(\{)'
    content = re.sub(history_pattern, rf'\1{new_history_entry}\n    \2', content)
    
    # ファイルを更新
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ バージョンを {current_version} → {new_version} に更新しました")
    return True

def get_commit_message():
    """コミットメッセージからバージョンタイプを判定"""
    try:
        # 最新のコミットメッセージを取得
        result = subprocess.run(['git', 'log', '-1', '--pretty=%B'], 
                              capture_output=True, text=True, check=True)
        commit_msg = result.stdout.strip().lower()
        
        # コミットメッセージからバージョンタイプを判定
        if any(keyword in commit_msg for keyword in ['feat:', '新機能', '機能追加']):
            return "minor"
        elif any(keyword in commit_msg for keyword in ['fix:', '修正', 'バグ修正']):
            return "patch"
        elif any(keyword in commit_msg for keyword in ['breaking', '破壊的変更']):
            return "major"
        else:
            return "patch"  # デフォルトはpatch
    except:
        return "patch"

def main():
    """メイン処理"""
    if len(sys.argv) > 1:
        version_type = sys.argv[1]
    else:
        version_type = get_commit_message()
    
    print(f"🔄 自動バージョンアップを開始します (タイプ: {version_type})")
    
    if update_version(version_type):
        print("✅ バージョンアップが完了しました")
        return 0
    else:
        print("❌ バージョンアップに失敗しました")
        return 1

if __name__ == "__main__":
    sys.exit(main())
