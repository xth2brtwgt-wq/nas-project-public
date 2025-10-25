#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube音声抽出ユーティリティ
yt-dlpを使用してYouTube動画から音声を抽出
"""

import os
import logging
import yt_dlp
from datetime import datetime

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self):
        self.audio_quality = int(os.getenv('AUDIO_QUALITY', '128'))
        self.max_duration = int(os.getenv('MAX_VIDEO_DURATION', '7200'))  # 2時間
        
    def download_audio(self, video_url, output_dir):
        """YouTube動画から音声を抽出"""
        try:
            # 出力ファイル名を生成
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"youtube_audio_{timestamp}.mp3"
            output_path = os.path.join(output_dir, output_filename)
            
            # yt-dlp設定（403エラー対策）
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path.replace('.mp3', '.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': str(self.audio_quality),
                }],
                'extractaudio': True,
                'audioformat': 'mp3',
                'noplaylist': True,
                'max_duration': self.max_duration,
                'quiet': True,
                'no_warnings': True,
                # 403エラー対策
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'cookiesfrombrowser': None,
                'extractor_retries': 3,
                'fragment_retries': 3,
                'retries': 3,
                'sleep_interval': 1,
                'max_sleep_interval': 5,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 動画情報を取得（ダウンロード前）
                info = ydl.extract_info(video_url, download=False)
                
                # 動画時間チェック
                duration = info.get('duration', 0)
                if duration > self.max_duration:
                    raise Exception(f"動画が長すぎます（{duration}秒 > {self.max_duration}秒）")
                
                # 音声ダウンロード
                ydl.download([video_url])
                
                # 実際の出力ファイル名を確認
                if os.path.exists(output_path):
                    return output_path
                else:
                    # 拡張子なしのファイルを探す
                    base_path = output_path.replace('.mp3', '')
                    for ext in ['.mp3', '.m4a', '.webm']:
                        test_path = base_path + ext
                        if os.path.exists(test_path):
                            return test_path
                    
                    raise Exception("音声ファイルの生成に失敗しました")
            
        except Exception as e:
            logger.error(f"YouTube音声抽出エラー: {str(e)}")
            raise Exception(f"音声抽出に失敗しました: {str(e)}")
    
    def get_video_info(self, video_url):
        """動画情報を取得（ダウンロードなし）"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                # 403エラー対策
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'extractor_retries': 3,
                'retries': 3,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                return {
                    'title': info.get('title', ''),
                    'channel': info.get('uploader', ''),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'url': video_url
                }
                
        except Exception as e:
            logger.error(f"動画情報取得エラー: {str(e)}")
            raise Exception(f"動画情報の取得に失敗しました: {str(e)}")
    
    def get_comments(self, video_url, max_comments=50):
        """YouTube動画のコメントを取得"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'writecomments': True,  # コメント取得を有効化
                'getcomments': True,    # コメント取得を明示的に有効化
                'extract_flat': False,  # フラット抽出を無効化
                # 403エラー対策
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'extractor_retries': 3,
                'retries': 3,
                'sleep_interval': 1,
                'max_sleep_interval': 5,
            }
            
            comments = []
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                logger.info(f"動画情報取得完了: {info.get('title', 'Unknown')}")
                logger.info(f"利用可能なキー: {list(info.keys())}")
                
                # コメント情報を取得
                if 'comments' in info and info['comments']:
                    logger.info(f"コメント情報が見つかりました: {len(info['comments'])}件")
                    for comment in info['comments'][:max_comments]:
                        comment_data = {
                            'text': comment.get('text', ''),
                            'author': comment.get('author', ''),
                            'like_count': comment.get('like_count', 0),
                            'timestamp': comment.get('timestamp', None)
                        }
                        comments.append(comment_data)
                else:
                    logger.warning("コメント情報が見つかりませんでした")
                    # 代替方法: コメントセクションを探す
                    if 'comment_count' in info:
                        logger.info(f"コメント数: {info['comment_count']}")
                    if 'comments' in info:
                        logger.info(f"コメントキーは存在しますが、値: {info['comments']}")
                
                logger.info(f"コメント取得完了: {len(comments)}件")
                return comments
                
        except Exception as e:
            logger.warning(f"コメント取得エラー: {str(e)}")
            # コメント取得に失敗しても処理を続行
            return []
    
    def validate_url(self, url):
        """YouTube URLの検証"""
        valid_domains = [
            'youtube.com',
            'youtu.be',
            'm.youtube.com',
            'www.youtube.com'
        ]
        
        if not url:
            return False, "URLが空です"
        
        # 基本的なURL形式チェック
        if not url.startswith(('http://', 'https://')):
            return False, "URLはhttp://またはhttps://で始まる必要があります"
        
        # YouTubeドメインチェック
        for domain in valid_domains:
            if domain in url:
                return True, "有効なYouTube URLです"
        
        return False, "YouTube URLではありません"
