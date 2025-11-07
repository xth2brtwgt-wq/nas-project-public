#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共通認証モジュール
各サービスで共有する認証機能を提供
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# 認証データベースのパスを取得
def get_auth_db_path() -> Path:
    """認証データベースのパスを取得"""
    if os.getenv('NAS_MODE'):
        # コンテナ内では /nas-project-data としてマウントされている
        # docker-compose.yml: /home/AdminUser/nas-project-data:/nas-project-data:rw
        return Path('/nas-project-data/nas-dashboard/auth.db')
    else:
        # ローカル環境ではプロジェクトディレクトリに保存
        # nas-dashboardディレクトリを基準にパスを解決
        project_root = Path(__file__).parent.parent.parent
        return project_root / 'nas-dashboard' / 'data' / 'auth.db'

def verify_session_from_cookie(session_id: str) -> Optional[int]:
    """セッションIDからユーザーIDを取得（共通関数）"""
    if not session_id:
        return None
    
    try:
        # データベースパスを取得
        db_path = get_auth_db_path()
        
        if not db_path.exists():
            logger.warning(f"認証データベースが見つかりません: {db_path}")
            return None
        
        import sqlite3
        from datetime import datetime
        
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
    except Exception as e:
        logger.error(f"セッション検証エラー: {e}")
        return None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """ユーザーIDからユーザー情報を取得（共通関数）"""
    if not user_id:
        return None
    
    try:
        # データベースパスを取得
        db_path = get_auth_db_path()
        
        if not db_path.exists():
            logger.warning(f"認証データベースが見つかりません: {db_path}")
            return None
        
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = 1', (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"ユーザー取得エラー: {e}")
            return None
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"ユーザー取得エラー: {e}")
        return None

def get_current_user_from_request(request) -> Optional[Dict]:
    """リクエストから現在のユーザーを取得（共通関数）"""
    try:
        # セッションIDをCookieから取得
        session_id = None
        
        # Flaskの場合
        if hasattr(request, 'cookies'):
            session_id = request.cookies.get('session_id')
        # FastAPIの場合
        elif hasattr(request, 'cookies'):
            session_id = request.cookies.get('session_id')
        # その他の場合（直接Cookieを取得）
        elif hasattr(request, 'headers'):
            cookie_header = request.headers.get('Cookie', '')
            if cookie_header:
                for cookie in cookie_header.split(';'):
                    cookie = cookie.strip()
                    if cookie.startswith('session_id='):
                        session_id = cookie.split('=', 1)[1]
                        break
        
        if not session_id:
            logger.debug("[AUTH] セッションIDがありません")
            return None
        
        # セッションを検証
        user_id = verify_session_from_cookie(session_id)
        if not user_id:
            logger.debug(f"[AUTH] セッション検証失敗: {session_id[:20]}...")
            return None
        
        # ユーザー情報を取得
        user = get_user_by_id(user_id)
        if user:
            logger.debug(f"[AUTH] ユーザー認証成功: {user.get('username', 'unknown')} (user_id: {user_id})")
        return user
    except Exception as e:
        logger.error(f"[AUTH] get_current_user_from_requestエラー: {e}", exc_info=True)
        return None

def get_dashboard_login_url(request=None) -> str:
    """
    ダッシュボードのログインページURLを取得
    
    注意: すべてのアクセスを外部URL（Nginx Proxy Manager経由）にリダイレクトします。
    ローカルアクセス（内部ネットワークから直接アクセス）は想定していません。
    
    Args:
        request: リクエストオブジェクト（FlaskまたはFastAPI）
                元のページURLを含めるために使用される
    
    Returns:
        ダッシュボードのログインページURL（外部URL、元のページ情報を含む）
    """
    # 環境変数で外部URLが設定されている場合はそれを使用
    external_url = os.getenv('NAS_EXTERNAL_ACCESS_URL', 'https://yoshi-nas-sys.duckdns.org:8443')
    
    # 元のページURLを取得（リダイレクト後に戻るため）
    original_path = None
    if request:
        # まず、現在のリクエストURLを確認
        current_path = None
        if hasattr(request, 'url'):
            # FlaskまたはFastAPIの場合
            try:
                from urllib.parse import urlparse
                parsed = urlparse(str(request.url))
                current_path = parsed.path
            except:
                pass
        
        # Refererヘッダーから元のページURLを取得（優先）
        referer = None
        if hasattr(request, 'headers'):
            referer = request.headers.get('Referer', '') or request.headers.get('referer', '')
        elif hasattr(request, 'referrer'):
            referer = request.referrer
        
        if referer:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(referer)
                # /login以外のパスを取得
                if parsed.path and parsed.path != '/login' and parsed.path != '/':
                    original_path = parsed.path
                    logger.info(f"[AUTH] Refererから元のページを取得: {original_path}")
            except Exception as e:
                logger.warning(f"[AUTH] Referer解析エラー: {e}")
        
        # Refererがない場合、現在のパスを使用（ただし/login以外）
        if not original_path and current_path and current_path != '/login' and current_path != '/':
            original_path = current_path
            logger.info(f"[AUTH] 現在のパスから元のページを取得: {original_path}")
    
    # 元のページパスがある場合は、nextパラメータとして追加
    if original_path:
        from urllib.parse import quote
        encoded_path = quote(original_path, safe='/')
        login_url = f'{external_url}/login?next={encoded_path}'
        logger.info(f"[AUTH] nextパラメータを追加: {login_url}")
    else:
        login_url = f'{external_url}/login'
    
    logger.info(f"[AUTH] ログインURL: {login_url}")
    return login_url

