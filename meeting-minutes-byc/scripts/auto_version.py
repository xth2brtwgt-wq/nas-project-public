#!/usr/bin/env python3
"""
自動バージョン管理スクリプト

Gitコミット時に自動的にバージョンをインクリメントし、
変更履歴を記録します。
"""

import re
import sys
from datetime import datetime
from pathlib import Path


def read_version_file(version_file):
    """version.pyファイルを読み込む"""
    with open(version_file, 'r', encoding='utf-8') as f:
        return f.read()


def parse_current_version(content):
    """現在のバージョンを解析"""
    match = re.search(r'__version__\s*=\s*["\'](\d+)\.(\d+)\.(\d+)["\']', content)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return None


def get_commit_messages():
    """最新のコミットメッセージを取得"""
    import subprocess
    try:
        # 最後のバージョンアップ以降のコミットメッセージを取得
        result = subprocess.run(
            ['git', 'log', '--pretty=format:%s', '-n', '10'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            messages = result.stdout.strip().split('\n')
            # バージョン更新のコミットは除外
            return [msg for msg in messages if not msg.startswith('Version bump to') 
                    and not msg.startswith('自動バージョンアップ')]
        return []
    except Exception as e:
        print(f"⚠️  Gitログの取得に失敗: {e}")
        return []


def detect_version_bump_type(commit_messages):
    """コミットメッセージから適切なバージョンアップタイプを判定"""
    # キーワードによる判定
    major_keywords = ['breaking', 'major', 'メジャー', '破壊的変更']
    minor_keywords = ['feature', 'feat', 'add', 'minor', 'マイナー', '新機能', '機能追加']
    
    messages_lower = ' '.join(commit_messages).lower()
    
    for keyword in major_keywords:
        if keyword in messages_lower:
            return 'major'
    
    for keyword in minor_keywords:
        if keyword in messages_lower:
            return 'minor'
    
    # デフォルトはpatch
    return 'patch'


def increment_version(major, minor, patch, bump_type='patch'):
    """バージョンをインクリメント"""
    if bump_type == 'major':
        return major + 1, 0, 0
    elif bump_type == 'minor':
        return major, minor + 1, 0
    else:  # patch
        return major, minor, patch + 1


def extract_changes_from_commits(commit_messages):
    """コミットメッセージから変更内容を抽出"""
    changes = []
    
    # パターンマッチングで変更内容を分類
    for msg in commit_messages[:5]:  # 最新5件まで
        msg = msg.strip()
        if not msg or msg.startswith('Merge'):
            continue
            
        # プレフィックスを除去
        cleaned_msg = re.sub(r'^(fix|feat|add|update|remove|refactor|docs|style|test|chore):\s*', '', msg, flags=re.IGNORECASE)
        
        if cleaned_msg:
            changes.append(cleaned_msg)
    
    # デフォルトメッセージ
    if not changes:
        changes = ['システムの改善と最適化']
    
    return changes


def update_version_file(version_file, major, minor, patch, changes):
    """version.pyファイルを更新"""
    content = read_version_file(version_file)
    today = datetime.now().strftime('%Y-%m-%d')
    new_version = f"{major}.{minor}.{patch}"
    
    # __version__ を更新
    content = re.sub(
        r'__version__\s*=\s*["\'][^"\']+["\']',
        f'__version__ = "{new_version}"',
        content
    )
    
    # __version_info__ を更新
    content = re.sub(
        r'__version_info__\s*=\s*\([^)]+\)',
        f'__version_info__ = ({major}, {minor}, {patch})',
        content
    )
    
    # __build_date__ を更新
    content = re.sub(
        r'__build_date__\s*=\s*["\'][^"\']+["\']',
        f'__build_date__ = "{today}"',
        content
    )
    
    # VERSION_HISTORY に新しいエントリを追加
    changes_str = ',\n                '.join([f'"{change}"' for change in changes])
    new_history_entry = f'''    {{
        "version": "{new_version}",
        "date": "{today}",
        "changes": [
                {changes_str}
        ]
    }},'''
    
    # VERSION_HISTORY の最初のエントリとして挿入
    content = re.sub(
        r'(VERSION_HISTORY\s*=\s*\[)',
        f'\\1\n{new_history_entry}',
        content
    )
    
    # ファイルに書き込み
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return new_version


def main():
    """メイン処理"""
    # 引数からバージョンアップタイプを取得（指定されていればそれを使用）
    bump_type = sys.argv[1] if len(sys.argv) > 1 else None
    
    # version.pyのパスを取得
    script_dir = Path(__file__).parent
    version_file = script_dir.parent / 'version.py'
    
    if not version_file.exists():
        print(f"❌ version.pyが見つかりません: {version_file}")
        sys.exit(1)
    
    # 現在のバージョンを取得
    content = read_version_file(version_file)
    current_version = parse_current_version(content)
    
    if not current_version:
        print("❌ 現在のバージョンを解析できませんでした")
        sys.exit(1)
    
    major, minor, patch = current_version
    print(f"📌 現在のバージョン: {major}.{minor}.{patch}")
    
    # コミットメッセージを取得
    commit_messages = get_commit_messages()
    
    # バージョンアップタイプを判定（指定がなければ自動判定）
    if not bump_type or bump_type not in ['major', 'minor', 'patch']:
        bump_type = detect_version_bump_type(commit_messages)
    
    print(f"🔄 バージョンアップタイプ: {bump_type}")
    
    # 変更内容を抽出
    changes = extract_changes_from_commits(commit_messages)
    
    # バージョンをインクリメント
    new_major, new_minor, new_patch = increment_version(major, minor, patch, bump_type)
    
    # version.pyを更新
    new_version = update_version_file(version_file, new_major, new_minor, new_patch, changes)
    
    print(f"✅ バージョンを更新しました: {major}.{minor}.{patch} → {new_version}")
    print(f"📝 変更内容:")
    for change in changes:
        print(f"   - {change}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

