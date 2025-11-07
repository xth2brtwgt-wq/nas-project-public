#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
認証データベース管理ユーティリティ
ユーザー管理とセッション管理のためのSQLiteデータベース操作
"""

import sqlite3
import bcrypt
import uuid
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

def get_db_path():
    """データベースパスを取得（環境に応じて）"""
    nas_mode = os.getenv('NAS_MODE', '').lower()
    if nas_mode in ('true', '1', 'yes'):
        # コンテナ内では /nas-project-data としてマウントされている
        # docker-compose.yml: /home/AdminUser/nas-project-data:/nas-project-data:rw
        return Path('/nas-project-data/nas-dashboard/auth.db')
    else:
        # ローカル環境ではプロジェクトディレクトリに保存
        return Path(__file__).parent.parent / 'data' / 'auth.db'

def init_auth_db():
    """認証データベースを初期化"""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ユーザーテーブルを作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # セッションテーブルを作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # インデックスを作成
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)')
        
        conn.commit()
        logger.info(f"認証データベースを初期化しました: {db_path}")
    except Exception as e:
        logger.error(f"認証データベース初期化エラー: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def hash_password(password: str) -> str:
    """パスワードをハッシュ化"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """パスワードを検証"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception as e:
        logger.error(f"パスワード検証エラー: {e}")
        return False

def get_user_by_username(username: str) -> Optional[Dict]:
    """ユーザー名でユーザーを取得"""
    db_path = get_db_path()
    # データベースディレクトリが存在しない場合は作成
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # データベースファイルが存在しない場合は初期化
    if not db_path.exists():
        logger.warning(f"認証データベースが存在しません。初期化します: {db_path}")
        init_auth_db()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except Exception as e:
        logger.error(f"ユーザー取得エラー: {e}")
        return None
    finally:
        conn.close()

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """ユーザーIDでユーザーを取得"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except Exception as e:
        logger.error(f"ユーザー取得エラー: {e}")
        return None
    finally:
        conn.close()

def get_all_users() -> List[Dict]:
    """すべてのユーザーを取得"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"ユーザー一覧取得エラー: {e}")
        return []
    finally:
        conn.close()

def create_user(username: str, password: str) -> bool:
    """ユーザーを作成"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        ''', (username, password_hash))
        conn.commit()
        logger.info(f"ユーザーを作成しました: {username}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"ユーザー名が既に存在します: {username}")
        return False
    except Exception as e:
        logger.error(f"ユーザー作成エラー: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_user(user_id: int, username: Optional[str] = None, password: Optional[str] = None) -> bool:
    """ユーザーを更新"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if username:
            updates.append('username = ?')
            params.append(username)
        
        if password:
            password_hash = hash_password(password)
            updates.append('password_hash = ?')
            params.append(password_hash)
        
        if not updates:
            return False
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(user_id)
        
        query = f'UPDATE users SET {", ".join(updates)} WHERE id = ?'
        cursor.execute(query, params)
        conn.commit()
        logger.info(f"ユーザーを更新しました: {user_id}")
        return True
    except Exception as e:
        logger.error(f"ユーザー更新エラー: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def deactivate_user(user_id: int) -> bool:
    """ユーザーを無効化"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
        conn.commit()
        logger.info(f"ユーザーを無効化しました: {user_id}")
        return True
    except Exception as e:
        logger.error(f"ユーザー無効化エラー: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_session(user_id: int, expires_at: datetime) -> Optional[str]:
    """セッションを作成"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        session_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO sessions (session_id, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (session_id, user_id, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        logger.info(f"セッションを作成しました: {session_id} (user_id: {user_id})")
        return session_id
    except Exception as e:
        logger.error(f"セッション作成エラー: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def verify_session(session_id: str) -> Optional[int]:
    """セッションを検証してユーザーIDを返す"""
    if not session_id:
        return None
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT user_id FROM sessions
            WHERE session_id = ? AND expires_at > ?
        ''', (session_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"セッション検証エラー: {e}")
        return None
    finally:
        conn.close()

def delete_session(session_id: str) -> bool:
    """セッションを削除"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        conn.commit()
        logger.info(f"セッションを削除しました: {session_id}")
        return True
    except Exception as e:
        logger.error(f"セッション削除エラー: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def cleanup_expired_sessions():
    """期限切れのセッションを削除"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM sessions WHERE expires_at < ?', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
        deleted_count = cursor.rowcount
        conn.commit()
        if deleted_count > 0:
            logger.info(f"期限切れセッションを削除しました: {deleted_count}件")
        return deleted_count
    except Exception as e:
        logger.error(f"セッションクリーンアップエラー: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()

