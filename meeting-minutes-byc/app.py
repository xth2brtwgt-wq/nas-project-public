#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meeting Minutes BYC - Flask Application
音声ファイルの文字起こしと議事録生成アプリケーション
"""

import os
import json
import logging
import threading
import time
from queue import Queue
from datetime import datetime
from typing import Optional

from flask import Flask, request, jsonify, render_template, send_from_directory, redirect
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import google.generativeai as genai
import sys
from pathlib import Path
from functools import wraps

# ロガーの初期化（認証モジュールのインポート前に必要）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# カスタムユーティリティのインポート（認証モジュールより前にインポート）
from utils.email_sender import EmailSender
from utils.notion_client import NotionClient
from utils.google_drive_client import GoogleDriveClient
from utils.markdown_generator import MarkdownGenerator
from utils.dictionary_manager import DictionaryManager
from utils.template_manager import TemplateManager

# 共通認証モジュールのインポート（カスタムユーティリティのインポート後）
nas_dashboard_path = Path('/nas-project/nas-dashboard')
if nas_dashboard_path.exists():
    # カスタムユーティリティの後に追加することで、パス競合を回避
    sys.path.insert(0, str(nas_dashboard_path))
    try:
        # 明示的にパスを指定してインポート
        import importlib.util
        auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
        if auth_common_path.exists():
            spec = importlib.util.spec_from_file_location("auth_common", str(auth_common_path))
            auth_common = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(auth_common)
            get_current_user_from_request = auth_common.get_current_user_from_request
            get_dashboard_login_url = auth_common.get_dashboard_login_url
            AUTH_ENABLED = True
            logger.info("認証モジュールを読み込みました")
        else:
            logger.warning(f"認証モジュールファイルが見つかりません: {auth_common_path}")
            AUTH_ENABLED = False
    except Exception as e:
        logger.warning(f"認証モジュールをインポートできませんでした（認証機能は無効化されます）: {e}")
        AUTH_ENABLED = False
else:
    logger.warning("認証モジュールのパスが見つかりません（認証機能は無効化されます）")
    AUTH_ENABLED = False

# 環境変数の読み込み
load_dotenv()

# アプリケーション情報
from config.version import APP_NAME, APP_VERSION

# サブフォルダ対応（Nginx Proxy Manager経由で /meetings でアクセスされる場合）
# 環境変数で制御可能（外部アクセス時のみ有効化）
SUBFOLDER_PATH = os.getenv('SUBFOLDER_PATH', '')

# Flask アプリケーションの初期化
# static_url_pathは通常の/staticのまま（物理パスはstatic/フォルダ）
# APPLICATION_ROOTを設定することで、url_forが自動的に/meetingsを付ける
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# APPLICATION_ROOTとSESSION_COOKIE_PATHを設定
# APPLICATION_ROOTを設定すると、url_forが自動的に/meetingsを付ける
# ただし、static_url_pathは/staticのままなので、url_for('static', ...)は/static/...を生成
# そのため、テンプレート側で手動で/meetingsを追加する必要がある
if SUBFOLDER_PATH and SUBFOLDER_PATH != '/':
    app.config['APPLICATION_ROOT'] = SUBFOLDER_PATH
    app.config['SESSION_COOKIE_PATH'] = SUBFOLDER_PATH

CORS(app)

# 認証デコレータ
def require_auth(f):
    """認証が必要なエンドポイントのデコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AUTH_ENABLED:
            # 認証が無効な場合はそのまま通す
            return f(*args, **kwargs)
        
        user = get_current_user_from_request(request)
        if not user:
            # ログインページにリダイレクト
            login_url = get_dashboard_login_url(request)
            logger.info(f"[AUTH] 認証が必要です: {request.path} -> {login_url}")
            return redirect(login_url)
        return f(*args, **kwargs)
    return decorated_function
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False, allow_unsafe_werkzeug=True)

# ログ設定（ファイルハンドラーを追加）
# NAS環境では統合データディレクトリを使用、ローカル環境では./logsを使用
if os.getenv('NAS_MODE'):
    log_dir = os.getenv('LOG_DIR', '/app/logs')
