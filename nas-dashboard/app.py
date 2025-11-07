#!/usr/bin/env python3
"""
NAS統合管理ダッシュボード
複数のWebアプリケーションとシステム監視を統合管理
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file, send_from_directory, make_response
import subprocess
import json
import os
import psutil
import requests
from datetime import datetime, timedelta
import logging
from pathlib import Path
import shutil
import zipfile
import tempfile
import re
from typing import Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from version import get_version, get_version_string, get_full_version_info
from utils.email_sender import EmailSender
from utils.ai_analyzer import AIAnalyzer
from utils.auth_db import (
    init_auth_db, get_user_by_username, get_user_by_id, get_all_users,
    create_user, update_user, deactivate_user,
    create_session, verify_session, delete_session, cleanup_expired_sessions,
    verify_password
)
from functools import wraps


# ログ設定
# NAS環境では統合データディレクトリを使用、ローカル環境では./logsを使用
# docker-compose.ymlで /home/AdminUser/nas-project-data/nas-dashboard/logs:/app/logs にマウントされている
if os.getenv('NAS_MODE'):
    log_dir = os.getenv('LOG_DIR', '/app/logs')
else:
    log_dir = os.getenv('LOG_DIR', './logs')
os.makedirs(log_dir, exist_ok=True)

# ファイルハンドラーを追加
log_file = os.path.join(log_dir, 'app.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        logging.StreamHandler()  # 標準出力も維持
    ]
)
logger = logging.getLogger(__name__)

# Gemini AI設定
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
else:
    model = None

def get_ip_location(ip):
    """IPアドレスの地理的位置情報を取得"""
    try:
        # プライベートIPアドレスの場合は「ローカル」を返す
        if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
            return "ローカル"
        
        # 外部APIを使用して地理的位置情報を取得（タイムアウトを短縮）
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                country = data.get('country', 'Unknown')
                region = data.get('regionName', '')
                city = data.get('city', '')
                
                location_parts = [part for part in [city, region, country] if part]
                return ', '.join(location_parts) if location_parts else 'Unknown'
        
        return "Unknown"
    except Exception as e:
        logger.warning(f"IP位置情報取得エラー ({ip}): {e}")
        return "Unknown"

def get_monthly_ban_history():
    """過去30日間のBAN履歴を取得（月次レポート用）"""
    try:
        if os.getenv('NAS_MODE'):
            logger.info("月次レポート用BAN履歴を取得中")
            ban_history = []
            
            # 過去30日間の日付を計算
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            thirty_days_ago_str = thirty_days_ago.strftime('%Y-%m-%d')
            
            logger.info(f"過去30日間のBAN履歴を取得中 (from: {thirty_days_ago_str})")
            
            try:
                # Dockerログから全履歴を取得
                result = subprocess.run([
                    'docker', 'logs', 'fail2ban'
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # BAN実行ログを解析
                    for line in result.stdout.split('\n'):
                        if 'Ban ' in line and 'NOTICE' in line:
                            try:
                                # タイムスタンプを抽出
                                timestamp_part = line.split(' fail2ban.actions')[0]
                                timestamp_str = timestamp_part.split(' ')[0] + ' ' + timestamp_part.split(' ')[1].split(',')[0]
                                
                                # 日付を解析して30日間フィルタを適用
                                log_date_str = timestamp_part.split(' ')[0]
                                log_date = datetime.strptime(log_date_str, '%Y-%m-%d')
                                
                                # 過去30日間のログのみを処理
                                if log_date >= thirty_days_ago:
                                    # Jail名を抽出
                                    jail_start = line.find('[') + 1
                                    jail_end = line.find(']', jail_start)
                                    jail = line[jail_start:jail_end]
                                    
                                    # IPアドレスを抽出
                                    ip_start = line.find('Ban ') + 4
                                    ip = line[ip_start:].strip()
                                    
                                    logger.info(f"月次BAN履歴追加: IP={ip}, Jail={jail}, Time={timestamp_str}")
                                    ban_history.append({
                                        'timestamp': timestamp_str,
                                        'ip': ip,
                                        'jail': jail,
                                        'action': 'Ban'
                                    })
                                else:
                                    logger.debug(f"30日間範囲外のログをスキップ: {log_date_str}")
                            except Exception as parse_error:
                                logger.warning(f"BANログ解析エラー: {parse_error}, Line: {line}")
                                continue
                    
                    # タイムスタンプでソート（新しい順）
                    ban_history.sort(key=lambda x: x['timestamp'], reverse=True)
                    logger.info(f"月次BAN履歴取得完了: {len(ban_history)}件")
                    
                else:
                    logger.error(f"Dockerログ取得エラー: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Dockerログ取得エラー: {e}")
                
            return ban_history
        else:
            # ローカル環境ではモックデータを返す
            return [
                {
                    'timestamp': '2025-10-20 10:30:00',
                    'ip': '192.168.1.100',
                    'jail': 'sshd',
                    'action': 'Ban'
                },
                {
                    'timestamp': '2025-10-18 15:45:00',
                    'ip': '10.0.0.50',
                    'jail': 'nginx-http-auth',
                    'action': 'Ban'
                }
            ]
    except Exception as e:
        logger.error(f"月次BAN履歴取得エラー: {e}")
        return []

def get_ban_history_simple():
    """BAN履歴を取得（位置情報なし）"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境ではFail2banログから過去7日間のBAN履歴を取得
            ban_history = []
            
            logger.info("BAN履歴をログから取得中")
            
            try:
                # 過去7日間の日付を計算
                from datetime import datetime, timedelta
                seven_days_ago = datetime.now() - timedelta(days=7)
                seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d')
                
                logger.info(f"過去7日間のBAN履歴を取得中 (from: {seven_days_ago_str})")
                
                # Fail2banログから全履歴を取得（--sinceが動作しないため）
                result = subprocess.run([
                    'docker', 'logs', 'fail2ban'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    # BAN実行ログを解析
                    for line in result.stdout.split('\n'):
                        if 'Ban ' in line and 'NOTICE' in line:
                            # 例: 2025-10-24 15:21:50,993 fail2ban.actions [1]: NOTICE [sshd] Ban 183.66.17.82
                            try:
                                # タイムスタンプを抽出
                                timestamp_part = line.split(' fail2ban.actions')[0]
                                timestamp_str = timestamp_part.split(' ')[0] + ' ' + timestamp_part.split(' ')[1].split(',')[0]
                                
                                # 日付を解析して7日間フィルタを適用
                                log_date_str = timestamp_part.split(' ')[0]
                                log_date = datetime.strptime(log_date_str, '%Y-%m-%d')
                                
                                # 過去7日間のログのみを処理
                                if log_date >= seven_days_ago:
                                    # Jail名を抽出
                                    jail_start = line.find('[') + 1
                                    jail_end = line.find(']', jail_start)
                                    jail = line[jail_start:jail_end]
                                    
                                    # IPアドレスを抽出
                                    ip_start = line.find('Ban ') + 4
                                    ip = line[ip_start:].strip()
                                    
                                    logger.info(f"BAN履歴追加: IP={ip}, Jail={jail}, Time={timestamp_str}")
                                    ban_history.append({
                                        'timestamp': timestamp_str,
                                        'ip': ip,
                                        'jail': jail,
                                        'action': 'Ban'
                                    })
                                else:
                                    logger.debug(f"7日間範囲外のログをスキップ: {log_date_str}")
                            except Exception as parse_error:
                                logger.warning(f"BANログ解析エラー: {parse_error}, Line: {line}")
                                continue
                
                # 過去7日間のUNBAN実行も取得
                for line in result.stdout.split('\n'):
                    if 'Unban ' in line and 'NOTICE' in line:
                        # 例: 2025-10-24 16:12:50,302 fail2ban.actions [1]: NOTICE [sshd] Unban 196.251.70.164
                        try:
                            # タイムスタンプを抽出
                            timestamp_part = line.split(' fail2ban.actions')[0]
                            timestamp_str = timestamp_part.split(' ')[0] + ' ' + timestamp_part.split(' ')[1].split(',')[0]
                            
                            # 日付を解析して7日間フィルタを適用
                            log_date_str = timestamp_part.split(' ')[0]
                            log_date = datetime.strptime(log_date_str, '%Y-%m-%d')
                            
                            # 過去7日間のログのみを処理
                            if log_date >= seven_days_ago:
                                # Jail名を抽出
                                jail_start = line.find('[') + 1
                                jail_end = line.find(']', jail_start)
                                jail = line[jail_start:jail_end]
                                
                                # IPアドレスを抽出
                                ip_start = line.find('Unban ') + 6
                                ip = line[ip_start:].strip()
                                
                                logger.info(f"UNBAN履歴追加: IP={ip}, Jail={jail}, Time={timestamp_str}")
                                ban_history.append({
                                    'timestamp': timestamp_str,
                                    'ip': ip,
                                    'jail': jail,
                                    'action': 'Unban'
                                })
                            else:
                                logger.debug(f"7日間範囲外のUNBANログをスキップ: {log_date_str}")
                        except Exception as parse_error:
                            logger.warning(f"UNBANログ解析エラー: {parse_error}, Line: {line}")
                            continue
                
                # タイムスタンプでソート（新しい順）
                ban_history.sort(key=lambda x: x['timestamp'], reverse=True)
                
                logger.info(f"BAN履歴取得完了: {len(ban_history)}件")
                return ban_history
                
            except Exception as log_error:
                logger.error(f"Fail2banログ取得エラー: {log_error}")
                return []
        else:
            # ローカル環境ではモックデータを返す
            return [
                {
                    'timestamp': '2025-10-24 15:21:50',
                    'ip': '183.66.17.82',
                    'jail': 'sshd',
                    'action': 'Ban'
                },
                {
                    'timestamp': '2025-10-24 16:18:47',
                    'ip': '220.154.129.88',
                    'jail': 'sshd',
                    'action': 'Ban'
                },
                {
                    'timestamp': '2025-10-24 17:40:06',
                    'ip': '196.251.70.164',
                    'jail': 'sshd',
                    'action': 'Ban'
                }
            ]
    except Exception as e:
        logger.error(f"BAN履歴取得エラー: {e}")
        return []

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'nas-dashboard-secret-key-2025')

# 認証データベースを初期化
try:
    init_auth_db()
    logger.info("認証データベースを初期化しました")
except Exception as e:
    logger.error(f"認証データベース初期化エラー: {e}")

# 期限切れセッションのクリーンアップ（起動時）
try:
    cleanup_expired_sessions()
except Exception as e:
    logger.warning(f"セッションクリーンアップエラー: {e}")

# Safariや一部ブラウザ向けに /favicon.ico を返す
@app.route('/favicon.ico')
def favicon():
    """Favicon endpoint - SVGを返す（Safari対応強化）"""
    try:
        # 絶対パスでfavicon.svgを返す
        favicon_path = os.path.join(os.path.dirname(__file__), 'static', 'favicon.svg')
        if os.path.exists(favicon_path):
            # Safariはネットワーク経由時にContent-Typeが重要
            response = send_file(favicon_path, mimetype='image/svg+xml')
            # Content-Typeを明示的に設定（Safari対応）
            response.headers['Content-Type'] = 'image/svg+xml; charset=utf-8'
            # キャッシュヘッダーを設定
            response.headers['Cache-Control'] = 'public, max-age=86400'
            response.headers['Last-Modified'] = datetime.fromtimestamp(os.path.getmtime(favicon_path)).strftime('%a, %d %b %Y %H:%M:%S GMT')
            # Safari用にContent-Dispositionも設定
            response.headers['Content-Disposition'] = 'inline; filename="favicon.svg"'
            return response
        else:
            logger.warning(f"Faviconファイルが見つかりません: {favicon_path}")
            return ('', 204)
    except Exception as e:
        logger.warning(f"Favicon読み込みエラー: {e}")
        # 空の204レスポンスを返す
        return ('', 204)

# 設定
class Config:
    # サービス設定
    SERVICES = {
                'meeting_minutes': {
                    'name': '議事録生成システム',
                    'url': 'http://192.168.68.110:5002' if os.getenv('NAS_MODE') else 'http://localhost:5002',
                    'description': '音声ファイルから自動で議事録を生成',
                    'icon': 'fas fa-microphone-alt',
                    'color': 'primary',
                    'category': 'ai_automation'
                },
        'document_automation': {
            'name': 'ドキュメント自動処理',
            'url': 'http://192.168.68.110:8080' if os.getenv('NAS_MODE') else 'http://localhost:8080',
            'description': 'PDF・画像からOCR、AI要約、自動分類',
            'icon': 'fas fa-file-alt',
            'color': 'success',
            'category': 'ai_automation'
        },
        'youtube_to_notion': {
            'name': 'YouTube-to-Notion自動投稿',
            'url': 'http://192.168.68.110:8111' if os.getenv('NAS_MODE') else 'http://localhost:8111',
            'description': 'YouTube動画の自動要約とNotion投稿、コメント分析',
            'icon': 'fab fa-youtube',
            'color': 'danger',
            'category': 'ai_automation'
        },
        'amazon_analytics': {
            'name': 'Amazon購入分析',
            'url': 'http://192.168.68.110:8001' if os.getenv('NAS_MODE') else 'http://localhost:8001',
            'description': 'Amazon購入履歴の分析と可視化、AI活用',
            'icon': 'fas fa-shopping-cart',
            'color': 'warning',
            'category': 'data_analysis'
        },
        'nas_monitoring': {
            'name': 'NAS監視システム',
            'url': 'http://192.168.68.110:3002' if os.getenv('NAS_MODE') else 'http://localhost:3002',
            'description': 'AI/機械学習ベースの異常検知機能付きNAS統合管理システム',
            'icon': 'fas fa-chart-line',
            'color': 'info',
            'category': 'data_analysis',
            'external': True
        },
        'insta360_sync': {
            'name': 'Insta360自動同期',
            'url': '#',  # WebUIがないため、ダッシュボード内で制御
            'description': 'Insta360ファイルの自動同期とログ確認（ダッシュボード内で制御）',
            'icon': 'fas fa-camera',
            'color': 'info',
            'category': 'security_monitoring',
            'external': False
        },
        # 'fail2ban': Fail2Ban機能はNAS監視システムのセキュリティタブで確認できます
        # NAS監視システムボタンからアクセスしてください
        'log_monitoring': {
            'name': 'ログ監視',
            'url': '/logs',  # ログ監視画面へのリンク
            'description': '全プロジェクトのログファイルをリアルタイム監視',
            'icon': 'fas fa-file-alt',
            'color': 'primary',
            'category': 'security_monitoring',
            'external': False
        }
    }
    
    # サービスカテゴリ設定
    SERVICE_CATEGORIES = {
        'ai_automation': {
            'name': 'AI・自動化系',
            'icon': 'fas fa-robot',
            'color': 'primary',
            'description': 'AI技術を活用した自動化システム'
        },
        'data_analysis': {
            'name': 'データ分析系',
            'icon': 'fas fa-chart-bar',
            'color': 'info',
            'description': 'データ分析と可視化システム'
        },
        'security_monitoring': {
            'name': 'セキュリティ・監視系',
            'icon': 'fas fa-shield-alt',
            'color': 'warning',
            'description': 'セキュリティ監視とシステム管理'
        }
    }
    
    # システム監視設定
    SYSTEM_MONITORING = {
        'disk_threshold': 80,  # ディスク使用率の警告閾値（%）
        'memory_threshold': 85,  # メモリ使用率の警告閾値（%）
        'cpu_threshold': 90   # CPU使用率の警告閾値（%）
    }

def get_base_url() -> str:
    """リクエストのホスト名からベースURLを生成"""
    # 環境変数でEXTERNAL_HOSTが設定されている場合はそれを使用
    external_host = os.getenv('EXTERNAL_HOST')
    if external_host:
        # ポート番号を含む場合はそのまま使用、含まない場合はリクエストのポートを使用
        if ':' in external_host:
            base_url = f"http://{external_host}"
        else:
            port = request.environ.get('SERVER_PORT', '9001')
            base_url = f"http://{external_host}:{port}"
        logger.info(f"[URL] get_base_url() from EXTERNAL_HOST = {base_url}")
        return base_url
    
    # X-Forwarded-Hostヘッダーを確認（Nginx Proxy Manager経由の場合）
    forwarded_host = request.headers.get('X-Forwarded-Host')
    if forwarded_host:
        # 外部アクセス（Nginx Proxy Manager経由）の場合は常にhttpsを使用
        # X-Forwarded-Protoが設定されていても、外部アクセスの場合はhttpsを強制
        forwarded_scheme = 'https'
        # X-Forwarded-Hostが設定されている場合はそれを使用（外部アクセス）
        # ポート番号が含まれていない場合は追加
        if ':' not in forwarded_host:
            # ポート番号を追加（8443はNginx Proxy Managerのデフォルトポート）
            forwarded_host = f"{forwarded_host}:8443"
        base_url = f"{forwarded_scheme}://{forwarded_host}"
        logger.info(f"[URL] get_base_url() from X-Forwarded-Host = {base_url}, X-Forwarded-Proto = {request.headers.get('X-Forwarded-Proto', 'N/A')}")
        return base_url
    
    # リクエストからホスト名とポートを取得
    host = request.host
    # 外部アクセス（yoshi-nas-sys.duckdns.org）の場合は常にhttpsを使用
    if 'yoshi-nas-sys.duckdns.org' in host or (hasattr(request, 'host') and '8443' in str(request.host)):
        scheme = 'https'
    else:
        scheme = request.scheme
    base_url = f"{scheme}://{host}"
    logger.info(f"[URL] get_base_url() from request = {base_url}, request.host = {request.host}, request.scheme = {request.scheme}")
    return base_url

def get_current_user():
    """現在のユーザーを取得（セッションから）"""
    try:
        session_id = request.cookies.get('session_id')
        if not session_id:
            logger.info(f"[AUTH] get_current_user: セッションIDがありません (path: {request.path})")
            return None
        
        logger.info(f"[AUTH] get_current_user: セッションIDを取得しました (path: {request.path}, session_id: {session_id[:20]}...)")
        user_id = verify_session(session_id)
        if not user_id:
            logger.info(f"[AUTH] get_current_user: セッション検証失敗 (path: {request.path}, session_id: {session_id[:20]}...)")
            return None
        
        user = get_user_by_id(user_id)
        if user:
            logger.info(f"[AUTH] get_current_user: ユーザー認証成功 (path: {request.path}, user: {user['username']}, user_id: {user_id})")
        else:
            logger.warning(f"[AUTH] get_current_user: ユーザー情報が取得できませんでした (user_id: {user_id})")
        return user
    except Exception as e:
        logger.error(f"[AUTH] get_current_userエラー: {e}", exc_info=True)
        return None

def is_admin_user(user: Optional[Dict] = None) -> bool:
    """ユーザーが管理者かどうかを判定"""
    if not user:
        user = get_current_user()
    
    if not user:
        logger.info("[ADMIN] ユーザーが取得できませんでした")
        return False
    
    username = user.get('username', 'Unknown')
    user_id = user.get('id')
    
    # 環境変数で管理者ユーザー名を指定（カンマ区切りで複数指定可能）
    admin_users_str = os.getenv('DASHBOARD_ADMIN_USERS', '').strip()
    logger.info(f"[ADMIN] DASHBOARD_ADMIN_USERS環境変数: '{admin_users_str}'")
    
    if admin_users_str:
        admin_users = [u.strip() for u in admin_users_str.split(',') if u.strip()]
        if admin_users:
            is_admin = username in admin_users
            logger.info(f"[ADMIN] ユーザー '{username}' (ID: {user_id}) の管理者チェック: {is_admin} (管理者リスト: {admin_users})")
            return is_admin
    
    # 環境変数が設定されていない場合は、最初のユーザー（ID=1）を管理者とする
    if user_id == 1:
        logger.info(f"[ADMIN] ユーザー '{username}' (ID: {user_id}) は最初のユーザー（ID=1）のため管理者として扱います")
        return True
    
    logger.info(f"[ADMIN] ユーザー '{username}' (ID: {user_id}) は管理者ではありません")
    return False

def require_auth(f):
    """認証が必要なエンドポイントのデコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            logger.info(f"[AUTH] require_auth: 認証チェック開始 (path: {request.path})")
            user = get_current_user()
            if not user:
                # 元のページURLをnextパラメータとして追加
                current_path = request.path
                login_url = url_for('login')
                if current_path and current_path != '/login' and current_path != '/':
                    from urllib.parse import quote
                    encoded_path = quote(current_path, safe='/')
                    login_url = f"{url_for('login')}?next={encoded_path}"
                    logger.info(f"[AUTH] require_auth: 元のパスをnextパラメータとして追加: {current_path} -> {login_url}")
                else:
                    logger.info(f"[AUTH] require_auth: 認証が必要です (path: {request.path}) -> /loginにリダイレクト")
                return redirect(login_url)
            logger.info(f"[AUTH] require_auth: 認証成功 (path: {request.path}, user: {user.get('username')})")
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"[AUTH] require_authエラー: {e}", exc_info=True)
            # エラー時も元のページURLをnextパラメータとして追加
            current_path = request.path
            login_url = url_for('login')
            if current_path and current_path != '/login' and current_path != '/':
                from urllib.parse import quote
                encoded_path = quote(current_path, safe='/')
                login_url = f"{url_for('login')}?next={encoded_path}"
            return redirect(login_url)
    return decorated_function

def get_dynamic_services():
    """リクエストのホスト名を使用して動的にサービスURLを生成"""
    base_url = get_base_url()
    logger.info(f"[URL] get_base_url() = {base_url}")
    # ホスト名とポートを抽出（例: "example.com:9001" または "192.168.68.110:9001"）
    url_without_scheme = base_url.replace('http://', '').replace('https://', '')
    if ':' in url_without_scheme:
        hostname, current_port = url_without_scheme.split(':', 1)
    else:
        hostname = url_without_scheme
        current_port = None
    
    logger.info(f"[URL] hostname = {hostname}, current_port = {current_port}")
    
    # 外部アクセス（Nginx Proxy Manager経由）かどうかを判定
    # 判定条件: ポートが8443（Nginx Proxy Managerのポート）または、ホスト名がyoshi-nas-sys.duckdns.org
    is_external_access = (
        current_port == '8443' or 
        hostname == 'yoshi-nas-sys.duckdns.org' or
        (current_port and current_port.startswith('844'))
    )
    logger.info(f"[URL] is_external_access = {is_external_access}")
    
    # スキーム（http/https）を決定
    # 外部アクセスの場合は常にhttpsを使用
    if is_external_access:
        scheme = 'https'
    else:
        # 内部アクセスの場合はbase_urlから抽出
        scheme = 'https' if base_url.startswith('https://') else 'http'
    logger.info(f"[URL] scheme = {scheme} (is_external_access = {is_external_access})")
    
    # Custom Locationパスマッピング（サービスID → Custom Locationパス）
    custom_location_mapping = {
        'meeting_minutes': '/meetings',
        'document_automation': '/documents',
        'youtube_to_notion': '/youtube',
        'amazon_analytics': '/analytics',
        'nas_monitoring': '/monitoring',
    }
    
    # ポートマッピング（サービスID → ポート番号）
    port_mapping = {
        'meeting_minutes': '5002',
        'document_automation': '8080',
        'youtube_to_notion': '8111',
        'amazon_analytics': '8001',
        'nas_monitoring': '3002',
    }
    
    # サービス設定をコピーしてURLを動的に生成
    dynamic_services = {}
    for service_id, service_config in Config.SERVICES.items():
        service_config_copy = service_config.copy()
        
        # URLが'#'や相対パスの場合はそのまま
        original_url = service_config.get('url', '')
        if original_url.startswith('#') or original_url.startswith('/'):
            dynamic_services[service_id] = service_config_copy
            continue
        
        # 外部アクセス（Nginx Proxy Manager経由）の場合はCustom Locationパスを使用
        if is_external_access and service_id in custom_location_mapping:
            custom_location_path = custom_location_mapping[service_id]
            # 外部アクセスの場合、ポート番号がない場合は8443をデフォルトで使用
            port = current_port if current_port else '8443'
            service_config_copy['url'] = f"{scheme}://{hostname}:{port}{custom_location_path}"
            logger.info(f"[URL] {service_id} -> {service_config_copy['url']} (external)")
        # ポートマッピングがある場合は動的に生成（内部アクセスの場合）
        elif service_id in port_mapping:
            port = port_mapping[service_id]
            # 現在のポートと同じ場合は相対パスを使用（異なるポートは通常使われないので、絶対URLを生成）
            service_config_copy['url'] = f"{scheme}://{hostname}:{port}"
            logger.info(f"[URL] {service_id} -> {service_config_copy['url']} (internal)")
        else:
            # その他のサービスは元の設定を維持
            dynamic_services[service_id] = service_config_copy
            logger.info(f"[URL] {service_id} -> {service_config_copy['url']} (unchanged)")
            continue
        
        dynamic_services[service_id] = service_config_copy
    
    return dynamic_services

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='ユーザー名とパスワードを入力してください')
        
        # ユーザーを検索
        user = get_user_by_username(username)
        
        # デバッグログを追加
        if user:
            logger.info(f"[AUTH] ユーザーが見つかりました: {username}, 状態: {'有効' if user['is_active'] else '無効'}")
            password_valid = verify_password(password, user['password_hash'])
            logger.info(f"[AUTH] パスワード検証結果: {password_valid}")
        else:
            logger.warning(f"[AUTH] ユーザーが見つかりません: {username}")
        
        if user and verify_password(password, user['password_hash']) and user['is_active']:
            # セッションIDを発行
            expires_at = datetime.now() + timedelta(minutes=30)
            session_id = create_session(user['id'], expires_at)
            
            if session_id:
                # リダイレクト先を決定（nextパラメータを優先）
                # POSTリクエストの場合はform dataから、GETリクエストの場合はquery stringから取得
                # デバッグ用: form dataとargsの内容を詳細にログ出力
                form_next = request.form.get('next')
                args_next = request.args.get('next')
                next_param = form_next or args_next
                logger.info(f"[AUTH] login: nextパラメータ (form): {form_next}, nextパラメータ (args): {args_next}, 最終: {next_param}")
                logger.info(f"[AUTH] login: request.form全体: {dict(request.form)}, request.args全体: {dict(request.args)}")
                
                if next_param:
                    # nextパラメータがある場合、URLデコードして使用
                    from urllib.parse import unquote
                    redirect_url = unquote(next_param)
                    logger.info(f"[AUTH] login: nextパラメータ (元の値): {next_param}")
                    logger.info(f"[AUTH] login: URLデコード後: {redirect_url}")
                    
                    # 相対パスのみ許可（セキュリティ対策）
                    if not redirect_url.startswith('/') or redirect_url.startswith('//'):
                        logger.warning(f"[AUTH] login: 不正なリダイレクトURL: {redirect_url}, ダッシュボードにリダイレクト")
                        redirect_url = url_for('dashboard')
                    else:
                        # リダイレクト先が正しく設定されているか確認
                        logger.info(f"[AUTH] login: リダイレクト先を設定: {redirect_url}")
                        # 外部URL（Nginx Proxy Manager経由）を使用する必要がある場合は、フルURLを生成
                        # 相対パスのままでも動作するが、外部URLの場合はフルURLを生成する方が確実
                        try:
                            base_url = get_base_url()
                            # 外部アクセス（Nginx Proxy Manager経由）の場合はフルURLを生成
                            if 'yoshi-nas-sys.duckdns.org' in base_url or ':8443' in base_url:
                                # スキームを取得（httpsを優先）
                                if base_url.startswith('https://'):
                                    scheme = 'https'
                                else:
                                    scheme = 'http'
                                # ホスト名とポートを抽出
                                url_without_scheme = base_url.replace('http://', '').replace('https://', '')
                                if ':' in url_without_scheme:
                                    hostname, port = url_without_scheme.split(':', 1)
                                else:
                                    hostname = url_without_scheme
                                    port = '8443'  # デフォルトポート
                                # フルURLを生成
                                full_redirect_url = f"{scheme}://{hostname}:{port}{redirect_url}"
                                logger.info(f"[AUTH] login: 外部URLに変換: {full_redirect_url}")
                                redirect_url = full_redirect_url
                            else:
                                # 内部アクセスの場合は相対パスのまま
                                logger.info(f"[AUTH] login: 内部アクセス、相対パスのまま使用: {redirect_url}")
                        except Exception as e:
                            logger.warning(f"[AUTH] login: フルURL生成エラー: {e}, 相対パスのまま使用: {redirect_url}")
                        
                        # リダイレクト先の確認
                        if redirect_url == '/documents' or redirect_url.endswith('/documents'):
                            logger.info(f"[AUTH] login: /documentsへのリダイレクトを確認: {redirect_url}")
                        elif redirect_url == '/' or redirect_url.endswith('/'):
                            logger.warning(f"[AUTH] login: リダイレクト先が'/'になっています。nextパラメータを再確認してください。")
                else:
                    # nextパラメータがない場合はダッシュボードにリダイレクト
                    redirect_url = url_for('dashboard')
                    logger.info(f"[AUTH] login: nextパラメータなし、ダッシュボードにリダイレクト")
                
                # CookieにセッションIDを保存
                # フルURLの場合はredirect()に直接渡す、相対パスの場合はurl_for()で生成
                if redirect_url.startswith('http://') or redirect_url.startswith('https://'):
                    response = redirect(redirect_url)
                else:
                    response = redirect(redirect_url)
                # 同一ドメインからのアクセスなので、samesite='Lax'を使用
                # secure=TrueはHTTPSの場合のみ有効（Nginx Proxy Manager経由でHTTPS使用）
                # domainを明示的に設定しない（デフォルトで現在のドメインが使用される）
                response.set_cookie(
                    'session_id',
                    session_id,
                    secure=True,
                    samesite='Lax',  # 同一ドメインからのアクセスなのでLaxに変更
                    httponly=True,
                    max_age=1800,  # 30分
                    path='/'  # すべてのパスでCookieを利用可能にする
                )
                logger.info(f"ユーザーがログインしました: {username} (user_id: {user['id']}), リダイレクト先: {redirect_url}")
                return response
            else:
                return render_template('login.html', error='セッションの作成に失敗しました')
        else:
            logger.warning(f"ログイン失敗: {username}")
            return render_template('login.html', error='ユーザー名またはパスワードが正しくありません')
    
    # 既にログインしている場合はダッシュボードにリダイレクト
    # ただし、Cookieが正しく読み取れない場合はログインページを表示
    user = get_current_user()
    if user:
        logger.info(f"[AUTH] 既にログイン済み: {user.get('username')} (ID: {user.get('id')})")
        return redirect(url_for('dashboard'))
    
    # nextパラメータをログに記録（デバッグ用）
    next_param = request.args.get('next')
    logger.info(f"[AUTH] ログインページ表示: request.url={request.url}, request.args={dict(request.args)}, nextパラメータ={next_param}")
    
    logger.info("[AUTH] 未ログイン状態: ログインページを表示")
    return render_template('login.html')

@app.route('/logout')
def logout():
    """ログアウト"""
    session_id = request.cookies.get('session_id')
    if session_id:
        delete_session(session_id)
        logger.info(f"ユーザーがログアウトしました: {session_id}")
    
    response = redirect(url_for('login'))
    response.set_cookie('session_id', '', expires=0)
    return response

@app.route('/')
@require_auth
def dashboard():
    """メインダッシュボード"""
    user = get_current_user()
    version_info = get_version()
    # 動的にサービスURLを生成
    logger.info("[DASHBOARD] dashboard() called")
    dynamic_services = get_dynamic_services()
    logger.info(f"[DASHBOARD] dynamic_services generated: {len(dynamic_services)} services")
    # 各サービスのURLを確認
    for service_id, service_config in dynamic_services.items():
        logger.info(f"[DASHBOARD] {service_id} URL: {service_config.get('url', 'N/A')}")
    # nas_monitoringのURLを確認
    if 'nas_monitoring' in dynamic_services:
        logger.info(f"[DASHBOARD] nas_monitoring URL: {dynamic_services['nas_monitoring'].get('url', 'N/A')}")
    # document_automationのURLを確認
    if 'document_automation' in dynamic_services:
        logger.info(f"[DASHBOARD] document_automation URL: {dynamic_services['document_automation'].get('url', 'N/A')}")
    # 管理者判定を実行
    logger.info(f"[DASHBOARD] 管理者判定を開始: user={user.get('username') if user else 'None'}, user_id={user.get('id') if user else 'None'}")
    is_admin = is_admin_user(user)
    logger.info(f"[DASHBOARD] 管理者判定結果: is_admin={is_admin}")
    return render_template('dashboard.html', 
                         services=dynamic_services, 
                         service_categories=Config.SERVICE_CATEGORIES,
                         version=version_info,
                         current_user=user,
                         is_admin=is_admin)

@app.route('/logs')
@require_auth
def log_viewer():
    """ログ監視専用画面"""
    user = get_current_user()
    is_admin = is_admin_user(user)
    version_info = get_version()
    return render_template('log_viewer.html', version=version_info, is_admin=is_admin)

@app.route('/calculator')
@require_auth
def calculator():
    """計算機ページ"""
    version_info = get_version()
    return render_template('calculator.html', version=version_info)




@app.route('/users')
@require_auth
def users_list():
    """ユーザー一覧"""
    users = get_all_users()
    current_user = get_current_user()
    is_admin = is_admin_user(current_user)
    return render_template('users.html', users=users, current_user=current_user, is_admin=is_admin)

@app.route('/users/add', methods=['GET', 'POST'])
@require_auth
def users_add():
    """ユーザー追加（管理者のみ）"""
    current_user = get_current_user()
    if not is_admin_user(current_user):
        logger.warning(f"[ADMIN] 管理者以外のユーザーがユーザー追加を試みました: {current_user.get('username') if current_user else 'Unknown'}")
        return redirect(url_for('users_list'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if not username or not password:
            return render_template('users_add.html', error='ユーザー名とパスワードを入力してください')
        
        if password != password_confirm:
            return render_template('users_add.html', error='パスワードが一致しません')
        
        if create_user(username, password):
            logger.info(f"ユーザーを追加しました: {username} (管理者: {current_user.get('username')})")
            return redirect(url_for('users_list'))
        else:
            return render_template('users_add.html', error='ユーザーの追加に失敗しました（ユーザー名が既に存在する可能性があります）')
    
    return render_template('users_add.html')

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@require_auth
def users_edit(user_id):
    """ユーザー編集"""
    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for('users_list'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if not username:
            return render_template('users_edit.html', user=user, error='ユーザー名を入力してください')
        
        # パスワードが入力されている場合は確認
        if password:
            if password != password_confirm:
                return render_template('users_edit.html', user=user, error='パスワードが一致しません')
        
        # ユーザーを更新
        if update_user(user_id, username=username, password=password if password else None):
            logger.info(f"ユーザーを更新しました: {user_id} (username: {username})")
            return redirect(url_for('users_list'))
        else:
            return render_template('users_edit.html', user=user, error='ユーザーの更新に失敗しました')
    
    return render_template('users_edit.html', user=user)

@app.route('/users/delete/<int:user_id>', methods=['POST'])
@require_auth
def users_delete(user_id):
    """ユーザー削除（無効化）"""
    current_user = get_current_user()
    
    # 自分自身を削除できないようにする
    if current_user['id'] == user_id:
        return redirect(url_for('users_list'))
    
    if deactivate_user(user_id):
        logger.info(f"ユーザーを無効化しました: {user_id}")
        return redirect(url_for('users_list'))
    else:
        return redirect(url_for('users_list'))

@app.route('/api/version')
def version_info():
    """バージョン情報を取得"""
    return jsonify(get_version())

@app.route('/api/proxy/anomalies')
def proxy_anomalies():
    """NAS監視システムの異常検知APIをプロキシ"""
    import requests
    try:
        # 外部IPアドレスを使用（Dockerネットワーク問題を回避）
        url = 'http://192.168.68.110:8002/api/v1/anomalies/'
        params = request.args
        response = requests.get(url, params=params, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proxy/metrics')
def proxy_metrics():
    """NAS監視システムのメトリクスAPIをプロキシ"""
    import requests
    try:
        # 外部IPアドレスを使用（Dockerネットワーク問題を回避）
        url = 'http://192.168.68.110:8002/api/v1/metrics/'
        response = requests.get(url, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# バックアップ関連のAPIエンドポイント
@app.route('/api/backup/create', methods=['POST'])
def create_backup():
    """バックアップを作成"""
    try:
        # バックアップディレクトリを設定
        if os.getenv('NAS_MODE'):
            backup_dir = Path('/app/backups')
            project_dir = Path('/nas-project')
        else:
            backup_dir = Path('/Users/Yoshi/nas-project/data/backups')
            project_dir = Path('/Users/Yoshi/nas-project')
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # バックアップファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"nas-project-backup-{timestamp}.zip"
        backup_path = backup_dir / backup_filename
        
        # プロジェクトディレクトリをZIP圧縮
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_dir):
                # 除外するディレクトリ
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
                
                for file in files:
                    # 除外するファイル
                    if file.endswith(('.pyc', '.pyo', '.log', '.tmp')):
                        continue
                    
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(project_dir)
                    zipf.write(file_path, arcname)
        
        # バックアップファイルのサイズを取得
        backup_size = backup_path.stat().st_size
        
        return jsonify({
            'success': True,
            'message': f'バックアップが作成されました: {backup_filename}',
            'filename': backup_filename,
            'size': backup_size,
            'path': str(backup_path)
        })
        
    except Exception as e:
        logger.error(f"バックアップ作成エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'バックアップの作成に失敗しました: {str(e)}'
        }), 500

@app.route('/api/backup/list')
def list_backups():
    """バックアップ一覧を取得"""
    try:
        # バックアップディレクトリを設定
        if os.getenv('NAS_MODE'):
            backup_dir = Path('/app/backups')
        else:
            backup_dir = Path('/Users/Yoshi/nas-project/data/backups')
        
        if not backup_dir.exists():
            return jsonify([])
        
        backups = []
        for backup_file in backup_dir.glob('*.zip'):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # 作成日時でソート（新しい順）
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify(backups)
        
    except Exception as e:
        logger.error(f"バックアップ一覧取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/download/<path:filename>')
def download_backup(filename):
    """バックアップファイルをダウンロード"""
    try:
        # バックアップディレクトリを設定
        if os.getenv('NAS_MODE'):
            backup_dir = Path('/app/backups')
        else:
            backup_dir = Path('/Users/Yoshi/nas-project/data/backups')
        
        backup_path = backup_dir / filename
        
        if not backup_path.exists():
            return jsonify({'error': 'バックアップファイルが見つかりません'}), 404
        
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"バックアップダウンロードエラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/delete/<path:filename>', methods=['DELETE'])
def delete_backup(filename):
    """バックアップファイルを削除"""
    try:
        # バックアップディレクトリを設定
        if os.getenv('NAS_MODE'):
            backup_dir = Path('/app/backups')
        else:
            backup_dir = Path('/Users/Yoshi/nas-project/data/backups')
        
        backup_path = backup_dir / filename
        
        if not backup_path.exists():
            return jsonify({'error': 'バックアップファイルが見つかりません'}), 404
        
        backup_path.unlink()
        
        return jsonify({
            'success': True,
            'message': f'バックアップ「{filename}」が削除されました'
        })
        
    except Exception as e:
        logger.error(f"バックアップ削除エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'バックアップの削除に失敗しました: {str(e)}'
        }), 500

@app.route('/api/system/status')
def system_status():
    """システム状態を取得"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # メモリ使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # ディスク使用率
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # ネットワーク統計
        network = psutil.net_io_counters()
        
        # システム情報
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        status = {
            'cpu': {
                'percent': cpu_percent,
                'status': 'warning' if cpu_percent > Config.SYSTEM_MONITORING['cpu_threshold'] else 'success'
            },
            'memory': {
                'percent': memory_percent,
                'used': memory.used,
                'total': memory.total,
                'status': 'warning' if memory_percent > Config.SYSTEM_MONITORING['memory_threshold'] else 'success'
            },
            'disk': {
                'percent': disk_percent,
                'used': disk.used,
                'total': disk.total,
                'status': 'warning' if disk_percent > Config.SYSTEM_MONITORING['disk_threshold'] else 'success'
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            },
            'uptime': {
                'days': uptime.days,
                'hours': uptime.seconds // 3600,
                'minutes': (uptime.seconds % 3600) // 60
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"システム状態取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/services/status')
def services_status():
    """各サービスの稼働状況を確認"""
    services_status = {}
    
    for service_id, service_config in Config.SERVICES.items():
        try:
            # Fail2Ban機能はNAS監視システムのセキュリティタブで確認できます
            # (fail2banサービスはConfig.SERVICESから削除済み)
            
            # その他のサービスはHTTPリクエストで確認
            if service_config['url'] != '#':
                try:
                    # Dockerコンテナ内からのアクセスのため、localhostを使用
                    if os.getenv('NAS_MODE'):
                        # NAS環境ではlocalhostでアクセス
                        if '192.168.68.110' in service_config['url']:
                            local_url = service_config['url'].replace('192.168.68.110', 'localhost')
                        else:
                            local_url = service_config['url']
                    else:
                        local_url = service_config['url']
                    
                    response = requests.get(f"{local_url}/", timeout=3)
                    services_status[service_id] = {
                        'name': service_config['name'],
                        'status': 'running' if response.status_code == 200 else 'error',
                        'url': service_config['url'],
                        'response_time': response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None
                    }
                except requests.exceptions.RequestException as e:
                    # HTTPリクエストが失敗した場合、Dockerコンテナの状態を確認
                    if os.getenv('NAS_MODE'):
                        try:
                            # Dockerコンテナの状態を確認
                            # サービスIDに応じて適切なコンテナ名を設定
                            if service_id == 'document_automation':
                                container_name = 'doc-automation-web'
                            elif service_id == 'meeting_minutes':
                                container_name = 'meeting-minutes-byc'
                            elif service_id == 'youtube_to_notion':
                                container_name = 'youtube-to-notion'
                            else:
                                container_name = service_id.replace('_', '-')
                            
                            result = subprocess.run([
                                'docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Status}}'
                            ], capture_output=True, text=True, timeout=5)
                            
                            if result.returncode == 0 and result.stdout.strip():
                                # コンテナが稼働している場合
                                services_status[service_id] = {
                                    'name': service_config['name'],
                                    'status': 'running',
                                    'url': service_config['url'],
                                    'response_time': None,
                                    'note': 'コンテナ稼働中（HTTP接続不可）'
                                }
                            else:
                                services_status[service_id] = {
                                    'name': service_config['name'],
                                    'status': 'stopped',
                                    'url': service_config['url'],
                                    'response_time': None
                                }
                        except subprocess.TimeoutExpired:
                            services_status[service_id] = {
                                'name': service_config['name'],
                                'status': 'unknown',
                                'url': service_config['url'],
                                'response_time': None
                            }
                    else:
                        services_status[service_id] = {
                            'name': service_config['name'],
                            'status': 'stopped',
                            'url': service_config['url'],
                            'response_time': None
                        }
            else:
                services_status[service_id] = {
                    'name': service_config['name'],
                    'status': 'unknown',
                    'url': service_config['url'],
                    'response_time': None
                }
        except requests.exceptions.RequestException:
            services_status[service_id] = {
                'name': service_config['name'],
                'status': 'stopped',
                'url': service_config['url'],
                'response_time': None
            }
        except Exception as e:
            logger.error(f"サービス {service_id} の状態確認エラー: {e}")
            services_status[service_id] = {
                'name': service_config['name'],
                'status': 'error',
                'url': service_config['url'],
                'response_time': None
            }
    
    return jsonify(services_status)

# Fail2Ban関連のAPIエンドポイントは監視システム（nas-dashboard-monitoring）に移動済み
# 詳細は http://192.168.68.110:8002 のセキュリティ監視タブを参照してください

@app.route('/api/backup/list')
def backup_list():
    """バックアップ一覧を取得"""
    try:
        # NAS環境かどうかでパスを切り替え
        if os.getenv('NAS_MODE'):
            backup_dir = Path('/app/backups')
        else:
            backup_dir = Path('/Users/Yoshi/nas-project/data/backups')
        
        if not backup_dir.exists():
            backup_dir.mkdir(parents=True, exist_ok=True)
        
        backups = []
        for backup_file in backup_dir.glob('backup_*.tar.gz'):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'path': str(backup_file)
            })
        
        # 作成日時でソート（新しい順）
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify(backups)
        
    except Exception as e:
        logger.error(f"バックアップ一覧取得エラー: {e}")
        return jsonify({'error': str(e)}), 500


def get_system_status_data():
    """システム状態データを取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のシステムデータを取得
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'timestamp': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            }
        else:
            # ローカル環境ではモックデータを返す
            return {
                'cpu_percent': 25.5,
                'memory_percent': 68.2,
                'memory_available_gb': 2.1,
                'disk_percent': 45.8,
                'disk_free_gb': 15.3,
                'timestamp': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            }
    except Exception as e:
        logger.error(f"システムデータ取得エラー: {e}")
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'memory_available_gb': 0,
            'disk_percent': 0,
            'disk_free_gb': 0,
            'timestamp': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'),
            'error': str(e)
        }

def get_fail2ban_status_data():
    """Fail2Ban状態データを取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のFail2Banデータを取得
            result = subprocess.run([
                'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status'
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                # アクティブなjailを取得
                jail_lines = [line for line in result.stdout.split('\n') if 'Jail list:' in line]
                if jail_lines:
                    jails = jail_lines[0].split('Jail list:')[1].strip().split(',')
                    jails = [jail.strip() for jail in jails if jail.strip()]
                else:
                    jails = []

                # 各jailの詳細情報を取得
                jail_details = {}
                total_banned = 0
                for jail in jails:
                    jail_result = subprocess.run([
                        'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status', jail
                    ], capture_output=True, text=True, timeout=5)

                    if jail_result.returncode == 0:
                        banned_count = 0
                        for line in jail_result.stdout.split('\n'):
                            if 'Currently banned:' in line:
                                banned_count = int(line.split('Currently banned:')[1].strip())
                                break

                        jail_details[jail] = {
                            'banned_count': banned_count,
                            'status': 'active'
                        }
                        total_banned += banned_count

                return {
                    'status': 'running',
                    'jails': jail_details,
                    'total_banned': total_banned,
                    'active_jails': len(jails)
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Fail2Banコンテナが起動していません',
                    'total_banned': 0,
                    'active_jails': 0
                }
        else:
            # ローカル環境ではモックデータを返す
            return {
                'status': 'mock',
                'jails': {
                    'sshd': {'banned_count': 3, 'status': 'active'},
                    'nginx-http-auth': {'banned_count': 1, 'status': 'active'}
                },
                'total_banned': 4,
                'active_jails': 2
            }
    except Exception as e:
        logger.error(f"Fail2Banデータ取得エラー: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'total_banned': 0,
            'active_jails': 0
        }

def get_docker_status_data():
    """Docker状態データを取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のDockerデータを取得
            result = subprocess.run([
                'docker', 'ps', '--format', 'json'
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        container_info = json.loads(line)
                        containers.append({
                            'name': container_info['Names'],
                            'image': container_info['Image'],
                            'status': container_info['Status']
                        })

                running_count = len([c for c in containers if 'Up' in c['status']])
                return {
                    'total_containers': len(containers),
                    'running_containers': running_count,
                    'stopped_containers': len(containers) - running_count,
                    'containers': containers
                }
            else:
                return {
                    'total_containers': 0,
                    'running_containers': 0,
                    'stopped_containers': 0,
                    'containers': [],
                    'error': 'Dockerコンテナ情報の取得に失敗しました'
                }
        else:
            # ローカル環境ではモックデータを返す
            return {
                'total_containers': 3,
                'running_containers': 3,
                'stopped_containers': 0,
                'containers': [
                    {'name': 'nas-dashboard', 'image': 'nas-dashboard:latest', 'status': 'Up 2 hours'},
                    {'name': 'meeting-minutes-byc', 'image': 'meeting-minutes-byc:latest', 'status': 'Up 1 day'},
                    {'name': 'doc-automation-web', 'image': 'document-automation-web:latest', 'status': 'Up 1 day'}
                ]
            }
    except Exception as e:
        logger.error(f"Dockerデータ取得エラー: {e}")
        return {
            'total_containers': 0,
            'running_containers': 0,
            'stopped_containers': 0,
            'containers': [],
            'error': str(e)
        }

def generate_report_content(system_data, fail2ban_data, docker_data, ban_history_data=None):
    """レポート内容を生成"""
    timestamp = system_data['timestamp']
    
    # システム状況の評価
    cpu_status = "正常" if system_data['cpu_percent'] < 80 else "注意" if system_data['cpu_percent'] < 95 else "危険"
    memory_status = "正常" if system_data['memory_percent'] < 80 else "注意" if system_data['memory_percent'] < 95 else "危険"
    disk_status = "正常" if system_data['disk_percent'] < 80 else "注意" if system_data['disk_percent'] < 95 else "危険"
    
    # 推奨事項の生成
    recommendations = []
    if system_data['cpu_percent'] > 80:
        recommendations.append("- CPU使用率が高いため、プロセスの確認を推奨")
    if system_data['memory_percent'] > 80:
        recommendations.append("- メモリ使用率が高いため、メモリの最適化を推奨")
    if system_data['disk_percent'] > 80:
        recommendations.append("- ディスク使用率が高いため、不要ファイルの削除を推奨")
    if fail2ban_data['total_banned'] > 10:
        recommendations.append("- 攻撃が多発しているため、セキュリティ設定の見直しを推奨")
    if docker_data['running_containers'] < docker_data['total_containers']:
        recommendations.append("- 停止中のコンテナがあるため、サービスの確認を推奨")
    
    if not recommendations:
        recommendations.append("- システムは正常に稼働しています")
        recommendations.append("- 定期的なバックアップの実行を推奨")
        recommendations.append("- セキュリティアップデートの適用を推奨")
    
    # Fail2Banの詳細情報
    fail2ban_details = ""
    if fail2ban_data['status'] == 'running' and 'jails' in fail2ban_data:
        fail2ban_details = "\n".join([
            f"- {jail}: {details['banned_count']}件" 
            for jail, details in fail2ban_data['jails'].items()
        ])
    elif fail2ban_data['status'] == 'error':
        fail2ban_details = f"- エラー: {fail2ban_data.get('message', '不明なエラー')}"
    else:
        fail2ban_details = "- データ取得不可"
    
    # BANされたIPの詳細情報を取得
    banned_ips_details = ""
    if ban_history_data:
        if ban_history_data:
            banned_ips_details = "\n".join([
                f"- {ban['ip']} | {ban['jail']} | {ban['timestamp']}"
                for ban in ban_history_data[:10]  # 最新10件
            ])
        else:
            banned_ips_details = "- BANされたIPなし"
    else:
        banned_ips_details = "- BANされたIP取得不可"
    
    # Dockerコンテナの詳細情報
    docker_details = ""
    if docker_data['containers']:
        docker_details = "\n".join([
            f"- {container['name']}: {container['status']}" 
            for container in docker_data['containers']
        ])
    else:
        docker_details = "- コンテナ情報取得不可"
    
    # 週番号を計算
    from datetime import datetime
    week_num = datetime.now().isocalendar()[1]
    year = datetime.now().year
    
    # BAN履歴の詳細情報を準備
    ban_activity = ""
    if ban_history_data:
        ban_activity = "\n".join([f"- {ban['ip']} | {ban['jail']} | {ban['timestamp']} | {ban['action']}" for ban in ban_history_data[:20]])
    else:
        ban_activity = "なし"
    
    # 攻撃元TOP5を準備
    attack_sources = ""
    if ban_history_data:
        # BAN実行のみを抽出
        ban_actions = [ban for ban in ban_history_data if ban['action'] == 'Ban']
        attack_sources = "\n".join([f"- {ban['ip']} ({ban['jail']})" for ban in ban_actions[:5]])
    else:
        attack_sources = "なし"
    
    # 推奨事項を準備
    recommendations_text = "\n".join(recommendations)
    
    # BANされたIPリストを準備
    banned_ip_list = ""
    if ban_history_data:
        # 現在BANされているIPのみを抽出
        current_banned = [ban for ban in ban_history_data if ban['action'] == 'Ban']
        banned_ip_list = " ".join([ban['ip'] for ban in current_banned[:20]])
    else:
        banned_ip_list = "なし"
    
    # Jailリストを準備
    jail_list = fail2ban_details.replace('- ', '').replace('件', '').replace('\n', ', ')
    
    # 統計情報を計算
    ban_count = 0
    unban_count = 0
    if ban_history_data:
        ban_count = len([ban for ban in ban_history_data if ban['action'] == 'Ban'])
        unban_count = len([ban for ban in ban_history_data if ban['action'] == 'Unban'])
    
    report_content = f"""
===================================================
Fail2ban 週次セキュリティレポート
週: {year}-W{week_num:02d}
作成日時: {timestamp}
サーバー: DXP2800
===================================================

【現在のセキュリティ状況】
Status
|- Number of jail:	{fail2ban_data['active_jails']}
`- Jail list:	{jail_list}

【各Jailの詳細】

[SSH保護]
Status for the jail: sshd
|- Filter
|  |- Currently failed:	0
|  |- Total failed:	{fail2ban_data.get('total_failed', 0)}
|  `- File list:	/var/log/auth.log
`- Actions
  |- Currently banned:	{fail2ban_data['total_banned']}
  |- Total banned:	{fail2ban_data['total_banned']}
  `- Banned IP list:	{banned_ip_list}

[Web認証保護]
Status for the jail: nginx-http-auth
|- Filter
|  |- Currently failed:	0
|  |- Total failed:	0
|  `- File list:	/var/log/nginx/error.log
`- Actions
  |- Currently banned:	0
  |- Total banned:	0
  `- Banned IP list:	

[レート制限保護]
Status for the jail: nginx-req-limit
|- Filter
|  |- Currently failed:	0
|  |- Total failed:	0
|  `- File list:	/var/log/nginx/error.log
`- Actions
  |- Currently banned:	0
  |- Total banned:	0
  `- Banned IP list:	

【過去7日間のBAN活動（最新20件）】
{ban_activity}

【統計】
今週のBAN実行回数: {ban_count} 回
今週のUNBAN実行回数: {unban_count} 回

【攻撃元TOP5】
{attack_sources}

【セキュリティ設定】
- SSH BAN期間: 7日間、最大試行回数: 3回
- Web認証 BAN期間: 24時間、最大試行回数: 2回
- レート制限 BAN期間: 1時間、最大試行回数: 5回

【システム状況】
- CPU使用率: {system_data['cpu_percent']:.1f}% ({cpu_status})
- メモリ使用率: {system_data['memory_percent']:.1f}% ({memory_status})
- ディスク使用率: {system_data['disk_percent']:.1f}% ({disk_status})

【推奨事項】
{recommendations_text}
        """
    
    return report_content

def generate_monthly_report_content(system_data, fail2ban_data, docker_data, ban_history_data, ai_analysis):
    """月次AI分析レポート内容を生成"""
    timestamp = system_data['timestamp']
    
    # 月番号を計算
    from datetime import datetime
    month_num = datetime.now().month
    year = datetime.now().year
    
    # AI分析結果を取得
    summary = ai_analysis.get('summary', '分析結果なし')
    insights = ai_analysis.get('insights', [])
    recommendations = ai_analysis.get('recommendations', [])
    risk_level = ai_analysis.get('risk_level', 'UNKNOWN')
    trends = ai_analysis.get('trends', {})
    
    # 統計情報を準備
    ban_count = len(ban_history_data) if ban_history_data else 0
    unban_count = 0  # UNBANは現在未実装
    
    # 攻撃元TOP5を準備
    attack_sources = ""
    if ban_history_data:
        attack_sources = "\n".join([f"- {ban['ip']} ({ban['jail']})" for ban in ban_history_data[:5]])
    else:
        attack_sources = "なし"
    
    # 推奨事項を準備
    recommendations_text = "\n".join([f"- {rec}" for rec in recommendations])
    
    # 洞察を準備
    insights_text = "\n".join([f"- {insight}" for insight in insights])
    
    # トレンド情報を準備
    ban_trend = trends.get('ban_trend', '不明')
    attack_patterns = trends.get('attack_patterns', '分析中')
    system_health = trends.get('system_health', '良好')
    
    report_content = f"""
===================================================
Fail2ban 月次AI分析セキュリティレポート
月: {year}-{month_num:02d}
作成日時: {timestamp}
サーバー: DXP2800
===================================================

【AI分析サマリー】
{summary}

【リスクレベル】
{risk_level}

【重要な洞察】
{insights_text}

【AI推奨事項】
{recommendations_text}

【セキュリティ統計】
- 今月のBAN実行回数: {ban_count} 回
- 今月のUNBAN実行回数: {unban_count} 回
- アクティブなJail数: {fail2ban_data['active_jails']} 個
- 総BAN数: {fail2ban_data['total_banned']} 件

【攻撃元TOP5】
{attack_sources}

【トレンド分析】
- BAN傾向: {ban_trend}
- 攻撃パターン: {attack_patterns}
- システム健全性: {system_health}

【システム状況】
- CPU使用率: {system_data['cpu_percent']:.1f}%
- メモリ使用率: {system_data['memory_percent']:.1f}%
- ディスク使用率: {system_data['disk_percent']:.1f}%

【過去30日間のBAN活動（最新20件）】
{chr(10).join([f"- {ban['ip']} | {ban['jail']} | {ban['timestamp']}" for ban in ban_history_data[:20]]) if ban_history_data else "なし"}

【Dockerコンテナ状況】
- 稼働中コンテナ: {docker_data['running_containers']}/{docker_data['total_containers']} 個
- 停止中コンテナ: {docker_data['stopped_containers']} 個

【AI分析詳細】
- 分析モデル: Gemini 2.0 Flash
- 分析期間: 過去30日間
- データソース: Fail2banログ、システム統計

===================================================
このレポートはAI分析により自動生成されました。
NAS統合管理システム
===================================================
    """
    
    return report_content

@app.route('/api/reports/monthly', methods=['POST'])
def generate_monthly_report():
    """月次AI分析レポートを生成"""
    try:
        # 過去30日間のデータを取得
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # システムデータを取得
        system_data = get_system_status_data()
        fail2ban_data = get_fail2ban_status_data()
        docker_data = get_docker_status_data()
        
        # 過去30日間のBAN履歴を取得
        logger.info("月次レポート用BAN履歴取得開始")
        ban_history_data = get_monthly_ban_history()
        logger.info(f"月次BAN履歴データ取得完了: {len(ban_history_data) if ban_history_data else 0}件")
        
        # AI分析用データを準備
        security_data = {
            'ban_history': ban_history_data,
            'system_stats': system_data,
            'fail2ban_stats': fail2ban_data,
            'docker_stats': docker_data,
            'period': thirty_days_ago.strftime('%Y-%m')
        }
        
        # AI分析実行
        logger.info("AI分析開始")
        ai_analyzer = AIAnalyzer()
        ai_analysis = ai_analyzer.analyze_monthly_security_data(security_data)
        logger.info("AI分析完了")
        
        # 月次レポート内容を生成
        report_content = generate_monthly_report_content(system_data, fail2ban_data, docker_data, ban_history_data, ai_analysis)
        
        # レポートファイルを保存
        # NAS環境では統合データディレクトリを使用、ローカル環境では相対パスを使用
        if os.getenv('NAS_MODE') and os.path.exists('/app/reports'):
            report_dir = Path('/app/reports')
        else:
            report_dir = Path('/Users/Yoshi/nas-project/data/reports')
        
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"monthly_report_{timestamp}.txt"
        report_file.write_text(report_content, encoding='utf-8')
        
        # メール送信のオプション
        send_email = request.json.get('send_email', False) if request.is_json else False
        
        if send_email:
            try:
                email_to = os.getenv('EMAIL_TO')
                if email_to:
                    email_sender = EmailSender()
                    email_sender.send_monthly_report(email_to, report_content, ai_analysis)
                    logger.info("月次AI分析レポートメール送信完了")
                else:
                    logger.warning("EMAIL_TO環境変数が設定されていません")
            except Exception as email_error:
                logger.error(f"メール送信エラー: {email_error}")
        
        return jsonify({
            'success': True,
            'message': f'月次AI分析レポートが生成されました: {report_file.name}',
            'output': report_content,
            'ai_analysis': ai_analysis,
            'email_sent': send_email and os.getenv('EMAIL_TO') is not None
        })
            
    except Exception as e:
        logger.error(f"月次AI分析レポート生成エラー: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/reports/weekly', methods=['POST'])
def generate_weekly_report():
    """週次レポートを生成"""
    try:
        # 実際のシステムデータを取得
        system_data = get_system_status_data()
        fail2ban_data = get_fail2ban_status_data()
        docker_data = get_docker_status_data()
        
        # BAN履歴を取得（位置情報なし）
        logger.info("BAN履歴取得開始")
        ban_history_data = get_ban_history_simple()
        logger.info(f"BAN履歴データ取得完了: {len(ban_history_data) if ban_history_data else 0}件")
        if ban_history_data:
            for ban in ban_history_data:
                logger.info(f"BAN履歴: {ban['ip']} | {ban['jail']} | {ban['timestamp']}")
        
        # レポート内容を生成
        report_content = generate_report_content(system_data, fail2ban_data, docker_data, ban_history_data)
        
        # レポートファイルを保存
        # NAS環境では統合データディレクトリを使用、ローカル環境では相対パスを使用
        if os.getenv('NAS_MODE') and os.path.exists('/app/reports'):
            report_dir = Path('/app/reports')
        else:
            report_dir = Path('/Users/Yoshi/nas-project/data/reports')
        
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"weekly_report_{timestamp}.txt"
        report_file.write_text(report_content, encoding='utf-8')
        
        # メール送信のオプション
        send_email = request.json.get('send_email', False) if request.is_json else False
        
        if send_email:
            try:
                email_to = os.getenv('EMAIL_TO')
                if email_to:
                    email_sender = EmailSender()
                    report_data = {
                        'system_data': system_data,
                        'fail2ban_data': fail2ban_data,
                        'docker_data': docker_data,
                        'ban_history_data': ban_history_data
                    }
                    email_sender.send_weekly_report(email_to, report_content, report_data)
                    logger.info("週次レポートメール送信完了")
                else:
                    logger.warning("EMAIL_TO環境変数が設定されていません")
            except Exception as email_error:
                logger.error(f"メール送信エラー: {email_error}")
        
        return jsonify({
            'success': True,
            'message': f'週次レポートが生成されました: {report_file.name}',
            'output': report_content,
            'email_sent': send_email and os.getenv('EMAIL_TO') is not None
        })
            
    except Exception as e:
        logger.error(f"週次レポート生成エラー: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/docker/containers')
def docker_containers():
    """Dockerコンテナの状態を取得"""
    try:
        # NAS環境では実際のDockerコンテナ情報を取得
        if os.getenv('NAS_MODE'):
            result = subprocess.run([
                'docker', 'ps', '--format', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        container_info = json.loads(line)
                        containers.append({
                            'id': container_info['ID'],
                            'name': container_info['Names'],
                            'image': container_info['Image'],
                            'status': container_info['Status'],
                            'ports': container_info['Ports']
                        })
                
                return jsonify(containers)
            else:
                return jsonify({'error': 'Dockerコンテナ情報の取得に失敗しました'}), 500
        else:
            # ローカル環境ではモックデータを返す
            return jsonify([
                {
                    'id': 'mock-container-1',
                    'name': 'nas-dashboard',
                    'image': 'nas-dashboard:latest',
                    'status': 'Up 2 hours',
                    'ports': '9000/tcp'
                },
                {
                    'id': 'mock-container-2', 
                    'name': 'meeting-minutes-byc',
                    'image': 'meeting-minutes-byc:latest',
                    'status': 'Up 1 day',
                    'ports': '5002/tcp'
                }
            ])
            
    except Exception as e:
        logger.error(f"Dockerコンテナ情報取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

# Insta360自動同期システム関連のAPIエンドポイント
@app.route('/api/insta360/status')
def insta360_status():
    """Insta360自動同期システムの状態を取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のDockerコンテナの状態を確認
            result = subprocess.run([
                'docker', 'ps', '--filter', 'name=insta360-auto-sync', '--format', '{{.Status}}'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                # コンテナが稼働している場合
                return jsonify({
                    'status': 'running',
                    'container_status': result.stdout.strip(),
                    'message': 'Insta360自動同期システムが稼働中です'
                })
            else:
                return jsonify({
                    'status': 'stopped',
                    'container_status': 'Not running',
                    'message': 'Insta360自動同期システムが停止しています'
                })
        else:
            # ローカル環境ではモックデータを返す
            return jsonify({
                'status': 'mock',
                'container_status': 'Up 1 day',
                'message': 'ローカル環境のため、モックデータを表示しています'
            })
            
    except Exception as e:
        logger.error(f"Insta360状態取得エラー: {e}")
        return jsonify({
            'status': 'error',
            'message': f'状態取得に失敗しました: {str(e)}'
        }), 500


@app.route('/api/insta360/logs')
def insta360_logs():
    """Insta360同期ログを取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のログファイルを読み取り
            log_paths = [
                '/app/logs/insta360_sync.log',
                '/app/logs/cleanup.log'
            ]
            
            logs = []
            for log_path in log_paths:
                if os.path.exists(log_path):
                    try:
                        # 最後の100行を取得
                        with open(log_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            recent_lines = lines[-100:] if len(lines) > 100 else lines
                            
                            logs.append({
                                'filename': os.path.basename(log_path),
                                'path': log_path,
                                'size': os.path.getsize(log_path),
                                'lines': len(lines),
                                'recent_lines': recent_lines,
                                'last_modified': datetime.fromtimestamp(os.path.getmtime(log_path)).isoformat()
                            })
                    except Exception as e:
                        logger.warning(f"ログファイル読み取りエラー {log_path}: {e}")
                        continue
            
            return jsonify({
                'success': True,
                'logs': logs,
                'total_logs': len(logs),
                'timestamp': datetime.now().isoformat()
            })
        else:
            # ローカル環境ではモックデータを返す
            return jsonify({
                'success': True,
                'logs': [
                    {
                        'filename': 'insta360_sync.log',
                        'path': '/app/logs/insta360_sync.log',
                        'size': 1024,
                        'lines': 50,
                        'recent_lines': [
                            '2024-01-15 14:30:15 - INFO - Insta360ファイル同期を開始します\n',
                            '2024-01-15 14:30:16 - INFO - 転送対象ファイル: 3件\n',
                            '2024-01-15 14:30:20 - INFO - ファイル転送完了: VID_20240115_143020.mp4\n',
                            '2024-01-15 14:30:25 - INFO - Insta360ファイル同期が完了しました\n'
                        ],
                        'last_modified': datetime.now().isoformat()
                    }
                ],
                'total_logs': 1,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Insta360ログ取得エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'ログ取得に失敗しました: {str(e)}',
            'logs': [],
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/insta360/test-connection')
def insta360_test_connection():
    """Insta360同期システムの接続テスト"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のテストを実行
            result = subprocess.run([
                'docker', 'exec', 'insta360-auto-sync', 'python', '/app/scripts/sync.py', '--test'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': '接続テストが成功しました',
                    'output': result.stdout,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'接続テストでエラーが発生しました: {result.stderr}',
                    'output': result.stdout,
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }), 500
        else:
            # ローカル環境ではモックレスポンス
            return jsonify({
                'success': True,
                'message': '接続テストが成功しました（モック）',
                'output': 'モック環境のため、実際のテストは実行されませんでした',
                'timestamp': datetime.now().isoformat()
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': '接続テストがタイムアウトしました',
            'timestamp': datetime.now().isoformat()
        }), 500
    except Exception as e:
        logger.error(f"Insta360接続テストエラー: {e}")
        return jsonify({
            'success': False,
            'message': f'接続テストに失敗しました: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500








@app.route('/api/docker/containers')
def get_docker_containers():
    """Dockerコンテナ一覧を取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のDockerコンテナを取得
            result = subprocess.run([
                'docker', 'ps', '-a', '--format', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            container_data = json.loads(line)
                            # Namesフィールドから先頭の/を削除し、最初の名前のみを使用
                            names = container_data.get('Names', '').strip()
                            if names:
                                # 複数の名前がスペース区切りの場合、最初の名前を使用
                                name = names.split()[0] if ' ' in names else names
                                # 先頭の/を削除
                                name = name.lstrip('/')
                            else:
                                name = container_data.get('ID', '')[:12]  # IDの最初の12文字をフォールバック
                            
                            containers.append({
                                'id': container_data.get('ID', ''),
                                'name': name,
                                'image': container_data.get('Image', ''),
                                'status': container_data.get('Status', ''),
                                'state': container_data.get('State', ''),
                                'created': container_data.get('CreatedAt', ''),
                                'ports': container_data.get('Ports', '')
                            })
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSONパースエラー: {line[:100]}... - {e}")
                            continue
                
                # コンテナ名でソート
                containers.sort(key=lambda x: x['name'].lower())
                
                return jsonify({
                    'success': True,
                    'containers': containers,
                    'total_containers': len(containers),
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Dockerコンテナ取得に失敗しました: {result.stderr}',
                    'containers': [],
                    'timestamp': datetime.now().isoformat()
                }), 500
        else:
            # ローカル環境でも実際のDockerコンテナを取得を試行
            try:
                result = subprocess.run([
                    'docker', 'ps', '-a', '--format', 'json'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    containers = []
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            try:
                                container_data = json.loads(line)
                                # Namesフィールドから先頭の/を削除し、最初の名前のみを使用
                                names = container_data.get('Names', '').strip()
                                if names:
                                    # 複数の名前がスペース区切りの場合、最初の名前を使用
                                    name = names.split()[0] if ' ' in names else names
                                    # 先頭の/を削除
                                    name = name.lstrip('/')
                                else:
                                    name = container_data.get('ID', '')[:12]  # IDの最初の12文字をフォールバック
                                
                                containers.append({
                                    'id': container_data.get('ID', ''),
                                    'name': name,
                                    'image': container_data.get('Image', ''),
                                    'status': container_data.get('Status', ''),
                                    'state': container_data.get('State', ''),
                                    'created': container_data.get('CreatedAt', ''),
                                    'ports': container_data.get('Ports', '')
                                })
                            except json.JSONDecodeError as e:
                                logger.warning(f"JSONパースエラー: {line[:100]}... - {e}")
                                continue
                    
                    # コンテナ名でソート
                    containers.sort(key=lambda x: x['name'].lower())
                    
                    return jsonify({
                        'success': True,
                        'containers': containers,
                        'total_containers': len(containers),
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    # Dockerコンテナが見つからない場合はモックデータを返す
                    return jsonify({
                        'success': True,
                        'containers': [
                            {
                                'id': 'abc123def456',
                                'name': 'nas-dashboard',
                                'image': 'nas-dashboard:latest',
                                'status': 'Up 2 hours',
                                'state': 'running',
                                'created': '2024-01-15T12:00:00Z',
                                'ports': '9001->9000/tcp'
                            },
                            {
                                'id': 'def456ghi789',
                                'name': 'amazon-analytics',
                                'image': 'amazon-analytics:latest',
                                'status': 'Up 1 hour',
                                'state': 'running',
                                'created': '2024-01-15T13:00:00Z',
                                'ports': '8000->8000/tcp'
                            }
                        ],
                        'total_containers': 2,
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                # Dockerコマンドが失敗した場合はモックデータを返す
                return jsonify({
                    'success': True,
                    'containers': [
                        {
                            'id': 'abc123def456',
                            'name': 'nas-dashboard',
                            'image': 'nas-dashboard:latest',
                            'status': 'Up 2 hours',
                            'state': 'running',
                            'created': '2024-01-15T12:00:00Z',
                            'ports': '9001->9000/tcp'
                        }
                    ],
                    'total_containers': 1,
                    'timestamp': datetime.now().isoformat()
                })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': 'Dockerコンテナ取得がタイムアウトしました',
            'containers': [],
            'timestamp': datetime.now().isoformat()
        }), 500
    except Exception as e:
        logger.error(f"Dockerコンテナ取得エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'Dockerコンテナ取得に失敗しました: {str(e)}',
            'containers': [],
            'timestamp': datetime.now().isoformat()
        }), 500






@app.route('/api/docker/logs/<container_name>')
def get_docker_logs(container_name):
    """特定のDockerコンテナのログを取得（シンプル実装）"""
    try:
        # コンテナの存在確認
        check_result = subprocess.run([
            'docker', 'ps', '-a', '--format', '{{.Names}}'
        ], capture_output=True, text=True, timeout=5)
        
        if check_result.returncode != 0:
            return jsonify({
                'success': False,
                'message': f'コンテナ一覧の取得に失敗しました: {check_result.stderr}',
                'logs': [],
                'timestamp': datetime.now().isoformat()
            }), 500
        
        available_containers = [name.strip() for name in check_result.stdout.split('\n') if name.strip()]
        
        if container_name not in available_containers:
            return jsonify({
                'success': False,
                'message': f"コンテナ '{container_name}' が見つかりません",
                'logs': [],
                'container_name': container_name,
                'total_lines': 0,
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # ログを取得（stdoutとstderrの両方を取得）
        result = subprocess.run([
            'docker', 'logs', '--tail', '100', '--timestamps', container_name
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logs = result.stdout.split('\n')
            # 空行と空文字列をフィルタリング
            filtered_logs = [log.strip() for log in logs if log.strip()]
            
            # ログが空の場合はstderrも確認
            if not filtered_logs and result.stderr:
                stderr_logs = result.stderr.split('\n')
                filtered_logs = [log.strip() for log in stderr_logs if log.strip()]
            
            # それでもログが空の場合はメッセージを追加
            if not filtered_logs:
                filtered_logs = [f"コンテナ '{container_name}' にはログがありません"]
            
            return jsonify({
                'success': True,
                'logs': filtered_logs,
                'container_name': container_name,
                'total_lines': len(filtered_logs),
                'timestamp': datetime.now().isoformat()
            })
        else:
            # エラーでもstderrにログがある可能性がある
            error_logs = []
            if result.stderr:
                error_logs = [log.strip() for log in result.stderr.split('\n') if log.strip()]
            
            if error_logs:
                return jsonify({
                    'success': True,
                    'logs': error_logs,
                    'container_name': container_name,
                    'total_lines': len(error_logs),
                    'timestamp': datetime.now().isoformat()
                })
            
            return jsonify({
                'success': False,
                'message': f'ログ取得に失敗しました: {result.stderr}',
                'logs': [],
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except subprocess.TimeoutExpired:
        logger.error(f"Dockerログ取得タイムアウト ({container_name})")
        return jsonify({
            'success': False,
            'message': 'ログ取得がタイムアウトしました',
            'logs': [],
            'timestamp': datetime.now().isoformat()
        }), 500
    except Exception as e:
        logger.error(f"Dockerログ取得エラー ({container_name}): {e}")
        return jsonify({
            'success': False,
            'message': f'ログ取得に失敗しました: {str(e)}',
            'logs': [],
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/logs/text')
def get_text_logs():
    """テキストログ一覧を取得（システム別）"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のログファイルを読み取り
            # docker-compose.ymlで /home/AdminUser/nas-project-data:/nas-project-data にマウントされている
            log_systems = {
                'meeting-minutes-byc': {
                    'name': 'Meeting Minutes BYC',
                    'log_file': '/nas-project-data/meeting-minutes-byc/logs/app.log'
                },
                'amazon-analytics': {
                    'name': 'Amazon Analytics',
                    'log_file': '/nas-project-data/amazon-analytics/logs/app.log'
                },
                'document-automation': {
                    'name': 'Document Automation',
                    'log_file': '/nas-project-data/document-automation/logs/app.log'
                },
                'youtube-to-notion': {
                    'name': 'YouTube to Notion',
                    'log_file': '/nas-project-data/youtube-to-notion/logs/app.log'
                },
                'nas-dashboard': {
                    'name': 'NAS Dashboard',
                    'log_file': '/nas-project-data/nas-dashboard/logs/app.log'
                },
                'nas-dashboard-monitoring': {
                    'name': 'NAS Dashboard Monitoring',
                    'log_file': '/nas-project-data/nas-dashboard-monitoring/logs/app.log'
                }
            }
        else:
            # Dockerコンテナ内ではマウントされたパスを使用
            log_systems = {
                'nas-dashboard': {
                    'name': 'NAS Dashboard',
                    'log_file': '/app/logs/app.log'
                }
            }
        
        systems = []
        for system_id, system_info in log_systems.items():
            if os.path.exists(system_info['log_file']):
                try:
                    with open(system_info['log_file'], 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        # 最新の10行を取得
                        recent_lines = lines[-10:] if len(lines) > 10 else lines
                        logs = [line.strip() for line in recent_lines if line.strip()]
                        systems.append({
                            'id': system_id,
                            'name': system_info['name'],
                            'logs': logs,
                            'total_lines': len(logs)
                        })
                except Exception as e:
                    logger.warning(f"ログファイル読み取りエラー {system_info['log_file']}: {e}")
                    continue
        
        return jsonify({
            'success': True,
            'systems': systems,
            'total_systems': len(systems),
            'timestamp': datetime.now().isoformat()
        })
            
    except Exception as e:
        logger.error(f"テキストログ取得エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'ログ取得に失敗しました: {str(e)}',
            'systems': [],
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/logs/text/<system_id>')
def get_text_logs_by_system(system_id):
    """特定システムのテキストログを取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のログファイルを読み取り
            # docker-compose.ymlで /home/AdminUser/nas-project-data:/nas-project-data にマウントされている
            log_files = {
                'meeting-minutes-byc': '/nas-project-data/meeting-minutes-byc/logs/app.log',
                'amazon-analytics': '/nas-project-data/amazon-analytics/logs/app.log',
                'document-automation': '/nas-project-data/document-automation/logs/app.log',
                'youtube-to-notion': '/nas-project-data/youtube-to-notion/logs/app.log',
                'nas-dashboard': '/nas-project-data/nas-dashboard/logs/app.log',
                'nas-dashboard-monitoring': '/nas-project-data/nas-dashboard-monitoring/logs/app.log'
            }
        else:
            # Dockerコンテナ内ではマウントされたパスを使用
            log_files = {
                'nas-dashboard': '/app/logs/app.log'
            }
        
        if system_id not in log_files:
            return jsonify({
                'success': False,
                'message': f'システム {system_id} が見つかりません',
                'logs': [],
                'timestamp': datetime.now().isoformat()
            }), 404
        
        log_file = log_files[system_id]
        if not os.path.exists(log_file):
            return jsonify({
                'success': False,
                'message': f'ログファイルが見つかりません: {log_file}',
                'logs': [],
                'timestamp': datetime.now().isoformat()
            }), 404
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # 最新の50行を取得
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                logs = [line.strip() for line in recent_lines if line.strip()]
            
            return jsonify({
                'success': True,
                'logs': logs,
                'total_lines': len(logs),
                'system_id': system_id,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"ログファイル読み取りエラー {log_file}: {e}")
            return jsonify({
                'success': False,
                'message': f'ログファイル読み取りエラー: {str(e)}',
                'logs': [],
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"テキストログ取得エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'ログ取得に失敗しました: {str(e)}',
            'logs': [],
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/security/analysis')
def security_analysis():
    """セキュリティ分析結果を取得"""
    try:
        logger.info("AI分析APIが呼び出されました")
        
        # タイムアウト付きでAI分析を実行
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("AI分析がタイムアウトしました")
        
        # 30秒のタイムアウトを設定
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)
        
        try:
            analysis_result = analyze_security_data()
            signal.alarm(0)  # タイムアウトを解除
            logger.info(f"AI分析結果: {analysis_result.get('status', 'unknown')}")
            return jsonify(analysis_result)
        except TimeoutError as e:
            signal.alarm(0)  # タイムアウトを解除
            logger.error(f"AI分析タイムアウト: {e}")
            return jsonify({
                'status': 'error',
                'message': 'AI分析がタイムアウトしました。しばらくしてから再試行してください。',
                'analysis': None
            }), 408
    except Exception as e:
        logger.error(f"セキュリティ分析APIエラー: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'analysis': None
        }), 500

@app.route('/api/email/test', methods=['POST'])
def send_test_email():
    """テストメール送信"""
    try:
        logger.info("テストメール送信APIが呼び出されました")
        
        # メール送信設定を確認
        email_sender = EmailSender()
        
        # テストメールの内容
        subject = "NAS システム - テストメール"
        body = f"""
        <h2>NAS システム テストメール</h2>
        <p>このメールはNASシステムのメール送信機能のテストです。</p>
        <p><strong>送信時刻:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>システム:</strong> NAS統合管理ダッシュボード</p>
        <hr>
        <p><small>このメールは自動送信されています。</small></p>
        """
        
        # メール送信
        success = email_sender.send_email(subject, body)
        
        if success:
            logger.info("テストメール送信成功")
            return jsonify({
                'success': True,
                'message': 'テストメールを送信しました'
            })
        else:
            logger.error("テストメール送信失敗")
            return jsonify({
                'success': False,
                'message': 'メール送信に失敗しました'
            }), 500
            
    except Exception as e:
        logger.error(f"テストメール送信エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'メール送信エラー: {str(e)}'
        }), 500

@app.route('/api/email/weekly-report', methods=['POST'])
def send_weekly_report():
    """週次レポート送信"""
    try:
        logger.info("週次レポート送信APIが呼び出されました")
        
        # メール送信設定を確認
        email_sender = EmailSender()
        
        # 週次レポートの内容を生成
        report_data = generate_weekly_report_data()
        
        subject = f"NAS システム 週次レポート - {report_data['period']}"
        body = f"""
        <h2>NAS システム 週次レポート</h2>
        <p><strong>期間:</strong> {report_data['period']}</p>
        
        <h3>システム概要</h3>
        <ul>
            <li><strong>稼働時間:</strong> {report_data['uptime']}</li>
            <li><strong>CPU使用率:</strong> {report_data['cpu_usage']}%</li>
            <li><strong>メモリ使用率:</strong> {report_data['memory_usage']}%</li>
            <li><strong>ディスク使用率:</strong> {report_data['disk_usage']}%</li>
        </ul>
        
        <h3>セキュリティ状況</h3>
        <ul>
            <li><strong>BAN総数:</strong> {report_data['total_bans']}件</li>
            <li><strong>新規BAN:</strong> {report_data['new_bans']}件</li>
            <li><strong>アクティブなBAN:</strong> {report_data['active_bans']}件</li>
        </ul>
        
        <h3>バックアップ状況</h3>
        <ul>
            <li><strong>バックアップ総数:</strong> {report_data['backup_count']}件</li>
            <li><strong>最新バックアップ:</strong> {report_data['latest_backup']}</li>
        </ul>
        
        <hr>
        <p><small>このレポートは自動生成されています。</small></p>
        """
        
        # メール送信
        success = email_sender.send_email(subject, body)
        
        if success:
            logger.info("週次レポート送信成功")
            return jsonify({
                'success': True,
                'message': '週次レポートを送信しました'
            })
        else:
            logger.error("週次レポート送信失敗")
            return jsonify({
                'success': False,
                'message': 'レポート送信に失敗しました'
            }), 500
            
    except Exception as e:
        logger.error(f"週次レポート送信エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'レポート送信エラー: {str(e)}'
        }), 500

def generate_weekly_report_data():
    """週次レポートデータを生成"""
    try:
        # システム情報を取得
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 期間を計算
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        period = f"{week_ago.strftime('%Y-%m-%d')} ～ {now.strftime('%Y-%m-%d')}"
        
        # バックアップ情報を取得
        backup_dir = os.getenv('BACKUP_DIR', '/home/AdminUser/nas-project-data/backups')
        backup_files = []
        if os.path.exists(backup_dir):
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
        
        return {
            'period': period,
            'uptime': '7日間（24時間稼働）',
            'cpu_usage': round(cpu_usage, 1),
            'memory_usage': round(memory.percent, 1),
            'disk_usage': round(disk.percent, 1),
            'total_bans': 0,  # 実際の実装ではFail2Banから取得
            'new_bans': 0,
            'active_bans': 0,
            'backup_count': len(backup_files),
            'latest_backup': backup_files[0] if backup_files else 'なし'
        }
    except Exception as e:
        logger.error(f"週次レポートデータ生成エラー: {e}")
        return {
            'period': '不明',
            'uptime': '不明',
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'total_bans': 0,
            'new_bans': 0,
            'active_bans': 0,
            'backup_count': 0,
            'latest_backup': 'なし'
        }

def generate_monthly_ai_report_data(system_data, fail2ban_data, docker_data):
    """月次AI分析レポートデータを生成"""
    try:
        # システム情報を取得
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 期間を計算（前月1日から今月1日まで）
        now = datetime.now()
        if now.month == 1:
            # 1月の場合、前年12月から
            start_date = datetime(now.year - 1, 12, 1)
        else:
            # その他の月は前月1日から
            start_date = datetime(now.year, now.month - 1, 1)
        
        end_date = datetime(now.year, now.month, 1)
        period = f"{start_date.strftime('%Y年%m月')} ～ {end_date.strftime('%Y年%m月')}"
        
        # バックアップ情報を取得
        backup_dir = os.getenv('BACKUP_DIR', '/home/AdminUser/nas-project-data/backups')
        backup_files = []
        if os.path.exists(backup_dir):
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
        
        # AI分析用のデータを準備
        ai_analysis_data = {
            'period': period,
            'system_metrics': {
                'cpu_usage': round(cpu_usage, 1),
                'memory_usage': round(memory.percent, 1),
                'disk_usage': round(disk.percent, 1),
                'uptime_days': 30  # 月次なので30日間
            },
            'security_metrics': {
                'total_bans': fail2ban_data.get('total_banned', 0),
                'active_jails': fail2ban_data.get('active_jails', 0),
                'security_events': fail2ban_data.get('security_events', 0)
            },
            'container_metrics': {
                'running_containers': docker_data.get('running_containers', 0),
                'total_containers': docker_data.get('total_containers', 0),
                'container_health': docker_data.get('health_status', 'unknown')
            },
            'backup_metrics': {
                'backup_count': len(backup_files),
                'latest_backup': backup_files[0] if backup_files else 'なし',
                'backup_success_rate': 100 if backup_files else 0
            }
        }
        
        # AI分析を実行
        try:
            logger.info("月次AI分析を開始します")
            
            # 過去30日間のBAN履歴を取得
            ban_history_data = get_monthly_ban_history()
            logger.info(f"月次BAN履歴取得完了: {len(ban_history_data)}件")
            
            # 期間をYYYY-MM形式に変換
            period_str = start_date.strftime('%Y-%m')
            
            # AI分析用データを準備
            security_data = {
                'ban_history': ban_history_data,
                'system_stats': {
                    'cpu_percent': round(cpu_usage, 1),
                    'memory_percent': round(memory.percent, 1),
                    'disk_percent': round(disk.percent, 1)
                },
                'fail2ban_stats': fail2ban_data,
                'docker_stats': docker_data,
                'period': period_str
            }
            
            # AIAnalyzerを使用して分析
            ai_analyzer = AIAnalyzer()
            ai_analysis_result = ai_analyzer.analyze_monthly_security_data(security_data)
            
            logger.info("月次AI分析完了")
            ai_analysis_data['ai_analysis'] = ai_analysis_result
            # BAN履歴も含める（レポートファイル用）
            ai_analysis_data['ban_history'] = ban_history_data
        except Exception as ai_error:
            logger.error(f"AI分析エラー: {ai_error}", exc_info=True)
            ai_analysis_data['ai_analysis'] = {
                'summary': 'AI分析を実行できませんでした',
                'risk_level': 'UNKNOWN',
                'insights': ['AI分析サービスが利用できません'],
                'recommendations': ['AI分析設定を確認してください']
            }
            ai_analysis_data['ban_history'] = []
        
        return ai_analysis_data
        
    except Exception as e:
        logger.error(f"月次AI分析レポートデータ生成エラー: {e}")
        return {
            'period': '不明',
            'system_metrics': {'cpu_usage': 0, 'memory_usage': 0, 'disk_usage': 0, 'uptime_days': 0},
            'security_metrics': {'total_bans': 0, 'active_jails': 0, 'security_events': 0},
            'container_metrics': {'running_containers': 0, 'total_containers': 0, 'container_health': 'unknown'},
            'backup_metrics': {'backup_count': 0, 'latest_backup': 'なし', 'backup_success_rate': 0},
            'ai_analysis': {
                'summary': 'レポート生成エラーが発生しました',
                'risk_level': 'UNKNOWN',
                'insights': ['システムエラーが発生しました'],
                'recommendations': ['システム管理者に連絡してください']
            }
        }

@app.route('/api/logs/analysis', methods=['POST'])
def analyze_logs():
    """ログ分析結果を取得"""
    try:
        logger.info("ログ分析APIが呼び出されました")
        
        # リクエストデータを取得
        data = request.get_json()
        system_id = data.get('system_id', 'nas-dashboard')
        analysis_type = data.get('analysis_type', 'general')
        
        # タイムアウト付きでログ分析を実行
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("ログ分析がタイムアウトしました")
        
        # 30秒のタイムアウトを設定
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)
        
        try:
            analysis_result = analyze_log_data(system_id, analysis_type)
            signal.alarm(0)  # タイムアウトを解除
            logger.info(f"ログ分析結果: {analysis_result.get('status', 'unknown')}")
            return jsonify(analysis_result)
        except TimeoutError as e:
            signal.alarm(0)  # タイムアウトを解除
            logger.error(f"ログ分析タイムアウト: {e}")
            return jsonify({
                'status': 'error',
                'message': 'ログ分析がタイムアウトしました。しばらくしてから再試行してください。',
                'analysis': None
            }), 408
    except Exception as e:
        logger.error(f"ログ分析APIエラー: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'analysis': None
        }), 500

def analyze_log_data(system_id, analysis_type):
    """ログデータをAIで分析"""
    try:
        logger.info(f"ログ分析を開始します: {system_id}, {analysis_type}")
        if not model:
            logger.error("Gemini AIモデルが設定されていません")
            return {
                'status': 'error',
                'message': 'Gemini AIが設定されていません',
                'analysis': None
            }
        
        # ログデータを取得
        log_data = get_log_data_for_analysis(system_id)
        
        # 分析用のデータを準備
        analysis_data = {
            'system_id': system_id,
            'analysis_type': analysis_type,
            'log_data': log_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # AI分析のプロンプトを作成
        prompt = create_log_analysis_prompt(analysis_data)
        
        logger.info("Gemini AIでログ分析を開始します")
        try:
            response = model.generate_content(prompt)
            analysis_result = response.text
            logger.info("Gemini AIログ分析が完了しました")
        except Exception as e:
            logger.error(f"Gemini AIログ分析エラー: {e}")
            return {
                'status': 'error',
                'message': f'AI分析でエラーが発生しました: {str(e)}',
                'analysis': None
            }
        
        return {
            'status': 'success',
            'analysis': analysis_result,
            'system_id': system_id,
            'analysis_type': analysis_type,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"ログ分析エラー: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'analysis': None
        }

def get_log_data_for_analysis(system_id):
    """分析用のログデータを取得"""
    try:
        # システムタイプを判定
        system_type = determine_system_type(system_id)
        
        if system_type == 'docker':
            # Dockerコンテナのログを取得
            return get_docker_only_log_data_for_analysis(system_id)
        elif system_type == 'hybrid':
            # ハイブリッドシステム（テキストログ + Dockerログ）の場合
            return get_hybrid_log_data_for_analysis(system_id)
        else:
            # テキストログファイルのパスを取得
            if os.getenv('NAS_MODE') and os.path.exists('/nas-project-data'):
                log_files = {
                    'meeting-minutes-byc': '/nas-project-data/meeting-minutes-byc/logs/app.log',
                    'amazon-analytics': '/nas-project-data/amazon-analytics/logs/app.log',
                    'document-automation': '/nas-project-data/document-automation/logs/app.log',
                    'youtube-to-notion': '/nas-project-data/youtube-to-notion/logs/app.log',
                    'nas-dashboard': '/nas-project-data/nas-dashboard/logs/app.log',
                    'nas-dashboard-monitoring': '/nas-project-data/nas-dashboard-monitoring/logs/app.log'
                }
            else:
                log_files = {
                    'nas-dashboard': '/app/logs/app.log'
                }
            
            if system_id not in log_files:
                return {
                    'error': f'システム {system_id} が見つかりません',
                    'logs': []
                }
            
            log_file = log_files[system_id]
            if not os.path.exists(log_file):
                return {
                    'error': f'ログファイルが見つかりません: {log_file}',
                    'logs': []
                }
            
            # ログファイルを読み取り（最新1000行）
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-1000:] if len(lines) > 1000 else lines
            
            # ログを解析
            log_stats = analyze_log_patterns(recent_lines)
            
            return {
                'system_id': system_id,
                'log_file': log_file,
                'total_lines': len(recent_lines),
                'recent_logs': recent_lines[-50:],  # 最新50行
                'log_stats': log_stats,
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"ログデータ取得エラー: {e}")
        return {
            'error': str(e),
            'logs': []
        }

def analyze_log_patterns(log_lines):
    """ログパターンを分析"""
    try:
        error_count = 0
        warning_count = 0
        info_count = 0
        error_patterns = []
        warning_patterns = []
        
        for line in log_lines:
            line_lower = line.lower()
            if 'error' in line_lower or 'exception' in line_lower:
                error_count += 1
                if len(error_patterns) < 10:  # 最新10個のエラーパターンを保存
                    error_patterns.append(line.strip())
            elif 'warning' in line_lower or 'warn' in line_lower:
                warning_count += 1
                if len(warning_patterns) < 10:  # 最新10個の警告パターンを保存
                    warning_patterns.append(line.strip())
            elif 'info' in line_lower:
                info_count += 1
        
        return {
            'error_count': error_count,
            'warning_count': warning_count,
            'info_count': info_count,
            'error_patterns': error_patterns,
            'warning_patterns': warning_patterns,
            'total_lines': len(log_lines)
        }
    except Exception as e:
        logger.error(f"ログパターン分析エラー: {e}")
        return {
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'error_patterns': [],
            'warning_patterns': [],
            'total_lines': 0
        }

def create_log_analysis_prompt(analysis_data):
    """ログ分析用のプロンプトを作成"""
    system_id = analysis_data['system_id']
    analysis_type = analysis_data['analysis_type']
    log_data = analysis_data['log_data']
    
    if 'error' in log_data:
        return f"""
        あなたはログ分析専門家です。以下のログデータを分析してください。

        システム: {system_id}
        分析タイプ: {analysis_type}
        エラー: {log_data['error']}

        分析結果は以下の項目を含めてマークダウン形式で出力してください。
        1. エラーの概要と原因
        2. 推奨される対応策
        3. 予防策の提案
        """
    
    log_stats = log_data.get('log_stats', {})
    recent_logs = log_data.get('recent_logs', [])
    
    # システムタイプに応じてプロンプトを調整
    system_type = determine_system_type(system_id)
    
    if system_type == 'docker':
        # Dockerコンテナ用のプロンプト
        return f"""
        あなたはDockerコンテナログ分析専門家です。以下のDockerコンテナログデータを分析して、コンテナの健全性と問題点を評価してください。

        【絶対ルール】
        1. 提供されたログデータのみを分析してください
        2. ログに含まれていない内容について推測や推論は行わないでください
        3. fail2ban、システムログ、その他のサービスについては一切言及しないでください
        4. コンテナ名がfail2banであっても、提供されたログデータの内容のみを分析してください
        5. ログにERRORやWARNINGが含まれていない場合は、コンテナは正常に動作していると判断してください

        コンテナ名: {system_id}
        分析タイプ: {analysis_type}
        ログソース: Dockerコンテナログのみ
        総行数: {log_data.get('total_lines', 0)}

        ログ統計:
        - エラー数: {log_stats.get('error_count', 0)}
        - 警告数: {log_stats.get('warning_count', 0)}
        - 情報数: {log_stats.get('info_count', 0)}

        【実際のログデータ】
        {log_data.get('log_text', 'ログデータが取得できませんでした')}

        【重要な分析指針】
        - エラー数が0の場合、コンテナは正常に動作しています
        - 警告数が0の場合、コンテナに問題はありません
        - INFOレベルのログのみの場合は、コンテナは健全です
        - ログに記載されていない問題については推測しないでください
        - コンテナ固有の問題と解決策に焦点を当ててください

        分析結果は以下の項目を含めてマークダウン形式で出力してください。
        1. コンテナ健全性の評価（ログデータに基づく）
        2. 主要な問題点の特定（ログから確認できる問題のみ）
        3. エラーパターンの分析（ログから抽出されたパターンのみ）
        4. 推奨される対応策（ログデータに基づく具体的な対応）
        5. 予防策の提案（コンテナ固有の予防策）
        6. 監視すべき指標（ログから確認できる指標のみ）
        7. コンテナ再起動の必要性（ログデータに基づく判断）
        """
    elif system_type == 'hybrid':
        # ハイブリッドシステム用のプロンプト
        return f"""
        あなたは包括的ログ分析専門家です。以下のテキストログとDockerログの統合データを分析して、システム全体の健全性と問題点を評価してください。

        【絶対ルール】
        1. 提供されたログデータのみを分析してください
        2. ログに含まれていない内容について推測や推論は行わないでください
        3. fail2ban、システムログ、その他のサービスについては一切言及しないでください

        システム名: {system_id}
        分析タイプ: {analysis_type}
        ログソース: テキストログ + Dockerログ（統合分析）
        テキストログ利用可能: {log_data.get('text_log_available', False)}
        Dockerログ利用可能: {log_data.get('docker_log_available', False)}
        総行数: {log_data.get('total_lines', 0)}

        ログ統計:
        - エラー数: {log_stats.get('error_count', 0)}
        - 警告数: {log_stats.get('warning_count', 0)}
        - 情報数: {log_stats.get('info_count', 0)}

        【実際の統合ログデータ】
        {log_data.get('log_text', 'ログデータが取得できませんでした')}

        【重要な分析指針】
        - エラー数が0の場合、システムは正常に動作しています
        - 警告数が0の場合、システムに問題はありません
        - INFOレベルのログのみの場合は、システムは健全です
        - ログに記載されていない問題については推測しないでください
        - テキストログとDockerログの相関性に焦点を当ててください

        分析結果は以下の項目を含めてマークダウン形式で出力してください。
        1. システム全体の健全性評価
        2. テキストログとDockerログの相関分析
        3. 主要な問題点の特定
        4. エラーパターンの包括的分析
        5. 推奨される対応策
        6. 予防策の提案
        7. 監視すべき指標
        8. システム再起動の必要性
        9. ログソース別の推奨事項
        """
    else:
        # テキストログ用のプロンプト
        return f"""
        あなたはログ分析専門家です。以下のログデータを分析して、システムの健全性と問題点を評価してください。

        システム: {system_id}
        分析タイプ: {analysis_type}
        ログファイル: {log_data.get('log_file', 'N/A')}
        総行数: {log_data.get('total_lines', 0)}

        ログ統計:
        - エラー数: {log_stats.get('error_count', 0)}
        - 警告数: {log_stats.get('warning_count', 0)}
        - 情報数: {log_stats.get('info_count', 0)}

        最新のログエントリ:
        {chr(10).join(recent_logs[-20:])}

        エラーパターン:
        {chr(10).join(log_stats.get('error_patterns', [])[:5])}

        警告パターン:
        {chr(10).join(log_stats.get('warning_patterns', [])[:5])}

        分析結果は以下の項目を含めてマークダウン形式で出力してください。
        1. システム健全性の評価
        2. 主要な問題点の特定
        3. エラーパターンの分析
        4. 推奨される対応策
        5. 予防策の提案
        6. 監視すべき指標
        """

def get_fail2ban_status():
    """Fail2Banの状態を取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のFail2Ban状態を取得
            result = subprocess.run([
                'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {
                    'status': 'running',
                    'output': result.stdout,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'output': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
        else:
            # ローカル環境ではモックデータを返す
            return {
                'status': 'mock',
                'output': 'Fail2Ban is running\nJail list: sshd, nginx-http-auth',
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Fail2Ban状態取得エラー: {e}")
        return {
            'status': 'error',
            'output': str(e),
            'timestamp': datetime.now().isoformat()
        }

def get_ban_history_data():
    """BAN履歴データを取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のBAN履歴を取得
            ban_history = []
            
            # 利用可能なjailを取得
            try:
                result = subprocess.run([
                    'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    jail_lines = [line for line in result.stdout.split('\n') if 'Jail list:' in line]
                    if jail_lines:
                        available_jails = [jail.strip() for jail in jail_lines[0].split('Jail list:')[1].strip().split(',') if jail.strip()]
                        
                        # 各jailのBAN情報を取得
                        for jail in available_jails:
                            try:
                                jail_result = subprocess.run([
                                    'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status', jail
                                ], capture_output=True, text=True, timeout=10)
                                
                                if jail_result.returncode == 0:
                                    for line in jail_result.stdout.split('\n'):
                                        if 'Banned IP list:' in line:
                                            ip_line = line.split('Banned IP list:')[1].strip()
                                            if ip_line and ip_line != '':
                                                banned_ips = [ip.strip() for ip in ip_line.split() if ip.strip()]
                                                
                                                for ip in banned_ips:
                                                    ban_history.append({
                                                        'ip': ip,
                                                        'jail': jail,
                                                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                    })
                                            break
                            except Exception as e:
                                logger.warning(f"jail {jail} の情報取得エラー: {e}")
                                continue
            except Exception as e:
                logger.error(f"jail一覧取得エラー: {e}")
            
            return ban_history
        else:
            # ローカル環境ではモックデータを返す
            return [
                {'ip': '192.168.1.100', 'jail': 'sshd', 'timestamp': '2024-01-15 14:30:00'},
                {'ip': '192.168.1.101', 'jail': 'nginx-http-auth', 'timestamp': '2024-01-15 13:45:00'}
            ]
    except Exception as e:
        logger.error(f"BAN履歴取得エラー: {e}")
        return []

def analyze_security_data():
    """セキュリティデータをAIで分析"""
    try:
        logger.info("AI分析を開始します")
        if not model:
            logger.error("Gemini AIモデルが設定されていません")
            return {
                'status': 'error',
                'message': 'Gemini AIが設定されていません',
                'analysis': None
            }
        
        # Fail2Banの状態を取得
        fail2ban_status = get_fail2ban_status()
        ban_history = get_ban_history_data()
        
        # 分析用のデータを準備
        analysis_data = {
            'fail2ban_status': fail2ban_status,
            'ban_history': ban_history,
            'timestamp': datetime.now().isoformat()
        }
        
        # AI分析のプロンプトを作成
        prompt = f"""
あなたはセキュリティ専門家です。以下のFail2Banデータを分析して、セキュリティの傾向と評価、対応の必要性を分析してください。

Fail2Ban状態:
{json.dumps(fail2ban_status, ensure_ascii=False, indent=2)}

BAN履歴:
{json.dumps(ban_history, ensure_ascii=False, indent=2)}

以下の形式で分析結果を提供してください：

1. **セキュリティ傾向の分析**
   - 攻撃パターンの特徴
   - 時間帯や地域の傾向
   - 攻撃の種類と頻度

2. **リスク評価**
   - 現在のセキュリティレベル（低/中/高）
   - 主要な脅威の特定
   - 脆弱性の評価

3. **対応の必要性**
   - 即座に対応が必要な項目
   - 推奨される対策
   - 長期的なセキュリティ改善提案

4. **推奨アクション**
   - 緊急度の高い対応
   - 予防策の提案
   - 監視の強化点

分析結果は日本語で、実用的で具体的な内容にしてください。
"""
        
        # Gemini AIで分析実行（タイムアウト付き）
        logger.info("Gemini AIで分析を開始します")
        try:
            response = model.generate_content(prompt)
            analysis_result = response.text
            logger.info("Gemini AI分析が完了しました")
        except Exception as e:
            logger.error(f"Gemini AI分析エラー: {e}")
            return {
                'status': 'error',
                'message': f'AI分析でエラーが発生しました: {str(e)}',
                'analysis': None
            }
        
        return {
            'status': 'success',
            'analysis': analysis_result,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"セキュリティ分析エラー: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'analysis': None
        }

def get_ban_history_data():
    """BAN履歴データを取得（AI分析用）"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のデータを取得
            ban_history = []
            
            # 利用可能なjailを取得
            available_jails = []
            try:
                result = subprocess.run([
                    'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    jail_lines = [line for line in result.stdout.split('\n') if 'Jail list:' in line]
                    if jail_lines:
                        available_jails = [jail.strip() for jail in jail_lines[0].split('Jail list:')[1].strip().split(',') if jail.strip()]
            except Exception as e:
                logger.error(f"jail取得エラー: {e}")
            
            # 各jailのBAN情報を取得
            for jail in available_jails:
                try:
                    result = subprocess.run([
                        'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status', jail
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'Banned IP list:' in line:
                                ip_line = line.split('Banned IP list:')[1].strip()
                                if ip_line and ip_line != '':
                                    banned_ips = [ip.strip() for ip in ip_line.split() if ip.strip()]
                                    
                                    for ip in banned_ips:
                                        location = get_ip_location(ip)
                                        ban_history.append({
                                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                            'ip': ip,
                                            'jail': jail,
                                            'location': location
                                        })
                                break
                except Exception as e:
                    logger.warning(f"jail {jail} の情報取得エラー: {e}")
                    continue
            
            return ban_history[:50]  # 最新50件に制限
        else:
            # ローカル環境ではモックデータ
            return [
                {'timestamp': '2024-01-15 14:30:00', 'ip': '192.168.1.100', 'jail': 'sshd', 'location': 'Unknown'},
                {'timestamp': '2024-01-15 13:45:00', 'ip': '192.168.1.101', 'jail': 'nginx-http-auth', 'location': 'Unknown'}
            ]
    except Exception as e:
        logger.error(f"BAN履歴データ取得エラー: {e}")
        return []

@app.route('/api/logs/analysis-systems')
def get_analysis_systems():
    """AI分析可能なシステム一覧を取得（テキストログ + Dockerログ）"""
    try:
        analysis_systems = []
        
        # テキストログシステムを取得
        text_systems_response = get_text_logs()
        text_systems = text_systems_response.get_json().get('systems', [])
        
        # Dockerコンテナ名のリストを事前に取得
        docker_container_names = [container['name'] for container in get_docker_containers_for_analysis()]
        
        for system in text_systems:
            # Dockerログとの重複チェック
            docker_log_exists = system['id'] in docker_container_names
            
            if docker_log_exists:
                # テキストログとDockerログの両方が存在する場合（Docker側で処理されるためスキップ）
                continue
            else:
                # テキストログのみの場合
                analysis_systems.append({
                    'id': system['id'],
                    'name': f"{system['name']} (テキストログ)",
                    'type': 'text',
                    'total_lines': system.get('total_lines', 0),
                    'has_text_logs': True,
                    'has_docker_logs': False
                })
        
        # Dockerコンテナシステムを取得
        docker_containers = get_docker_containers_for_analysis()
        for container in docker_containers:
            # テキストログシステムと重複チェック
            text_system_exists = any(system['id'] == container['name'] for system in text_systems)
            
            if text_system_exists:
                # テキストログとDockerログの両方が存在する場合
                analysis_systems.append({
                    'id': container['name'],
                    'name': f"{container['name']} (テキストログ + Dockerログ)",
                    'type': 'hybrid',
                    'status': container.get('status', 'unknown'),
                    'has_text_logs': True,
                    'has_docker_logs': True
                })
            else:
                # Dockerログのみの場合
                analysis_systems.append({
                    'id': container['name'],
                    'name': f"{container['name']} (Dockerログ)",
                    'type': 'docker',
                    'status': container.get('status', 'unknown'),
                    'has_text_logs': False,
                    'has_docker_logs': True
                })
        
        return jsonify({
            'success': True,
            'systems': analysis_systems
        })
    except Exception as e:
        logger.error(f"分析システム一覧取得エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_docker_containers_for_analysis():
    """AI分析用のDockerコンテナ一覧を取得"""
    try:
        import subprocess
        
        # 実行中のDockerコンテナ一覧を取得
        result = subprocess.run([
            'docker', 'ps', '--format', '{{.Names}}\t{{.Status}}'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return []
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    containers.append({
                        'name': parts[0],
                        'status': parts[1]
                    })
        
        # 新しい監視システムのコンテナを追加
        monitoring_containers = [
            'nas-dashboard-monitoring-frontend-1',
            'nas-dashboard-monitoring-backend-1',
            'nas-dashboard-monitoring-postgres-1',
            'nas-dashboard-monitoring-redis-1'
        ]
        
        for container_name in monitoring_containers:
            # コンテナが存在するかチェック
            check_result = subprocess.run([
                'docker', 'ps', '-a', '--filter', f'name={container_name}', '--format', '{{.Names}}'
            ], capture_output=True, text=True, timeout=5)
            
            if check_result.returncode == 0 and container_name in check_result.stdout:
                containers.append({
                    'name': container_name,
                    'status': 'running'  # 簡易的な状態
                })
        
        return containers
    except Exception as e:
        logger.error(f"Dockerコンテナ一覧取得エラー: {e}")
        return []

def determine_system_type(system_id):
    """システムタイプを判定"""
    try:
        # テキストログファイルの存在確認
        has_text_log = False
        if os.getenv('NAS_MODE'):
            log_file_path = f'/nas-project-data/{system_id}/logs/app.log'
        else:
            log_file_path = f'./logs/{system_id}.log'
        
        if os.path.exists(log_file_path):
            has_text_log = True
        
        # Dockerコンテナの存在確認
        has_docker_log = False
        import subprocess
        result = subprocess.run([
            'docker', 'ps', '--format', '{{.Names}}'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and system_id in result.stdout:
            has_docker_log = True
        
        # システムタイプを判定
        if has_text_log and has_docker_log:
            return 'hybrid'
        elif has_text_log:
            return 'text'
        elif has_docker_log:
            return 'docker'
        else:
            return 'unknown'
    except Exception as e:
        logger.error(f"システムタイプ判定エラー: {e}")
        return 'unknown'

def get_docker_only_log_data_for_analysis(system_id):
    """Dockerのみのシステムのログデータを取得"""
    try:
        # Dockerコンテナのログを直接取得
        result = subprocess.run([
            'docker', 'logs', '--tail', '1000', system_id
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {
                'error': f'Dockerコンテナ {system_id} のログ取得に失敗しました: {result.stderr}',
                'logs': []
            }
        
        # ログをそのままテキストとして使用
        log_text = result.stdout
        log_lines = log_text.split('\n')
        
        # ログを解析（統計情報用）
        log_stats = analyze_log_patterns(log_lines)
        
        return {
            'system_id': system_id,
            'log_source': 'docker',
            'log_text': log_text,  # 生のログテキスト
            'total_lines': len(log_lines),
            'recent_logs': log_lines[-50:],  # 最新50行
            'log_stats': log_stats,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Dockerログデータ取得エラー: {e}")
        return {
            'error': str(e),
            'logs': []
        }

def get_hybrid_log_data_for_analysis(system_id):
    """ハイブリッドシステム（テキストログ + Dockerログ）のログデータを取得"""
    try:
        # テキストログを取得
        text_log_data = None
        if os.getenv('NAS_MODE') and os.path.exists('/nas-project-data'):
            log_files = {
                'meeting-minutes-byc': '/nas-project-data/meeting-minutes-byc/logs/app.log',
                'amazon-analytics': '/nas-project-data/amazon-analytics/logs/app.log',
                'document-automation': '/nas-project-data/document-automation/logs/app.log',
                'youtube-to-notion': '/nas-project-data/youtube-to-notion/logs/app.log',
                'nas-dashboard': '/nas-project-data/nas-dashboard/logs/app.log'
            }
        else:
            log_files = {
                'nas-dashboard': '/app/logs/app.log'
            }
        
        text_log_text = ""
        if system_id in log_files and os.path.exists(log_files[system_id]):
            with open(log_files[system_id], 'r', encoding='utf-8') as f:
                text_log_text = f.read()
                text_log_data = {
                    'text': text_log_text,
                    'source': 'text_file'
                }
        
        # Dockerログを取得
        docker_log_text = ""
        docker_log_data = None
        try:
            result = subprocess.run([
                'docker', 'logs', '--tail', '1000', system_id
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                docker_log_text = result.stdout
                docker_log_data = {
                    'text': docker_log_text,
                    'source': 'docker'
                }
        except Exception as e:
            logger.warning(f"Dockerログ取得エラー: {e}")
        
        # ログを統合
        combined_log_text = ""
        if text_log_text:
            combined_log_text += f"[TEXT LOGS]\n{text_log_text}\n\n"
        if docker_log_text:
            combined_log_text += f"[DOCKER LOGS]\n{docker_log_text}\n"
        
        # 統合ログを解析
        all_logs = combined_log_text.split('\n')
        log_stats = analyze_log_patterns(all_logs)
        
        return {
            'system_id': system_id,
            'log_source': 'hybrid',
            'log_text': combined_log_text,  # 統合されたログテキスト
            'text_log_available': text_log_data is not None,
            'docker_log_available': docker_log_data is not None,
            'total_lines': len(all_logs),
            'recent_logs': all_logs[-50:],  # 最新50行
            'log_stats': log_stats,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"ハイブリッドログデータ取得エラー: {e}")
        return {
            'error': str(e),
            'logs': []
        }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
