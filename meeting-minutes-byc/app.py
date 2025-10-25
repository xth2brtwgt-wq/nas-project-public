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
from queue import Queue
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import google.generativeai as genai

# カスタムユーティリティのインポート
from utils.email_sender import EmailSender
from utils.notion_client import NotionClient
from utils.markdown_generator import MarkdownGenerator
from utils.dictionary_manager import DictionaryManager
from utils.template_manager import TemplateManager

# 環境変数の読み込み
load_dotenv()

# アプリケーション情報
from config.version import APP_NAME, APP_VERSION

# Flask アプリケーションの初期化
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False, allow_unsafe_werkzeug=True)

# ログ設定
log_dir = os.getenv('LOG_DIR', './logs')
os.makedirs(log_dir, exist_ok=True)

# ファイルハンドラーを追加
log_file = os.path.join(log_dir, 'app.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        logging.StreamHandler()  # 標準出力も維持
    ]
)
logger = logging.getLogger(__name__)

# 設定
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
UPLOAD_FOLDER = os.getenv('UPLOAD_DIR', './uploads')
TRANSCRIPT_FOLDER = os.getenv('TRANSCRIPT_DIR', './transcripts')
DEFAULT_EMAIL = os.getenv('EMAIL_TO', 'nas.system.0828@gmail.com')
TEMPLATES_FOLDER = os.getenv('TEMPLATES_DIR', './templates')
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg', 'webm'}

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

def send_email_async(email_data):
    """バックグラウンドでメール送信"""
    session_id = email_data.get('session_id', 'default')
    original_filepath = email_data.get('original_filepath')  # 元のアップロードファイルパス
    
    try:
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

# バックグラウンドスレッドを開始
email_thread = threading.Thread(target=process_email_queue, daemon=True)
email_thread.start()
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
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    return f"{name}_{timestamp}{ext}"


def transcribe_audio_with_gemini(file_path):
    """Gemini AI を使用して音声を文字起こし"""
    try:
        if not model:
            raise Exception("Gemini AI model not configured")
        
        # 音声ファイルを読み込み
        with open(file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
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
        
        # Gemini AI に送信するためのプロンプト
        prompt = f"""
        以下の音声ファイルの内容を正確に文字起こししてください。
        日本語の会議内容を想定し、話者の区別も含めて詳細に文字起こししてください。
        
        {dictionary_info}
        
        出力形式：
        [時刻] 話者名: 発言内容
        
        例：
        [00:01:23] 田中: 今日の会議の議題について説明します
        [00:02:15] 佐藤: ありがとうございます。質問があります
        
        注意事項：
        - 上記のカスタム辞書に記載されている用語は、必ず指定された正しい表記で文字起こししてください
        - 技術用語や固有名詞は特に注意深く聞き取り、正確に文字起こししてください
        - 不明な用語がある場合は、音声に最も近い表記を推測して記載してください
        """
        
        # Gemini AI に送信
        response = model.generate_content([
            prompt,
            {
                "mime_type": mime_type,
                "data": audio_data
            }
        ])
        
        return response.text
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise Exception(f"文字起こしに失敗しました: {str(e)}")


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
def index():
    """メインページ"""
    return render_template('index.html', 
                         app_name=APP_NAME, 
                         app_version=APP_VERSION,
                         default_email=DEFAULT_EMAIL)


@app.route('/history')
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
        template_id = request.form.get('template_id', '')
        
        # ファイルの保存
        filename = generate_unique_filename(secure_filename(file.filename))
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # ファイルサイズを取得（削除前に取得）
        file_size = os.path.getsize(filepath)
        
        logger.info(f'ファイルをアップロードしました: {filename}')
        
        # 進捗更新: ファイルアップロード完了
        emit_progress_update(session_id, 'file_upload', 'ファイルアップロード完了', 10, {'filename': filename})
        
        # 進捗更新: 文字起こし開始
        emit_progress_update(session_id, 'transcription', '音声文字起こしを開始しています...', 20)
        
        # 文字起こし
        transcript = transcribe_audio_with_gemini(filepath)
        
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
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'エラーが発生しました: {str(e)}', exc_info=True)
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