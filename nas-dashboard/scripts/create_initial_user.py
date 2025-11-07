#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初期ユーザー作成スクリプト
認証データベースを初期化し、初期ユーザーを作成
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth_db import init_auth_db, create_user, get_all_users

def main():
    """初期ユーザーを作成"""
    print("認証データベースを初期化しています...")
    
    # データベースを初期化
    try:
        init_auth_db()
        print("✅ 認証データベースを初期化しました")
    except Exception as e:
        print(f"❌ 認証データベース初期化エラー: {e}")
        return 1
    
    # 既存のユーザーを確認
    existing_users = get_all_users()
    if existing_users:
        print(f"\n既存のユーザーが {len(existing_users)} 人存在します:")
        for user in existing_users:
            status = "有効" if user['is_active'] else "無効"
            print(f"  - {user['username']} (ID: {user['id']}, 状態: {status})")
        print("\n初期ユーザーを作成しますか？ (y/n): ", end="")
        choice = input().strip().lower()
        if choice != 'y':
            print("初期ユーザーの作成をスキップしました")
            return 0
    
    # 環境変数から初期ユーザー情報を取得
    username = os.getenv('DASHBOARD_USERNAME', 'admin')
    password = os.getenv('DASHBOARD_PASSWORD')
    
    if not password:
        print("\n初期ユーザー情報を入力してください")
        username = input("ユーザー名 (デフォルト: admin): ").strip() or 'admin'
        password = input("パスワード: ").strip()
        
        if not password:
            print("❌ パスワードが入力されていません")
            return 1
    
    # 初期ユーザーを作成
    print(f"\n初期ユーザーを作成しています...")
    print(f"  ユーザー名: {username}")
    
    if create_user(username, password):
        print(f"✅ 初期ユーザー「{username}」を作成しました")
        return 0
    else:
        print(f"❌ 初期ユーザーの作成に失敗しました（ユーザー名が既に存在する可能性があります）")
        return 1

if __name__ == '__main__':
    sys.exit(main())