else:
    log_dir = os.getenv('LOG_DIR', './logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# サブフォルダ対応のログ出力（logger初期化後）
if SUBFOLDER_PATH and SUBFOLDER_PATH != '/':
    logger.info(f"サブフォルダ対応を有効化: APPLICATION_ROOT={SUBFOLDER_PATH}")

# 設定
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# NAS環境では統合データディレクトリを使用、ローカル環境では相対パスを使用
if os.getenv('NAS_MODE'):
    UPLOAD_FOLDER = os.getenv('UPLOAD_DIR', '/app/uploads')
    TRANSCRIPT_FOLDER = os.getenv('TRANSCRIPT_DIR', '/app/transcripts')
else:
    UPLOAD_FOLDER = os.getenv('UPLOAD_DIR', './uploads')
    TRANSCRIPT_FOLDER = os.getenv('TRANSCRIPT_DIR', './transcripts')
DEFAULT_EMAIL = os.getenv('EMAIL_TO', 'nas.system.0828@gmail.com')
TEMPLATES_FOLDER = os.getenv('TEMPLATES_DIR', './templates')
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg', 'webm'}

# メール送信の重複防止に関する定数（マジックナンバー回避のため定数化）
EMAIL_DEDUPE_WINDOW_SECONDS = int(os.getenv('EMAIL_DEDUPE_WINDOW_SECONDS', '600'))  # 既定: 10分
EMAIL_LOCK_DIR = os.path.join(TRANSCRIPT_FOLDER, '.email_locks')
os.makedirs(EMAIL_LOCK_DIR, exist_ok=True)

# アップロード処理の重複防止に関する定数
UPLOAD_DEDUPE_WINDOW_SECONDS = int(os.getenv('UPLOAD_DEDUPE_WINDOW_SECONDS', '60'))  # 既定: 60秒
UPLOAD_LOCK_DIR = os.path.join(TRANSCRIPT_FOLDER, '.upload_locks')
os.makedirs(UPLOAD_LOCK_DIR, exist_ok=True)

# ディレクトリの作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)
os.makedirs(TEMPLATES_FOLDER, exist_ok=True)

# メール送信の非同期処理
email_queue = Queue()
email_status_tracker = {}

# カスタム辞書マネージャーの初期化
dictionary_manager = DictionaryManager()

# テンプレートマネージャーの初期化
template_manager = TemplateManager()

# メールワーカーの多重起動防止フラグ
EMAIL_THREAD_STARTED = False

def _should_start_email_worker() -> bool:
    """メール送信ワーカーを起動すべきか判定する。
    - 開発サーバのリロードで二重起動しないように WERKZEUG_RUN_MAIN を考慮
    - FLASK_DEBUG=True の場合はリロード子プロセスのみで起動
    """
    # 明示的に有効化したい場合の環境変数（将来拡張用）
    enable_env = os.getenv('ENABLE_EMAIL_WORKER')
    if enable_env is not None:
        return enable_env.lower() in ('1', 'true', 'yes')

    werkzeug_run_main = os.getenv('WERKZEUG_RUN_MAIN', 'false').lower() == 'true'
    flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Debug時はリロード後の子プロセス（WERKZEUG_RUN_MAIN=true）のみ起動
    if flask_debug:
        return werkzeug_run_main

    # 非Debug時は通常通り起動
    return True

def _get_email_dedupe_key(to_email: str, meeting_data: dict) -> str:
    """メール送信の重複を判定するためのキーを生成。
    ファイル名（ユニークタイムスタンプ含む）と宛先でキー化する。
    """
    filename = meeting_data.get('filename', 'unknown')
    return f"{to_email}__{filename}"

def _get_lock_path(key: str) -> str:
    return os.path.join(EMAIL_LOCK_DIR, f"{key}.lock")

def _is_recently_locked(key: str, window_seconds: int = EMAIL_DEDUPE_WINDOW_SECONDS) -> bool:
    """ロックファイルが存在し、TTL内なら重複と見なす。"""
    path = _get_lock_path(key)
    if not os.path.exists(path):
        return False
    try:
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        now = datetime.now()
        delta = (now - mtime).total_seconds()
        return delta <= window_seconds
    except Exception:
        # 取得失敗時は重複とは見なさない
        return False

def _touch_lock(key: str) -> None:
    """ロックファイルを更新（作成/更新）する。"""
    path = _get_lock_path(key)
    try:
        with open(path, 'a', encoding='utf-8'):
            pass
        # mtime更新
        os.utime(path, None)
    except Exception as e:
        logger.warning(f'メール重複ロックの作成/更新に失敗しました: {str(e)}')

def _get_upload_lock_path(filename: str) -> str:
    """アップロード処理のロックファイルパスを取得"""
    return os.path.join(UPLOAD_LOCK_DIR, f"{filename}.lock")

def _is_upload_processing(filename: str) -> bool:
    """アップロード処理が進行中かチェック"""
    path = _get_upload_lock_path(filename)
    if not os.path.exists(path):
        return False
    try:
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        now = datetime.now()
        delta = (now - mtime).total_seconds()
        # タイムアウトを超えている場合は古いロックファイルとして削除
        if delta > UPLOAD_DEDUPE_WINDOW_SECONDS:
            logger.warning(f'古いロックファイルを削除: {filename} (経過時間: {delta:.1f}秒)')
            try:
                os.remove(path)
            except Exception as e:
                logger.warning(f'ロックファイル削除に失敗: {str(e)}')
            return False
        return True
    except Exception:
        # 取得失敗時は処理中と見なさない
        return False

def _create_upload_lock(filename: str) -> None:
    """アップロード処理のロックファイルを作成"""
    path = _get_upload_lock_path(filename)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(datetime.now().isoformat())
    except Exception as e:
        logger.warning(f'アップロードロックの作成に失敗しました: {str(e)}')

def _remove_upload_lock(filename: str) -> None:
    """アップロード処理のロックファイルを削除"""
    path = _get_upload_lock_path(filename)
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.warning(f'アップロードロックの削除に失敗しました: {str(e)}')

def send_email_async(email_data):
    """バックグラウンドでメール送信"""
    session_id = email_data.get('session_id', 'default')
    original_filepath = email_data.get('original_filepath')  # 元のアップロードファイルパス
    
    try:
        # 重複送信の簡易デデュープ（ロックファイル + TTL）
        to_email = email_data.get('to_email', '')
        meeting_data = email_data.get('meeting_data', {})
        dedupe_key = _get_email_dedupe_key(to_email, meeting_data)
        if _is_recently_locked(dedupe_key):
            # 既に同一キーで最近送信済みと判断。ユーザー体験上は「送信完了」として扱う。
            logger.info(f"重複検知によりメール送信をスキップ: {to_email} ({dedupe_key})")
            email_status_tracker['last_email_status'] = True
            email_status_tracker['last_email_error'] = ''
            emit_email_status_update(session_id, 'sent', 'メールはすでに送信済み（重複検知によりスキップ）', {'to_email': to_email})
            # 元ファイル削除は通常フローに合わせて実施
            if original_filepath and os.path.exists(original_filepath):
                try:
                    os.remove(original_filepath)
                    logger.info(f'元ファイル削除完了: {original_filepath}')
                except OSError as e:
                    logger.warning(f'元ファイル削除失敗: {str(e)}')
            return

        # 送信直前にロックを作成（並行実行での競合も一定程度回避）
        _touch_lock(dedupe_key)

        # WebSocket更新: メール送信開始
        emit_email_status_update(session_id, 'sending', 'メール送信中...', {'to_email': email_data['to_email']})
        
        email_sender = EmailSender()
        email_sender.send_meeting_minutes(
            email_data['to_email'],
            email_data['meeting_data'],
            email_data['transcript_file_path'],
            email_data['meeting_file_path']
        )
        
        # 送信成功を記録
        email_status_tracker['last_email_status'] = True
        email_status_tracker['last_email_error'] = ''
        logger.info(f"メール送信完了: {email_data['to_email']}")
        
        # WebSocket更新: メール送信完了
        emit_email_status_update(session_id, 'sent', 'メール送信完了', {'to_email': email_data['to_email']})
        
        # メール送信完了後に元のアップロードファイルを削除
        if original_filepath and os.path.exists(original_filepath):
            try:
                os.remove(original_filepath)
                logger.info(f'元ファイル削除完了: {original_filepath}')
            except OSError as e:
                logger.warning(f'元ファイル削除失敗: {str(e)}')
        
    except Exception as e:
        # 送信失敗を記録
        email_status_tracker['last_email_status'] = False
        email_status_tracker['last_email_error'] = str(e)
        logger.error(f"メール送信エラー: {str(e)}")
        
        # WebSocket更新: メール送信エラー
        emit_email_status_update(session_id, 'error', f'メール送信エラー: {str(e)}', {'to_email': email_data['to_email']})
        
        # エラー時も元のアップロードファイルを削除
        if original_filepath and os.path.exists(original_filepath):
            try:
                os.remove(original_filepath)
                logger.info(f'エラー時の元ファイル削除完了: {original_filepath}')
            except OSError as e:
                logger.warning(f'エラー時の元ファイル削除失敗: {str(e)}')

def process_email_queue():
    """メール送信キューを処理"""
    while True:
        try:
            email_data = email_queue.get()
            if email_data is None:
                break
            send_email_async(email_data)
            email_queue.task_done()
        except Exception as e:
            logger.error(f"メールキュー処理エラー: {str(e)}")

# バックグラウンドスレッドを開始（多重起動防止ガード）
if _should_start_email_worker() and not EMAIL_THREAD_STARTED:
    email_thread = threading.Thread(target=process_email_queue, daemon=True)
    email_thread.start()
    EMAIL_THREAD_STARTED = True
    logger.info("メール送信の非同期処理を開始しました")

# Gemini AI の設定
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    logger.info('Gemini AI configured successfully')
else:
    logger.warning('GEMINI_API_KEY not found')
    model = None

# ユーティリティクラスの初期化
email_sender = EmailSender()
notion_client = NotionClient()
google_drive_client = GoogleDriveClient()
markdown_generator = MarkdownGenerator()

# WebSocketイベントハンドラー
@socketio.on('connect')
def handle_connect():
    """クライアント接続時の処理"""
    logger.info(f'クライアントが接続しました: {request.sid}')
    # 自動的にデフォルトルームに参加
    join_room('default')
    logger.info(f'クライアント {request.sid} をデフォルトルームに参加させました')
    emit('connected', {'message': 'WebSocket接続が確立されました'})

@socketio.on('disconnect')
def handle_disconnect():
    """クライアント切断時の処理"""
    logger.info(f'クライアントが切断しました: {request.sid}')

@socketio.on('join_room')
def handle_join_room(data):
    """ルーム参加処理"""
    room = data.get('room', 'default')
    join_room(room)
    emit('joined_room', {'room': room, 'message': f'ルーム {room} に参加しました'})

def emit_progress_update(room, step, message, progress_percent=None, data=None):
    """進捗更新をクライアントに送信"""
    if socketio is None:
        logger.info(f'WebSocket無効化: 進捗更新をスキップ [{room}]: {step} - {message}')
        return
    
    update_data = {
        'step': step,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'progress_percent': progress_percent,
        'data': data
    }
    logger.info(f'進捗更新送信準備 [{room}]: {step} - {message} - データ: {update_data}')
    socketio.emit('progress_update', update_data, room=room)
    logger.info(f'進捗更新送信完了 [{room}]: {step} - {message}')

def emit_email_status_update(room, status, message, data=None):
    """メール送信状況更新をクライアントに送信"""
    if socketio is None:
        logger.info(f'WebSocket無効化: メール状況更新をスキップ [{room}]: {status} - {message}')
        return
    
    update_data = {
        'status': status,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    socketio.emit('email_status_update', update_data, room=room)
    logger.info(f'メール状況更新送信 [{room}]: {status} - {message}')


def allowed_file(filename):
    """ファイル拡張子のチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """ユニークなファイル名を生成"""
    import uuid
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # ミリ秒とUUID（短縮版）を追加してよりユニークにする
    microsecond = datetime.now().microsecond // 1000  # ミリ秒
    unique_id = str(uuid.uuid4())[:8]  # UUIDの最初の8文字
    name, ext = os.path.splitext(filename)
    return f"{name}_{timestamp}_{microsecond:03d}_{unique_id}{ext}"


# エラークラス定義
class TranscriptionError(Exception):
    """文字起こしエラーの基底クラス"""
    pass


class RetryableError(TranscriptionError):
    """再試行可能なエラー"""
    def __init__(self, message, error_type="unknown", original_error=None):
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error


class NonRetryableError(TranscriptionError):
    """再試行不可能なエラー"""
    def __init__(self, message, error_type="unknown", original_error=None):
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error


def classify_error(error):
    """エラーを分類してRetryableErrorまたはNonRetryableErrorを返す
    
    Args:
        error: 発生した例外
        
    Returns:
        RetryableErrorまたはNonRetryableError
    """
    error_message = str(error).lower()
    error_type_str = type(error).__name__
    
    # タイムアウトエラー（再試行可能）
    if any(keyword in error_message for keyword in ['timeout', 'timed out', 'タイムアウト', 'time out']):
        return RetryableError(
            f"タイムアウトエラー: {str(error)}",
            error_type="timeout",
            original_error=error
        )
    
    # レート制限エラー（再試行可能）
    if any(keyword in error_message for keyword in ['rate limit', 'quota', '429', 'レート制限', 'クォータ']):
        return RetryableError(
            f"レート制限エラー: {str(error)}",
            error_type="rate_limit",
            original_error=error
        )
    
    # ネットワークエラー（再試行可能）
    if any(keyword in error_message for keyword in ['connection', 'network', 'dns', 'ネットワーク', '接続']):
        return RetryableError(
            f"ネットワークエラー: {str(error)}",
            error_type="network",
            original_error=error
        )
    
    # サーバーエラー（5xx系、再試行可能）
    if any(keyword in error_message for keyword in ['500', '502', '503', '504', '50x', 'server error', 'サーバーエラー']):
        return RetryableError(
            f"サーバーエラー: {str(error)}",
            error_type="server_error",
            original_error=error
        )
    
    # APIキーエラー（再試行不可能）
    if any(keyword in error_message for keyword in ['api key', 'authentication', 'unauthorized', '401', '403', '認証', 'APIキー']):
        return NonRetryableError(
            f"認証エラー: {str(error)}",
            error_type="authentication",
            original_error=error
        )
    
    # ファイル形式エラー（再試行不可能）
    if any(keyword in error_message for keyword in ['format', 'mime type', 'unsupported', '形式', 'ファイル形式']):
        return NonRetryableError(
            f"ファイル形式エラー: {str(error)}",
            error_type="file_format",
            original_error=error
        )
    
    # ファイルサイズエラー（再試行不可能）
    if any(keyword in error_message for keyword in ['file size', 'too large', 'size limit', 'ファイルサイズ', 'サイズ制限']):
        return NonRetryableError(
            f"ファイルサイズエラー: {str(error)}",
            error_type="file_size",
            original_error=error
        )
    
    # その他のエラーはデフォルトで再試行可能とする（保守的なアプローチ）
    return RetryableError(
        f"エラー: {str(error)}",
        error_type="unknown",
        original_error=error
    )


def _transcribe_audio_single_attempt(file_path, participants):
    """1回の文字起こし試行を実行
    
    Args:
        file_path: 音声ファイルのパス
        participants: 参加者名（カンマ区切りまたは改行区切り）
    
    Returns:
        文字起こし結果のテキスト
        
    Raises:
        Exception: 文字起こしに失敗した場合
    """
    if not model:
        raise NonRetryableError("Gemini AI model not configured", error_type="configuration")
    
    # 音声ファイルを読み込み
    try:
        with open(file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
    except IOError as e:
        raise NonRetryableError(f"ファイル読み込みエラー: {str(e)}", error_type="file_read", original_error=e)
    
    # ファイル形式の判定
    file_ext = os.path.splitext(file_path)[1].lower()
    mime_type_map = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mp3',
        '.m4a': 'audio/mp4',
        '.flac': 'audio/flac',
        '.ogg': 'audio/ogg',
        '.webm': 'audio/webm'
    }
    mime_type = mime_type_map.get(file_ext, 'audio/wav')
    
    # カスタム辞書情報を取得
    dictionary_info = dictionary_manager.get_dictionary_for_prompt()
    
    # 参加者情報の整形
    participants_text = ""
    if participants and participants.strip():
        # カンマ区切りまたは改行区切りの参加者名を整形
        participants_list = [p.strip() for p in participants.replace('\n', ',').split(',') if p.strip()]
        if participants_list:
            participants_text = f"""
### 会議参加者
以下の参加者が会議に参加しています。可能な限り、これらの名前を使用して話者を識別してください：
{', '.join(participants_list)}

**注意**: 参加者名が音声で明確に聞き取れない場合は、音声の特徴（声のトーン、話し方など）から推測して、最も適切と思われる参加者名を割り当ててください。判断が難しい場合は「話者1」「話者2」などの形式を使用してください。
"""
    else:
        participants_text = """
### 会議参加者
参加者情報が提供されていません。音声の特徴（声のトーン、話し方など）から話者を識別し、「話者1」「話者2」などの形式で区別してください。
"""
    
    # Gemini AI に送信するためのプロンプト（構造化）
    prompt = f"""## 音声文字起こしタスク

### 目的
会議音声を正確に文字起こしし、後続の議事録生成に使用するテキストを生成します。

### 会議情報
- **言語**: 日本語
- **用途**: 議事録作成用の詳細な文字起こし
{participants_text}
### カスタム辞書
{dictionary_info}

### 出力要件

1. **話者識別**
   - 参加者名が指定されている場合は、可能な限りその名前を使用してください
   - 音声の特徴から話者を識別し、一貫性を保ってください
   - 参加者名が未指定の場合は「話者1」「話者2」などの形式を使用してください

2. **発話の区切り**
   - 話者ごとの発話間を明確に区切ってください
   - 短い発話（「はい」「了解です」など）も見逃さず記録してください
   - 発話の開始時刻を正確に記録してください

3. **時刻表記**
   - 各発話の開始時刻を [HH:MM:SS] 形式で記録してください
   - 時刻は音声ファイルの開始時点を 00:00:00 として計算してください

4. **正確性**
   - カスタム辞書に記載されている用語は、必ず指定された正しい表記で文字起こししてください
   - 技術用語や固有名詞は特に注意深く聞き取り、正確に文字起こししてください
   - 不明な用語がある場合は、音声に最も近い表記を推測して記載してください

5. **同時発話・重なりの処理**
   - 同時発話や重なりがある場合は、可能な限り両方の内容を記録してください
   - 形式: [時刻] 話者A / 話者B: [それぞれの発言内容]

6. **不明瞭な音声**
   - 聞き取りが困難な部分は「[聞き取り不能]」または「[不明瞭]」と明記してください
   - 推測が含まれる場合は「[推測: 内容]」と明記してください

### 出力形式
[時刻] 話者名: 発言内容

### 出力例
[00:00:00] 田中: それでは、本日の会議を開始いたします
[00:00:15] 佐藤: よろしくお願いします
[00:00:20] 田中: 本日の議題は、新プロジェクトの進捗状況についてです
[00:00:35] 佐藤: ありがとうございます。プロジェクトの現状について説明させていただきます
[00:01:00] 田中 / 佐藤: [田中: 了解です] [佐藤: それでは説明します]

### 注意事項
- カスタム辞書に記載されている用語は、必ず指定された正しい表記で文字起こししてください
- 技術用語や固有名詞は特に注意深く聞き取り、正確に文字起こししてください
- 同時発話や重なりがある場合は、可能な限り両方の内容を記録してください
- 不明瞭な音声部分は「[聞き取り不能]」または「[不明瞭]」と明記してください
- 推測を含む場合は「[推測: 内容]」と明記してください
- 話者識別に迷う場合は、音声の特徴や文脈から最適と思われる話者名を割り当ててください
"""
    
    # Gemini AI に送信
    try:
        response = model.generate_content([
            prompt,
            {
                "mime_type": mime_type,
                "data": audio_data
            }
        ])
        
        if not response or not response.text:
            raise Exception("空のレスポンスが返されました")
        
        return response.text
        
    except Exception as e:
        # エラーを分類して再スロー
        classified_error = classify_error(e)
        raise classified_error


def transcribe_audio_with_gemini(file_path, participants="", max_retries=3):
    """Gemini AI を使用して音声を文字起こし（再試行ロジック付き）
    
    Args:
        file_path: 音声ファイルのパス
        participants: 参加者名（カンマ区切りまたは改行区切り）
        max_retries: 最大再試行回数（デフォルト: 3）
    
    Returns:
        文字起こし結果のテキスト
        
    Raises:
        NonRetryableError: 再試行不可能なエラーの場合
        RetryableError: 最大再試行回数を超えた場合
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # 再試行の場合はログに記録
            if attempt > 0:
                wait_time = min(2 ** attempt, 60)  # 指数バックオフ（最大60秒）
                logger.info(f"文字起こし再試行 {attempt}/{max_retries-1} (待機時間: {wait_time}秒)")
                time.sleep(wait_time)
            
            # 文字起こしを実行
            return _transcribe_audio_single_attempt(file_path, participants)
            
        except NonRetryableError as e:
            # 再試行不可能なエラーは即座に失敗
            logger.error(f"文字起こしエラー（再試行不可）: {e.error_type} - {str(e)}")
            raise
        
        except RetryableError as e:
            last_error = e
            logger.warning(f"文字起こしエラー（再試行可能）: {e.error_type} - {str(e)} (試行 {attempt + 1}/{max_retries})")
            
            # 最後の試行の場合はエラーを再スロー
            if attempt == max_retries - 1:
                logger.error(f"文字起こしに失敗しました（最大再試行回数に達しました）: {e.error_type} - {str(e)}")
                raise RetryableError(
                    f"文字起こしに失敗しました（{max_retries}回試行しました）: {str(e)}",
                    error_type=e.error_type,
                    original_error=e.original_error
                )
        
        except Exception as e:
            # 予期しないエラーも分類して処理
            classified_error = classify_error(e)
            last_error = classified_error
            
            if isinstance(classified_error, NonRetryableError):
                logger.error(f"文字起こしエラー（再試行不可）: {classified_error.error_type} - {str(classified_error)}")
                raise classified_error
            else:
                logger.warning(f"文字起こしエラー（再試行可能）: {classified_error.error_type} - {str(classified_error)} (試行 {attempt + 1}/{max_retries})")
                
                # 最後の試行の場合はエラーを再スロー
                if attempt == max_retries - 1:
                    logger.error(f"文字起こしに失敗しました（最大再試行回数に達しました）: {classified_error.error_type} - {str(classified_error)}")
                    raise classified_error
    
    # ここに到達することはないが、念のため
    if last_error:
        raise last_error
    else:
        raise Exception("文字起こしに失敗しました（未知のエラー）")


def _format_datetime_for_gemini(datetime_str):
    """日時文字列をYYYY/MM/DD HH24:Mi形式に変換"""
    if not datetime_str or datetime_str == '未設定':
        return '[日時]'
    
    try:
        # ISO形式の日時をパース
        if 'T' in datetime_str:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        else:
            # その他の形式を試行
            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        
        # YYYY/MM/DD HH24:Mi形式に変換
        return dt.strftime('%Y/%m/%d %H:%M')
    except ValueError:
        # パースできない場合は元の文字列を返す
        return datetime_str


def generate_meeting_notes_with_gemini(transcript, conditions="", meeting_date="", template_id=None, participants=""):
    """Gemini AI を使用して議事録を生成"""
    try:
        if not model:
            raise Exception("Gemini AI model not configured")
        
        # テンプレートIDが指定されていない場合はデフォルトを使用
        if not template_id:
            template_id = template_manager.get_default_template_id()
        
        # テンプレートを使用してプロンプトを生成
        prompt = template_manager.generate_meeting_notes_with_template(
            template_id, transcript, conditions, meeting_date, participants
        )
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Meeting notes generation error: {str(e)}")
        raise Exception(f"議事録生成に失敗しました: {str(e)}")


@app.route('/')
@require_auth
def index():
    """メインページ"""
    return render_template('index.html', 
                         app_name=APP_NAME, 
                         app_version=APP_VERSION,
                         default_email=DEFAULT_EMAIL,
                         subfolder_path=SUBFOLDER_PATH)


@app.route('/history')
@require_auth
def get_history():
    """履歴取得"""
    try:
        # 履歴ファイルの一覧を取得
        history_files = []
        if os.path.exists(TRANSCRIPT_FOLDER):
            for filename in os.listdir(TRANSCRIPT_FOLDER):
                if filename.endswith('.json'):
                    filepath = os.path.join(TRANSCRIPT_FOLDER, filename)
                    stat = os.stat(filepath)
                    history_files.append({
                        'filename': filename,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'size': stat.st_size
                    })
        
        # 作成日時でソート（新しい順）
        history_files.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'history': history_files
        })
    except Exception as e:
        logger.error(f"履歴取得エラー: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/health')
def health_check():
    """ヘルスチェック"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'gemini_configured': model is not None,
        'flask_version': '3.1.2'
    })


@app.route('/test-notion')
def test_notion():
    """Notion接続テスト"""
    try:
        success, message = notion_client.test_connection()
        return jsonify({
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Notion接続テストエラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/dictionary', methods=['GET'])
def get_dictionary():
    """辞書情報を取得"""
    try:
        entries = dictionary_manager.get_all_entries()
        statistics = dictionary_manager.get_statistics()
        
        return jsonify({
            'success': True,
            'entries': entries,
            'statistics': statistics,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"辞書取得エラー: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'辞書取得エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/dictionary/search', methods=['GET'])
def search_dictionary():
    """辞書を検索"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                'success': False,
                'message': '検索クエリが指定されていません',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        results = dictionary_manager.search_entries(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"辞書検索エラー: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'辞書検索エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/dictionary/entry', methods=['POST'])
def add_dictionary_entry():
    """辞書エントリを追加"""
    try:
        data = request.get_json()
        category = data.get('category', '')
        japanese = data.get('japanese', '')
        correct_form = data.get('correct_form', '')
        
        if not all([category, japanese, correct_form]):
            return jsonify({
                'success': False,
                'message': 'カテゴリ、日本語表記、正しい表記は必須です',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        success = dictionary_manager.add_entry(category, japanese, correct_form)
        
        if success:
            return jsonify({
                'success': True,
                'message': '辞書エントリを追加しました',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': '辞書エントリの追加に失敗しました',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"辞書エントリ追加エラー: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'辞書エントリ追加エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/dictionary/entry', methods=['DELETE'])
def remove_dictionary_entry():
    """辞書エントリを削除"""
    try:
        data = request.get_json()
        category = data.get('category', '')
        japanese = data.get('japanese', '')
        
        if not all([category, japanese]):
            return jsonify({
                'success': False,
                'message': 'カテゴリと日本語表記は必須です',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        success = dictionary_manager.remove_entry(category, japanese)
        
        if success:
            return jsonify({
                'success': True,
                'message': '辞書エントリを削除しました',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': '辞書エントリの削除に失敗しました',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"辞書エントリ削除エラー: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'辞書エントリ削除エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


# テンプレート管理API
@app.route('/api/templates', methods=['GET'])
def get_templates():
    """テンプレート一覧を取得"""
    try:
        templates = template_manager.get_template_list()
        default_template_id = template_manager.get_default_template_id()
        
        return jsonify({
            'success': True,
            'templates': templates,
            'default_template_id': default_template_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"テンプレート取得エラー: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'テンプレート取得エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/templates/<template_id>', methods=['GET'])
def get_template(template_id):
    """指定されたテンプレートを取得"""
    try:
        template = template_manager.get_template(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'message': 'テンプレートが見つかりません',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        return jsonify({
            'success': True,
            'template': template,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"テンプレート取得エラー: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'テンプレート取得エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/templates', methods=['POST'])
def add_template():
    """カスタムテンプレートを追加"""
    try:
        data = request.get_json()
        template_id = data.get('id', '')
        name = data.get('name', '')
        description = data.get('description', '')
        prompt_template = data.get('prompt_template', '')
        
        if not all([template_id, name, prompt_template]):
            return jsonify({
                'success': False,
                'message': 'ID、名前、プロンプトテンプレートは必須です',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        success = template_manager.add_custom_template(template_id, name, description, prompt_template)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'テンプレートを追加しました',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'テンプレートの追加に失敗しました',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"テンプレート追加エラー: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'テンプレート追加エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    """テンプレートを更新"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        prompt_template = data.get('prompt_template')
        
        success = template_manager.update_template(template_id, name, description, prompt_template)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'テンプレートを更新しました',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'テンプレートの更新に失敗しました',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"テンプレート更新エラー: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'テンプレート更新エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """テンプレートを削除"""
    try:
        success = template_manager.delete_template(template_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'テンプレートを削除しました',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'テンプレートの削除に失敗しました',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"テンプレート削除エラー: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'テンプレート削除エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/templates/<template_id>/default', methods=['POST'])
def set_default_template(template_id):
    """デフォルトテンプレートを設定"""
    try:
        success = template_manager.set_default_template(template_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'デフォルトテンプレートを設定しました',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'デフォルトテンプレートの設定に失敗しました',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"デフォルトテンプレート設定エラー: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'デフォルトテンプレート設定エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    """音声ファイルのアップロードと処理"""
    try:
        # セッションIDをルームとして使用（WebSocketのセッションIDを取得）
        session_id = 'default'  # 全クライアントに送信
        
        # ファイルのチェック
        if 'audio' not in request.files:
            return jsonify({'error': '音声ファイルが選択されていません'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'サポートされていないファイル形式です'}), 400
        
        # 追加パラメータの取得
        meeting_date = request.form.get('meeting_date', '')
        participants = request.form.get('participants', '')
        conditions = request.form.get('conditions', '')
        email = request.form.get('email', '')
        send_to_notion = request.form.get('send_to_notion', 'false').lower() == 'true'
        save_to_google_drive = request.form.get('save_to_obsidian', 'false').lower() == 'true'  # フロントエンドのチェックボックス名はsave_to_obsidianのまま
        template_id = request.form.get('template_id', '')
        
        # ファイルの保存
        filename = generate_unique_filename(secure_filename(file.filename))
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # 重複実行防止: 同じファイル名で処理中かチェック
        if _is_upload_processing(filename):
            logger.warning(f'重複実行を検出: {filename} は既に処理中です')
            return jsonify({'error': 'このファイルは既に処理中です。しばらく待ってから再度お試しください。'}), 409
        
        # ロックファイルを作成（処理開始）
        _create_upload_lock(filename)
        
        try:
            file.save(filepath)
        except Exception as e:
            # ファイル保存に失敗した場合はロックを削除
            _remove_upload_lock(filename)
            raise
        
        # ファイルサイズを取得（削除前に取得）
        file_size = os.path.getsize(filepath)
        
        logger.info(f'ファイルをアップロードしました: {filename}')
        
        # 進捗更新: ファイルアップロード完了
        emit_progress_update(session_id, 'file_upload', 'ファイルアップロード完了', 10, {'filename': filename})
        
        # 進捗更新: 文字起こし開始
        emit_progress_update(session_id, 'transcription', '音声文字起こしを開始しています...', 20)
        
        # 文字起こし（参加者情報を渡す、再試行ロジック付き）
        try:
            transcript = transcribe_audio_with_gemini(filepath, participants)
        except NonRetryableError as e:
            # 再試行不可能なエラー（認証エラー、ファイル形式エラーなど）
            logger.error(f"文字起こしエラー（再試行不可）: {e.error_type} - {str(e)}")
            _remove_upload_lock(filename)
            
            # エラー進捗更新を送信
            error_message = f"文字起こしに失敗しました: {str(e)}"
            if e.error_type == "authentication":
                error_message = "認証エラーが発生しました。APIキーの設定を確認してください。"
            elif e.error_type == "file_format":
                error_message = "ファイル形式エラーが発生しました。対応形式を確認してください。"
            elif e.error_type == "file_size":
                error_message = "ファイルサイズエラーが発生しました。ファイルサイズを確認してください。"
            
            emit_progress_update(session_id, 'transcription_error', error_message, 20, {
                'error_type': e.error_type,
                'error': str(e)
            })
            
            return jsonify({
                'error': error_message,
                'error_type': e.error_type
            }), 400
        except RetryableError as e:
            # 再試行後も失敗したエラー
            logger.error(f"文字起こしエラー（再試行後も失敗）: {e.error_type} - {str(e)}")
            _remove_upload_lock(filename)
            
            # エラー進捗更新を送信
            error_message = f"文字起こしに失敗しました（{e.error_type}）: {str(e)}"
            if e.error_type == "timeout":
                error_message = "タイムアウトエラーが発生しました。ファイルが大きすぎる可能性があります。しばらく待ってから再度お試しください。"
            elif e.error_type == "rate_limit":
                error_message = "レート制限エラーが発生しました。しばらく待ってから再度お試しください。"
            elif e.error_type == "network":
                error_message = "ネットワークエラーが発生しました。接続を確認してから再度お試しください。"
            elif e.error_type == "server_error":
                error_message = "サーバーエラーが発生しました。しばらく待ってから再度お試しください。"
            
            emit_progress_update(session_id, 'transcription_error', error_message, 20, {
                'error_type': e.error_type,
                'error': str(e)
            })
            
            return jsonify({
                'error': error_message,
                'error_type': e.error_type
            }), 500
        except TranscriptionError as e:
            # その他の文字起こしエラー
            logger.error(f"文字起こしエラー: {str(e)}")
            _remove_upload_lock(filename)
            
            # エラー進捗更新を送信
            emit_progress_update(session_id, 'transcription_error', f"文字起こしに失敗しました: {str(e)}", 20, {
                'error': str(e)
            })
            
            return jsonify({
                'error': f"文字起こしに失敗しました: {str(e)}"
            }), 500
        
        # 進捗更新: 文字起こし完了
        emit_progress_update(session_id, 'transcription_complete', '音声文字起こし完了', 40, {'transcript_length': len(transcript)})
        
        # 進捗更新: 議事録生成開始
        emit_progress_update(session_id, 'meeting_notes', '議事録を生成しています...', 50)
        
        # 議事録生成
        meeting_notes = generate_meeting_notes_with_gemini(transcript, conditions, meeting_date, template_id, participants)
        
        # 進捗更新: 議事録生成完了
        emit_progress_update(session_id, 'meeting_notes_complete', '議事録生成完了', 60, {'notes_length': len(meeting_notes)})
        
        # 結果の保存
        result = {
            'filename': filename,
            'transcript': transcript,
            'meeting_notes': meeting_notes,
            'meeting_date': meeting_date,
            'participants': participants,
            'conditions': conditions,
            'template_id': template_id,
            'timestamp': datetime.now().isoformat(),
            'file_size': file_size
        }
        
        result_file = os.path.join(TRANSCRIPT_FOLDER, f'{filename}.json')
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 進捗更新: ファイル生成開始
        emit_progress_update(session_id, 'file_generation', 'ファイルを生成しています...', 70)
        
        # ファイルの生成
        md_filepath = markdown_generator.generate_meeting_markdown(result)
        transcript_filepath = markdown_generator.generate_transcript_file(result)
        
        # 進捗更新: ファイル生成完了
        emit_progress_update(session_id, 'file_generation_complete', 'ファイル生成完了', 80)
        
        # Notion登録(メール送信前に実行)
        if send_to_notion:
            try:
                # 進捗更新: Notion登録開始
                emit_progress_update(session_id, 'notion_upload', 'Notionに登録しています...', 85)
                
                notion_page_id = notion_client.create_meeting_page(result)
                result['notion_page_id'] = notion_page_id
                result['notion_sent'] = True
                logger.info(f'Notion登録完了: {notion_page_id}')
                
                # 進捗更新: Notion登録完了
                emit_progress_update(session_id, 'notion_upload_complete', 'Notion登録完了', 90, {'page_id': notion_page_id})
            except Exception as e:
                logger.error(f'Notion登録エラー: {str(e)}')
                result['notion_sent'] = False
                result['notion_error'] = str(e)
                
                # 進捗更新: Notion登録エラー
                emit_progress_update(session_id, 'notion_upload_error', f'Notion登録エラー: {str(e)}', 90)
        else:
            result['notion_sent'] = False
            result['notion_page_id'] = None
        
        # Google Drive保存（議事録のみ、Obsidian Vault用）
        if save_to_google_drive:
            try:
                # 進捗更新: Google Drive保存開始
                emit_progress_update(session_id, 'google_drive_upload', 'Google Drive（Obsidian Vault）に保存しています...', 88)
                
                google_drive_file_id = google_drive_client.save_meeting_file(result, md_filepath)
                if google_drive_file_id:
                    result['google_drive_file_id'] = google_drive_file_id
                    result['obsidian_saved'] = True  # フロントエンドとの互換性のため
                    logger.info(f'Google Drive（Obsidian Vault）保存完了: {google_drive_file_id}')
                    
                    # 進捗更新: Google Drive保存完了
                    emit_progress_update(session_id, 'google_drive_upload_complete', 'Google Drive（Obsidian Vault）保存完了', 89, {'file_id': google_drive_file_id})
                else:
                    result['obsidian_saved'] = False
                    result['obsidian_error'] = 'ファイルIDが取得できませんでした'
                    result['google_drive_file_id'] = None
                    logger.error('Google Drive（Obsidian Vault）保存エラー: ファイルIDが取得できませんでした')
                    
                    # 進捗更新: Google Drive保存エラー
                    emit_progress_update(session_id, 'google_drive_upload_error', 'Google Drive（Obsidian Vault）保存エラー: ファイルIDが取得できませんでした', 89)
            except Exception as e:
                logger.error(f'Google Drive（Obsidian Vault）保存エラー: {str(e)}')
                result['obsidian_saved'] = False
                result['obsidian_error'] = str(e)
                result['google_drive_file_id'] = None
                
                # 進捗更新: Google Drive保存エラー
                emit_progress_update(session_id, 'google_drive_upload_error', f'Google Drive（Obsidian Vault）保存エラー: {str(e)}', 89)
        else:
            result['obsidian_saved'] = False
            result['google_drive_file_id'] = None
            result['obsidian_error'] = None
            # Google Drive保存がスキップされた場合でも進捗を更新（88%）
            emit_progress_update(session_id, 'google_drive_skip', 'Google Drive（Obsidian Vault）保存: スキップ', 88)
        
        # メール送信を非同期で実行
        if email and email.strip():
            try:
                # 進捗更新: メール送信キューに追加
                emit_progress_update(session_id, 'email_queue', 'メール送信をキューに追加しています...', 95)
                
                # メール送信データをキューに追加
                email_data = {
                    'to_email': email,
                    'meeting_data': result,
                    'transcript_file_path': transcript_filepath,
                    'meeting_file_path': md_filepath,
                    'original_filepath': filepath,  # 元のアップロードファイルパスを追加
                    'session_id': session_id  # WebSocket用のセッションIDを追加
                }
                email_queue.put(email_data)
                
                result['email_sent'] = True  # キューに追加された時点で成功
                result['email_address'] = email
                result['email_status'] = 'queued'
                logger.info(f'メール送信をキューに追加: {email}')
                
                # 進捗更新: メール送信キュー追加完了
                emit_progress_update(session_id, 'email_queue_complete', 'メール送信をキューに追加完了', 95)
            except Exception as e:
                logger.error(f'メール送信キュー追加エラー: {str(e)}')
                result['email_sent'] = False
                result['email_error'] = str(e)
                result['email_status'] = 'error'
                
                # 進捗更新: メール送信エラー
                emit_progress_update(session_id, 'email_queue_error', f'メール送信エラー: {str(e)}', 95)
        else:
            result['email_sent'] = False
            result['email_address'] = None
            result['email_status'] = 'not_set'
            
            # メール送信が設定されていない場合は、ここで元のアップロードファイルを削除
            try:
                os.remove(filepath)
                logger.info(f'メール未設定時のファイル削除完了: {filepath}')
            except OSError as e:
                logger.warning(f'メール未設定時のファイル削除失敗: {str(e)}')
        
        # 進捗更新: 処理完了
        emit_progress_update(session_id, 'complete', '処理完了', 100, {'filename': filename})
        
        logger.info(f'処理完了: {filename}')
        
        # ロックファイルを削除（処理完了）
        _remove_upload_lock(filename)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'エラーが発生しました: {str(e)}', exc_info=True)
        # エラー時もロックファイルを削除
        if 'filename' in locals():
            _remove_upload_lock(filename)
        return jsonify({'error': str(e)}), 500


@app.route('/api/email-status')
def get_email_status():
    """メール送信状況を取得"""
    return jsonify({
        'email_sent': email_status_tracker.get('last_email_status', None),
        'email_error': email_status_tracker.get('last_email_error', ''),
        'queue_size': email_queue.qsize()
    })


@app.route('/transcripts/<filename>')
def get_transcript(filename):
    """議事録ファイルの取得"""
    try:
        return send_from_directory(TRANSCRIPT_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({'error': 'ファイルが見つかりません'}), 404


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f'Starting Flask application with WebSocket on {host}:{port} (debug={debug})')
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)