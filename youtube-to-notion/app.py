#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube to Notion Summarizer - Flask Application
YouTube動画の要約・Notion自動投稿アプリケーション
"""

import os
import json
import logging
import threading
import uuid
from queue import Queue
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from dotenv import load_dotenv
import google.generativeai as genai

# カスタムユーティリティのインポート
from utils.youtube_downloader import YouTubeDownloader
from utils.notion_client import NotionClient
from utils.markdown_generator import MarkdownGenerator
from utils.video_info_service import VideoInfoService
from utils.summarization_service import SummarizationService

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
UPLOAD_FOLDER = os.getenv('UPLOAD_DIR', './data/uploads')
OUTPUT_FOLDER = os.getenv('OUTPUT_DIR', './data/outputs')
CACHE_FOLDER = os.getenv('CACHE_DIR', './data/cache')
LOG_FOLDER = os.getenv('LOG_DIR', './logs')
MAX_VIDEO_DURATION = int(os.getenv('MAX_VIDEO_DURATION', '7200'))  # 2時間
AUDIO_QUALITY = int(os.getenv('AUDIO_QUALITY', '128'))

# ディレクトリの作成
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, CACHE_FOLDER, LOG_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# サービス初期化
youtube_downloader = YouTubeDownloader()
video_info_service = VideoInfoService()
notion_client = NotionClient()
markdown_generator = MarkdownGenerator()
summarization_service = SummarizationService()

# セッション管理
active_sessions = {}

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html', 
                         app_name=APP_NAME, 
                         app_version=APP_VERSION)

@app.route('/health')
def health():
    """ヘルスチェック"""
    return jsonify({
        "status": "ok",
        "version": APP_VERSION,
        "uptime": "running"
    })

@app.route('/api/youtube/process', methods=['POST'])
def process_youtube():
    """YouTube動画処理開始"""
    try:
        data = request.get_json()
        youtube_url = data.get('youtube_url')
        save_to_notion = data.get('save_to_notion', True)
        summary_length = data.get('summary_length', 'medium')
        include_timestamps = data.get('include_timestamps', False)
        
        if not youtube_url:
            return jsonify({"success": False, "error": "YouTube URLが必要です"}), 400
        
        # セッションID生成
        session_id = str(uuid.uuid4())
        
        # セッション情報を保存
        active_sessions[session_id] = {
            'status': 'pending',
            'progress': 0,
            'current_step': 'initializing',
            'youtube_url': youtube_url,
            'save_to_notion': save_to_notion,
            'summary_length': summary_length,
            'include_timestamps': include_timestamps,
            'created_at': datetime.now()
        }
        
        # 非同期処理開始
        thread = threading.Thread(
            target=process_youtube_async,
            args=(session_id, youtube_url, save_to_notion, summary_length, include_timestamps)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "処理を開始しました"
        })
        
    except Exception as e:
        logger.error(f"YouTube処理開始エラー: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/youtube/status/<session_id>')
def get_status(session_id):
    """処理状態取得"""
    if session_id not in active_sessions:
        return jsonify({"error": "セッションが見つかりません"}), 404
    
    session = active_sessions[session_id]
    return jsonify({
        "session_id": session_id,
        "status": session['status'],
        "progress": session['progress'],
        "current_step": session['current_step'],
        "message": session.get('message', '')
    })

@app.route('/api/youtube/result/<session_id>')
def get_result(session_id):
    """処理結果取得"""
    if session_id not in active_sessions:
        return jsonify({"error": "セッションが見つかりません"}), 404
    
    session = active_sessions[session_id]
    if session['status'] != 'completed':
        return jsonify({"error": "処理が完了していません"}), 400
    
    return jsonify(session.get('result', {}))

@app.route('/api/youtube/download/<session_id>')
def download_markdown(session_id):
    """マークダウンファイルダウンロード"""
    if session_id not in active_sessions:
        return jsonify({"error": "セッションが見つかりません"}), 404
    
    session = active_sessions[session_id]
    if session['status'] != 'completed':
        return jsonify({"error": "処理が完了していません"}), 400
    
    try:
        result = session.get('result', {})
        video_info = session.get('video_info', {})
        
        # マークダウン生成
        markdown_content = markdown_generator.generate_youtube_markdown(
            video_info=video_info,
            summary=result.get('summary', ''),
            transcript=result.get('transcript', ''),
            keywords=result.get('keywords', []),
            category=result.get('category', ''),
            include_timestamps=result.get('include_timestamps', False)
        )
        
        # ファイル名生成（安全なASCII文字のみ）
        title = video_info.get('title', 'YouTube動画要約')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title[:50]  # ファイル名長さ制限
        filename = f"youtube_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # レスポンス作成
        from flask import Response
        import urllib.parse
        
        # ファイル名をURLエンコード
        encoded_filename = urllib.parse.quote(filename.encode('utf-8'))
        
        return Response(
            markdown_content.encode('utf-8'),
            mimetype='text/markdown',
            headers={
                'Content-Disposition': f'attachment; filename*=UTF-8\'\'{encoded_filename}',
                'Content-Type': 'text/markdown; charset=utf-8'
            }
        )
        
    except Exception as e:
        logger.error(f"マークダウンダウンロードエラー: {str(e)}")
        return jsonify({"error": f"ダウンロードに失敗しました: {str(e)}"}), 500

def process_youtube_async(session_id, youtube_url, save_to_notion, summary_length, include_timestamps):
    """YouTube動画の非同期処理"""
    try:
        session = active_sessions[session_id]
        
        # 1. 動画情報取得
        update_progress(session_id, 5, 'video_info', '動画情報取得中...')
        video_info = video_info_service.get_video_info(youtube_url)
        session['video_info'] = video_info
        
        # 2. コメント取得
        update_progress(session_id, 10, 'comments', 'コメント取得中...')
        comments = youtube_downloader.get_comments(youtube_url, max_comments=200)
        session['comments'] = comments
        
        # 3. 音声ダウンロード
        update_progress(session_id, 20, 'downloading', '音声ダウンロード中...')
        audio_path = youtube_downloader.download_audio(youtube_url, UPLOAD_FOLDER)
        session['audio_path'] = audio_path
        
        # 4. 文字起こし
        update_progress(session_id, 50, 'transcription', '文字起こし中...')
        transcript = summarization_service.transcribe_audio(audio_path)
        session['transcript'] = transcript
        
        # 5. 要約生成
        update_progress(session_id, 70, 'summarizing', '要約生成中...')
        summary = summarization_service.generate_summary(
            transcript, video_info, comments, summary_length
        )
        session['summary'] = summary
        
        # 6. コメント分析
        update_progress(session_id, 75, 'comment_analysis', 'コメント分析中...')
        comment_analysis = summarization_service.analyze_comments(comments)
        session['comment_analysis'] = comment_analysis
        
        # 7. Notion保存
        if save_to_notion:
            update_progress(session_id, 90, 'notion_save', 'Notion保存中...')
            notion_url = notion_client.create_youtube_page(
                video_info, summary, transcript, comment_analysis
            )
            session['notion_url'] = notion_url
        
        # 8. ファイル保存
        update_progress(session_id, 95, 'saving', 'ファイル保存中...')
        markdown_path = markdown_generator.save_youtube_summary(
            video_info, summary, transcript, OUTPUT_FOLDER
        )
        session['markdown_path'] = markdown_path
        
        # 7. 完了
        update_progress(session_id, 100, 'completed', '処理完了')
        session['status'] = 'completed'
        session['result'] = {
            'video_info': video_info,
            'summary': summary,
            'transcript': transcript,
            'comments': comments,
            'comment_analysis': comment_analysis,
            'notion_url': session.get('notion_url'),
            'markdown_path': markdown_path
        }
        
        # 完了イベントを送信
        socketio.emit('process_complete', {
            'session_id': session_id,
            'result': session['result']
        }, room=session_id)
        
        # 音声ファイルの定期クリーンアップ（1週間経過後削除）
        try:
            from utils.file_cleanup import cleanup_youtube_audio_files
            cleanup_result = cleanup_youtube_audio_files(
                upload_dir=UPLOAD_FOLDER,
                max_age_hours=168,  # 1週間（168時間）後に削除
                max_files=50,       # 最大50ファイルまで保持
                dry_run=False
            )
            logger.info(f"音声ファイルクリーンアップ完了: {cleanup_result}")
        except Exception as e:
            logger.warning(f"音声ファイルクリーンアップエラー: {str(e)}")
            # フォールバック: 現在のファイルは保持（1週間後に削除される）
            
    except Exception as e:
        logger.error(f"YouTube処理エラー: {str(e)}")
        session['status'] = 'failed'
        session['error'] = str(e)
        update_progress(session_id, 0, 'error', f'エラー: {str(e)}')
        
        # エラーイベントを送信
        socketio.emit('error', {
            'session_id': session_id,
            'error': str(e)
        }, room=session_id)

def update_progress(session_id, progress, step, message):
    """進捗更新"""
    if session_id in active_sessions:
        active_sessions[session_id]['progress'] = progress
        active_sessions[session_id]['current_step'] = step
        active_sessions[session_id]['message'] = message
        
        # WebSocketで進捗を送信
        socketio.emit('progress_update', {
            'session_id': session_id,
            'progress': progress,
            'step': step,
            'message': message
        }, room=session_id)

@socketio.on('join_room')
def on_join_room(data):
    """WebSocketルーム参加"""
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        emit('joined', {'session_id': session_id})

if __name__ == '__main__':
    # Gemini API設定
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    
    # アプリケーション起動
    port = int(os.getenv('PORT', 8110))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
